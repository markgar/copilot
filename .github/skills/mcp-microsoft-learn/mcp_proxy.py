#!/usr/bin/env python3
"""Proxy a workspace HTTP/SSE MCP server defined in the repo's .mcp.json.

Why this exists: GitHub Copilot desktop-app sessions don't load a repo-root
`.mcp.json` natively (the session CLI's cwd is ~/.copilot; see skill
`workspace-mcp` and copilot-cli issues #3126 / #3688). This script lets a
session still USE those servers by speaking MCP JSON-RPC over HTTP directly,
which approximates "loading" them.

Usage:
  mcp_proxy.py load                         # list every server + its tools
  mcp_proxy.py tools <server>               # list one server's tools (JSON)
  mcp_proxy.py call <server> <tool> [JSON]  # call a tool; JSON args default {}

Only `type: http` / `type: sse` servers can be reached. `local`/`stdio`
servers need a real process and can't be proxied over HTTP — run the terminal
`copilot` from inside the repo for those.
"""
import json
import os
import subprocess
import sys
import urllib.request

PROTOCOL_VERSION = "2024-11-05"


def repo_root() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return os.getcwd()


def load_config() -> dict:
    cfg_path = os.path.join(repo_root(), ".mcp.json")
    if not os.path.isfile(cfg_path):
        sys.exit(f"No .mcp.json found at {cfg_path}")
    with open(cfg_path) as fh:
        return json.load(fh).get("mcpServers", {})


def _parse_sse(body: bytes):
    """Return the JSON object from the last `data:` line of an SSE response."""
    result = None
    for line in body.decode("utf-8", "replace").splitlines():
        if line.startswith("data:"):
            payload = line[len("data:"):].strip()
            if payload:
                result = json.loads(payload)
    return result


def _post(url: str, body: dict, headers: dict, want_header: str = None):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json, text/event-stream")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
        hdr = resp.headers.get(want_header) if want_header else None
    return _parse_sse(raw), hdr


def _server(name: str):
    servers = load_config()
    if name not in servers:
        sys.exit(f"Server '{name}' not in .mcp.json (have: {', '.join(servers)})")
    s = servers[name]
    if s.get("type") not in ("http", "sse"):
        sys.exit(f"Server '{name}' is type '{s.get('type','stdio')}' — only http/sse can be proxied.")
    return s["url"], s.get("headers", {})


def _session(url: str, headers: dict) -> str:
    body = {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "mcp_proxy", "version": "0.1"},
        },
    }
    _, sid = _post(url, body, headers, want_header="mcp-session-id")
    return sid


def list_tools(name: str):
    url, headers = _server(name)
    sid = _session(url, headers)
    h = dict(headers, **({"mcp-session-id": sid} if sid else {}))
    obj, _ = _post(url, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}, h)
    return obj.get("result", {}).get("tools", [])


def call_tool(name: str, tool: str, args: dict):
    url, headers = _server(name)
    sid = _session(url, headers)
    h = dict(headers, **({"mcp-session-id": sid} if sid else {}))
    body = {
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": tool, "arguments": args},
    }
    obj, _ = _post(url, body, h)
    return obj


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "load"
    if cmd == "load":
        for name, s in load_config().items():
            if s.get("type") not in ("http", "sse"):
                print(f"[{name}] {s.get('type','stdio')} — cannot proxy over HTTP (use terminal copilot)")
                continue
            print(f"== {name} ({s['url']}) ==")
            for t in list_tools(name):
                desc = (t.get("description") or "").splitlines()
                print(f" - {t['name']}: {desc[0][:80] if desc else ''}")
    elif cmd == "tools":
        print(json.dumps(list_tools(argv[2]), indent=2))
    elif cmd == "call":
        name, tool = argv[2], argv[3]
        args = json.loads(argv[4]) if len(argv) > 4 else {}
        obj = call_tool(name, tool, args)
        result = obj.get("result", obj)
        # MCP tool results are usually result.content[].text
        contents = result.get("content") if isinstance(result, dict) else None
        if contents:
            for c in contents:
                if c.get("type") == "text":
                    print(c["text"])
        else:
            print(json.dumps(obj, indent=2))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
