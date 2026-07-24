"""MCP client demo: connects to toy server via subprocess stdio."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))


@dataclass
class MCPClient:
    proc: subprocess.Popen

    def request(self, method: str, params: dict | None = None) -> dict:
        msg = {"jsonrpc": "2.0", "id": 1, "method": method}
        if params:
            msg["params"] = params
        payload = json.dumps(msg) + "\n"
        self.proc.stdin.write(payload)
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        return json.loads(line)

    def close(self):
        self.proc.stdin.close()
        self.proc.terminate()
        self.proc.wait()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Toy MCP client over subprocess stdio.")
    p.add_argument("--server-cmd", default=f"{sys.executable} {_HERE / 'mcp_server_demo.py'}")
    p.add_argument("--tool", default="calculator")
    p.add_argument("--args", default='{"expr": "2+3*4"}', help="JSON tool arguments")
    p.add_argument("--use-api", action="store_true", help="Use DeepSeek API instead of toy logic")
    p.add_argument("--model", default="deepseek-v4-flash")
    p.add_argument(
        "--query", default="", help="Natural-language goal; with --use-api the LLM picks tool+args"
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    client_llm = None
    if args.use_api:
        from scripts.llm_client import get_client

        client_llm = get_client()
        if client_llm is None:
            print("⚠️  API mode requested but no client available.", file=sys.stderr)
            print(
                "   Copy agents/.env.example to agents/.env and set DEEPSEEK_API_KEY",
                file=sys.stderr,
            )
            print("   Falling back to toy mode.\n", file=sys.stderr)
    cmd = args.server_cmd.split()

    print("Starting MCP server...")
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    client = MCPClient(proc)

    # Initialize
    resp = client.request("initialize", {"protocolVersion": "2024-11-05"})
    print(
        f"Initialize: server={resp['result']['serverInfo']['name']} v{resp['result']['serverInfo']['version']}"
    )

    # List tools
    resp = client.request("tools/list")
    tools = resp["result"]["tools"]
    print(f"Tools available: {[t['name'] for t in tools]}")

    # Choose tool + args: fixed flags (default) or real LLM decision (--use-api --query)
    tool_name, tool_args = args.tool, json.loads(args.args)
    if args.use_api and client_llm is not None and args.query:
        from scripts.llm_client import chat_json

        catalog = json.dumps(
            [
                {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "schema": t.get("inputSchema", {}),
                }
                for t in tools
            ],
            ensure_ascii=False,
        )
        pick = chat_json(
            client_llm,
            f"Available MCP tools:\n{catalog}\n\nUser goal: {args.query}\n"
            'Pick the best tool and arguments. Return JSON: {"tool": "<name>", "args": {...}}',
            model=args.model,
            system="You map user goals to MCP tool calls. JSON only.",
        )
        if pick.get("tool"):
            tool_name, tool_args = pick["tool"], pick.get("args", {})
            print(f"LLM selected: {tool_name}({json.dumps(tool_args, ensure_ascii=False)})")

    resp = client.request("tools/call", {"name": tool_name, "arguments": tool_args})
    if "error" in resp:
        print(f"Error: {resp['error']['message']}")
    else:
        content = resp["result"]["content"]
        for item in content:
            print(f"Result: {item['text']}")

    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
