import importlib.util
from pathlib import Path
import unittest


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


if __name__ == "__main__":
    unittest.main()
