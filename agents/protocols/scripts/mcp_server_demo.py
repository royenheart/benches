"""MCP server demo: minimal JSON-RPC 2.0 server over stdio."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass


@dataclass
class Tool:
    name: str
    description: str
    inputSchema: dict

    def call(self, arguments: dict) -> list[dict]:
        raise NotImplementedError


class CalculatorTool(Tool):
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Evaluate a mathematical expression",
            inputSchema={
                "type": "object",
                "properties": {"expr": {"type": "string"}},
                "required": ["expr"],
            },
        )

    def call(self, arguments: dict) -> list[dict]:
        expr = arguments["expr"]
        allowed = set("0123456789+-*/().% ")
        if not all(c in allowed for c in expr):
            return [{"type": "text", "text": f"Error: disallowed characters in '{expr}'"}]
        try:
            result = eval(expr, {"__builtins__": {}}, {})
            return [{"type": "text", "text": str(result)}]
        except Exception as e:
            return [{"type": "text", "text": f"Error: {e}"}]


class WeatherTool(Tool):
    def __init__(self):
        super().__init__(
            name="weather",
            description="Get weather for a city",
            inputSchema={
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        )

    def call(self, arguments: dict) -> list[dict]:
        city = arguments["city"].lower()
        data = {
            "beijing": "Sunny, 25°C",
            "shanghai": "Cloudy, 22°C",
            "tokyo": "Rainy, 18°C",
            "london": "Overcast, 12°C",
            "default": "Unknown city",
        }
        return [{"type": "text", "text": data.get(city, data["default"])}]


def handle_request(req: dict, tools: dict[str, Tool]) -> dict:
    method = req.get("method", "")
    mid = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": mid,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "toy-mcp-server", "version": "1.0.0"},
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": mid,
            "result": {
                "tools": [
                    {"name": t.name, "description": t.description, "inputSchema": t.inputSchema}
                    for t in tools.values()
                ]
            },
        }

    if method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        tool = tools.get(tool_name)
        if not tool:
            return {
                "jsonrpc": "2.0",
                "id": mid,
                "error": {"code": -32601, "message": f"Tool not found: {tool_name}"},
            }
        content = tool.call(tool_args)
        return {"jsonrpc": "2.0", "id": mid, "result": {"content": content}}

    return {
        "jsonrpc": "2.0",
        "id": mid,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    }


def server_loop(tools: list[Tool], verbose: bool) -> None:
    tool_map = {t.name: t for t in tools}
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        if verbose:
            print(f"[server] ← {json.dumps(req)}", file=sys.stderr)
        resp = handle_request(req, tool_map)
        if verbose:
            print(f"[server] → {json.dumps(resp)}", file=sys.stderr)
        print(json.dumps(resp), flush=True)


def parse_args():
    import argparse

    p = argparse.ArgumentParser(description="Toy MCP server over stdio.")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--tools", default="calculator,weather")
    return p.parse_args()


def main():
    args = parse_args()
    available = {
        "calculator": CalculatorTool(),
        "weather": WeatherTool(),
    }
    selected = [available[name] for name in args.tools.split(",") if name in available]
    server_loop(selected, args.verbose)
    return 0


if __name__ == "__main__":
    sys.exit(main())
