"""Vercel serverless MCP endpoint for intangible-valuation — 14 folded tools, prompts and resources.

The tool surface is defined once in ``mcp_server/tool_surface.py`` and shared
with the stdio server, so the hosted endpoint and the local server advertise
byte-identical tool definitions (name, title, description, JSON Schemas,
annotations). Model Context Protocol (MCP) JSON-RPC 2.0 over POST:

* ``initialize``   — handshake
* ``tools/list``   — 14 tool definitions
* ``tools/call``   — execute a tool by name
* ``prompts/list`` / ``prompts/get``       — guided valuation workflows
* ``resources/list`` / ``resources/read`` — the method catalog
"""

import json as _json
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from mcp_server import agent_guides  # noqa: E402
from mcp_server.tool_surface import (  # noqa: E402
    SERVER_NAME,
    SERVER_VERSION,
    call_tool,
    list_tools,
    tool_count,
)

PROTOCOL_VERSION = "2025-06-18"

# Origins a browser may call from. The MCP transport specification requires a server to validate
# the Origin header on every incoming connection and answer 403 when a present Origin is invalid;
# a wildcard Access-Control-Allow-Origin does not satisfy that, because it governs who may *read*
# a reply rather than who may *speak* to the server. A client that sends no Origin — every CLI and
# SDK — stays allowed.
DEFAULT_ALLOWED_ORIGINS = frozenset(
    {
        "https://intangible-valuation.ascent-partners.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    }
)


def allowed_origins() -> frozenset:
    """The browser origins permitted to call this endpoint (``MCP_ALLOWED_ORIGINS`` overrides)."""
    raw = _os.environ.get("MCP_ALLOWED_ORIGINS", "").strip()
    if not raw:
        return DEFAULT_ALLOWED_ORIGINS
    return frozenset(o.strip() for o in raw.split(",") if o.strip())


def _cors(origin=None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Accept, MCP-Protocol-Version",
        "Vary": "Origin",
    }
    if origin is not None and origin in allowed_origins():
        headers["Access-Control-Allow-Origin"] = origin
    return headers


_CORS = _cors()


def _ok(payload: dict) -> tuple:
    return 200, _CORS, _json.dumps(payload).encode()


def _rpc_result(req_id, result) -> tuple:
    return _ok({"jsonrpc": "2.0", "id": req_id, "result": result})


def _rpc_error(req_id, code: int, message: str) -> tuple:
    return _ok({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})


def handle_request(http_method: str, _path: str, body_raw: str | None) -> tuple:
    if http_method == "GET":
        return _ok(
            {
                "status": "ok",
                "server": SERVER_NAME,
                "version": SERVER_VERSION,
                "protocolVersion": PROTOCOL_VERSION,
                "transport": "streamable-http",
                "tools": tool_count(),
            }
        )

    if http_method == "OPTIONS":
        return 204, _CORS, b""

    if http_method != "POST":
        return _rpc_error(None, -32600, f"Unsupported method: {http_method}")

    try:
        body = _json.loads(body_raw) if body_raw else {}
    except _json.JSONDecodeError:
        return _rpc_error(None, -32700, "Parse error")

    if not isinstance(body, dict):
        return _rpc_error(None, -32600, "Invalid Request")

    req_id = body.get("id")
    req_method = body.get("method")

    if req_method == "initialize":
        return _rpc_result(
            req_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                "capabilities": {
                    "tools": {"listChanged": False},
                    "prompts": {"listChanged": False},
                    "resources": {"listChanged": False, "subscribe": False},
                },
                "instructions": (
                    "Intangible asset valuation calculators: 14 tools covering time value, discount rates, "
                    "cost, market and income approaches, IP, technology, customer and human-capital assets, "
                    "goodwill and purchase price allocation, impairment, royalty analysis, uncertainty "
                    "(Monte Carlo / decision trees), and transfer-pricing / litigation. Select a formula with "
                    "the `method` argument. Read the resource "
                    f"{agent_guides.CATALOG_URI} for every method's required parameters, or use a "
                    "prompt (purchase_price_allocation, value_ip_asset, impairment_test) for a guided "
                    "multi-method workflow."
                ),
            },
        )
    if req_method in ("notifications/initialized", "notifications/cancelled"):
        return 202, {"Content-Type": "application/json"}, b"{}"
    if req_method == "ping":
        return _rpc_result(req_id, {})
    if req_method == "tools/list":
        return _rpc_result(req_id, {"tools": list_tools()})
    if req_method == "tools/call":
        params = body.get("params", {})
        name = params.get("name", "")
        arguments = params.get("arguments", {}) or {}
        try:
            result = call_tool(name, arguments)
        except ValueError as exc:
            return _rpc_error(req_id, -32602, str(exc))
        except Exception as exc:  # noqa: BLE001 — surface any computation error to the client
            return _rpc_error(req_id, -32603, str(exc))
        return _rpc_result(
            req_id,
            {"content": [{"type": "text", "text": _json.dumps(result)}], "structuredContent": result},
        )

    if req_method == "prompts/list":
        return _rpc_result(req_id, {"prompts": agent_guides.list_prompts()})
    if req_method == "prompts/get":
        params = body.get("params", {})
        try:
            return _rpc_result(req_id, agent_guides.get_prompt(params.get("name", ""), params.get("arguments")))
        except ValueError as exc:
            return _rpc_error(req_id, -32602, str(exc))
    if req_method == "resources/list":
        return _rpc_result(req_id, {"resources": agent_guides.list_resources()})
    if req_method == "resources/templates/list":
        return _rpc_result(req_id, {"resourceTemplates": []})
    if req_method == "resources/read":
        try:
            return _rpc_result(req_id, agent_guides.read_resource(body.get("params", {}).get("uri", "")))
        except ValueError as exc:
            return _rpc_error(req_id, -32002, str(exc))

    return _rpc_error(req_id, -32601, f"Unknown method: {req_method}")


from http.server import BaseHTTPRequestHandler  # noqa: E402


class handler(BaseHTTPRequestHandler):  # noqa: N801
    def _respond(self, code, headers, body):
        self.send_response(code)
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _origin(self):
        """The Origin header, or None for a non-browser client."""
        return self.headers.get("Origin")

    def _refuse_origin(self):
        """403 for a present but unapproved Origin, before anything reaches the protocol layer."""
        origin = self._origin()
        if origin is None or origin in allowed_origins():
            return False
        body = _json.dumps(
            {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Origin not allowed"}}
        ).encode()
        self._respond(403, _cors(origin), body)
        return True

    def do_GET(self):  # noqa: N802
        if self._refuse_origin():
            return
        code, headers, body = handle_request("GET", self.path, None)
        self._respond(code, {**headers, **_cors(self._origin())}, body)

    def do_POST(self):  # noqa: N802
        if self._refuse_origin():
            return
        length = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(length).decode() if length else "{}"
        code, headers, body = handle_request("POST", self.path, body_raw)
        self._respond(code, {**headers, **_cors(self._origin())}, body)

    def do_OPTIONS(self):  # noqa: N802
        if self._refuse_origin():
            return
        # A preflight must echo the allowed origin; the shared _CORS has no origin, so it is
        # merged here rather than widened to a wildcard.
        code, _headers, body = handle_request("OPTIONS", self.path, None)
        self._respond(code, _cors(self._origin()), body)
