import importlib.util
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("discovery", Path(__file__).resolve().parents[1] / "mcp/acceptance/discovery.py")
discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discovery)


class DiscoveryTest(unittest.TestCase):
    def test_json_and_sse_results_decode(self):
        expected = {"jsonrpc": "2.0", "id": 1, "result": {"tools": []}}
        self.assertEqual(expected, discovery.decode('{"jsonrpc":"2.0","id":1,"result":{"tools":[]}}'))
        self.assertEqual(expected, discovery.decode('event: message\r\ndata: {"jsonrpc":"2.0","id":1,"result":{"tools":[]}}\r\n\r\n'))

    def test_credentials_only_go_to_local_endpoints(self):
        with self.assertRaises(ValueError):
            discovery.Client("https://example.org/mcp", "token")
        with self.assertRaises(ValueError):
            discovery.Client("http://127.0.0.1:23871/mcp", "")

    def test_missing_rpc_result_is_rejected(self):
        with self.assertRaises(ValueError):
            discovery.decode("event: ping\ndata: {}\n\n")

    def test_http_lifecycle_discovers_operations_and_closes_session(self):
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                message = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                requests.append((message, dict(self.headers)))
                method = message["method"]
                if method == "notifications/initialized":
                    self.send_response(202)
                    self.end_headers()
                    return
                if method == "initialize":
                    result = {"protocolVersion": "2025-03-26"}
                elif method == "tools/list":
                    result = {"tools": [{"name": name} for name in ["workspace_list_operations", "workspace_get_operation", "workspace_inspect"]]}
                elif method == "tools/call":
                    result = {"structuredContent": {"data": {"items": [{"id": "workspace_inspect"}], "total": 1}}}
                else:
                    self.send_error(400)
                    return
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Mcp-Session-Id", "acceptance-session")
                self.end_headers()
                self.wfile.write(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": result}).encode())

            def do_DELETE(self):
                requests.append(({"method": "DELETE"}, dict(self.headers)))
                self.send_response(200)
                self.end_headers()

        with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                with patch.dict(os.environ, {"PSD2LIVE_MCP_ENDPOINT": f"http://127.0.0.1:{server.server_port}/mcp",
                                             "PSD2LIVE_MCP_TOKEN": "test-token"}):
                    discovery.main()
            finally:
                server.shutdown()
                worker.join()
        self.assertEqual(["initialize", "notifications/initialized", "tools/list", "tools/call", "DELETE"],
                         [message["method"] for message, _ in requests])
        self.assertTrue(all(headers["Authorization"] == "Bearer test-token" for _, headers in requests))
        self.assertTrue(all(headers.get("Mcp-Session-Id") == "acceptance-session" for _, headers in requests[1:]))
        self.assertEqual({"name": "workspace_list_operations", "arguments": {"limit": 1}}, requests[3][0]["params"])


if __name__ == "__main__":
    unittest.main()
