"""Read-only Streamable HTTP MCP discovery acceptance for a running PSD2Live."""

import json
import os
from urllib.parse import urlparse
import urllib.request


def decode(data):
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        for block in data.replace("\r\n", "\n").split("\n\n"):
            payload = "\n".join(line[5:].lstrip() for line in block.splitlines() if line.startswith("data:"))
            if payload:
                message = json.loads(payload)
                if "result" in message or "error" in message:
                    return message
        raise ValueError("No JSON-RPC result in the MCP response")


class Client:
    def __init__(self, endpoint, token):
        parsed = urlparse(endpoint)
        if parsed.scheme not in {"http", "https"} or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("Use a local PSD2Live MCP endpoint")
        if not token:
            raise ValueError("Set PSD2LIVE_MCP_TOKEN")
        self.endpoint = endpoint
        self.token = token
        self.session = None
        self.version = "2025-03-26"
        self.sequence = 0

    def call(self, method, params=None, notification=False, delete=False):
        self.sequence += 1
        message = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        if not notification:
            message["id"] = self.sequence
        headers = {"Authorization": "Bearer " + self.token, "Accept": "application/json, text/event-stream",
                   "Content-Type": "application/json", "MCP-Protocol-Version": self.version}
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        request = urllib.request.Request(self.endpoint, data=None if delete else json.dumps(message).encode(),
                                         headers=headers, method="DELETE" if delete else "POST")
        # Refuse redirects so the session token never follows an unexpected endpoint.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, response_headers, newurl):
                return None
        with urllib.request.build_opener(NoRedirect).open(request, timeout=30) as response:
            self.session = response.headers.get("Mcp-Session-Id", self.session)
            if notification or delete:
                return None
            result = decode(response.read().decode())
        if result.get("id") != self.sequence or "error" in result:
            raise ValueError(f"MCP request failed: {method}")
        return result["result"]


def main():
    client = Client(os.environ.get("PSD2LIVE_MCP_ENDPOINT", "http://127.0.0.1:23871/mcp"),
                    os.environ.get("PSD2LIVE_MCP_TOKEN", ""))
    try:
        initialized = client.call("initialize", {"protocolVersion": client.version, "capabilities": {},
                                  "clientInfo": {"name": "psd2live-examples-discovery", "version": "1.0.0"}})
        client.version = initialized["protocolVersion"]
        client.call("notifications/initialized", notification=True)
        tools = []
        cursor = None
        seen = set()
        while True:
            page = client.call("tools/list", {"cursor": cursor} if cursor else {})
            tools.extend(page["tools"])
            cursor = page.get("nextCursor")
            if not cursor:
                break
            if cursor in seen:
                raise ValueError("Repeated discovery cursor")
            seen.add(cursor)
        names = {tool["name"] for tool in tools}
        required = {"workspace_list_operations", "workspace_get_operation", "workspace_inspect"}
        if not required.issubset(names):
            raise ValueError("Required workspace discovery tools are missing")
        result = client.call("tools/call", {"name": "workspace_list_operations", "arguments": {"limit": 1}})
        if result.get("isError") or not result.get("structuredContent"):
            raise ValueError("Operation discovery failed")
        print(f"MCP discovery passed: {len(names)} tools, protocol {client.version}")
    finally:
        if client.session:
            client.call("", delete=True)


if __name__ == "__main__":
    main()
