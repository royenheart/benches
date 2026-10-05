"""ACP (Zed Agent Client Protocol) stdio demo, standard library only.

ACP is the *editor <-> coding agent* protocol (NOT agent<->agent): a JSON-RPC 2.0 conversation over stdio, where the client spawns the agent as a subprocess. Every message is one JSON object per line; stderr is reserved for logs.

This demo is self-contained: the default mode plays a scripted "editor client" that spawns ``python acp_stdio_demo.py --agent`` as a subprocess and walks through the protocol lifecycle:

  1. initialize          — capability handshake (protocolVersion, fs/terminal)
  2. session/new         — agent gets a cwd + mcpServers, returns sessionId
  3. session/prompt      — user prompt; while it runs, the agent streams session/update notifications (agent_message_chunk, tool_call / tool_call_update) and can issue *client-side* requests (fs/read_text_file) that the editor must answer — bidirectional JSON-RPC on one pipe
  4. response            — final result with stopReason

Shapes follow the ACP schema (agentclientprotocol.com), simplified where noted.

Usage:
    python acp_stdio_demo.py            # scripted editor client drives --agent child
    python acp_stdio_demo.py --agent    # run the agent side (spawned automatically)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def send_line(stream, obj: dict):
    stream.write(json.dumps(obj) + "\n")
    stream.flush()


def read_line(stream) -> dict:
    line = stream.readline()
    if not line:
        raise EOFError("peer closed the pipe")
    return json.loads(line)


# --- Agent side ---------------------------------------------------------------


def agent_loop() -> None:
    """The 'coding agent': a stateful JSON-RPC peer reading stdin/writing stdout."""
    stdin, stdout = sys.stdin, sys.stdout
    while True:
        msg = read_line(stdin)
        method, params = msg.get("method"), msg.get("params", {})

        if method == "initialize":
            send_line(
                stdout,
                {
                    "jsonrpc": "2.0",
                    "id": msg["id"],
                    "result": {
                        "protocolVersion": 1,
                        "agentCapabilities": {
                            "loadSession": False,
                            "promptCapabilities": {"image": False, "audio": False, "embeddedContext": False},
                            "mcpCapabilities": {"http": False, "sse": False},
                        },
                        "agentInfo": {"name": "tutorial-agent", "version": "1.0.0"},
                        "authMethods": [],
                    },
                },
            )
        elif method == "session/new":
            send_line(stdout, {"jsonrpc": "2.0", "id": msg["id"], "result": {"sessionId": "sess-demo-1"}})
        elif method == "session/prompt":
            sid = params["sessionId"]

            def notify(update: dict):
                send_line(stdout, {"jsonrpc": "2.0", "method": "session/update", "params": {"sessionId": sid, "update": update}})

            # agent thinks out loud, then decides it needs to read a file.
            notify({"sessionUpdate": "agent_message_chunk", "content": {"type": "text", "text": "I'll inspect the project files first."}})
            notify(
                {
                    "sessionUpdate": "tool_call",
                    "toolCallId": "call-1",
                    "title": "Read README.md",
                    "kind": "read",
                    "status": "in_progress",
                    "content": [],
                }
            )
            # Client-side request: the EDITOR owns the filesystem, so the agent
            # must ask. This is the defining inversion of ACP vs A2A.
            send_line(stdout, {"jsonrpc": "2.0", "id": 100, "method": "fs/read_text_file", "params": {"path": "/workspace/README.md", "sessionId": sid}})
            file_content = read_line(stdin)["result"]  # ACP returns the content string
            notify(
                {
                    "sessionUpdate": "tool_call_update",
                    "toolCallId": "call-1",
                    "status": "completed",
                    "content": [{"type": "text", "text": file_content[:60] + "..."}],
                }
            )
            notify({"sessionUpdate": "agent_message_chunk", "content": {"type": "text", "text": "Project summary: tutorial workspace, 3 files."}})
            send_line(stdout, {"jsonrpc": "2.0", "id": msg["id"], "result": {"stopReason": "end_turn"}})
        elif method == "session/cancel":
            send_line(stdout, {"jsonrpc": "2.0", "id": msg["id"], "result": {}})
        else:
            send_line(stdout, {"jsonrpc": "2.0", "id": msg.get("id"), "error": {"code": -32601, "message": method}})


# --- Editor client side ---------------------------------------------------------


class EditorClient:
    """Scripted editor: answers client-side requests, prints the transcript."""

    def __init__(self, verbose: bool):
        self.verbose = verbose
        self.proc = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--agent"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=None,
            text=True,
        )
        self._prompt_req_id: int | None = None

    def request(self, method: str, params: dict, want_response: bool = True) -> dict | None:
        EditorClient._next = getattr(EditorClient, "_next", 0) + 1
        req_id = EditorClient._next
        if method == "session/prompt":
            self._prompt_req_id = req_id
        send_line(self.proc.stdin, {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params})
        if not want_response:
            return None
        # Route incoming traffic until the response to OUR request arrives:
        # notifications (no id) -> print; requests (method+id) -> serve.
        while True:
            msg = read_line(self.proc.stdout)
            if self.verbose:
                print(f"  << {json.dumps(msg, ensure_ascii=False)}")
            if "method" in msg and "id" in msg:  # agent -> client request
                self._serve(msg)
            elif msg.get("id") == req_id:
                return msg
            # else: notification, already printed

    def _serve(self, msg: dict):
        if msg["method"] == "fs/read_text_file":
            fake = "# Tutorial Workspace\n\nA tiny project with 3 files."
            send_line(self.proc.stdin, {"jsonrpc": "2.0", "id": msg["id"], "result": fake})
        else:
            send_line(self.proc.stdin, {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32601, "message": msg["method"]}})

    def close(self):
        self.proc.terminate()
        self.proc.wait(timeout=5)


def run_client(verbose: bool):
    print("# spawning agent subprocess: python acp_stdio_demo.py --agent\n")
    client = EditorClient(verbose)

    print("== 1. initialize (capability handshake) ==")
    resp = client.request(
        "initialize",
        {
            "protocolVersion": 1,
            "clientCapabilities": {"fs": {"readTextFile": True, "writeTextFile": True}, "terminal": False},
            "clientInfo": {"name": "tutorial-editor", "version": "0.1.0"},
        },
    )
    print(f"  agent: {resp['result']['agentInfo']}  negotiatedVersion={resp['result']['protocolVersion']}")

    print("\n== 2. session/new (editor grants cwd + mcpServers) ==")
    resp = client.request("session/new", {"cwd": "/workspace", "mcpServers": []})
    sid = resp["result"]["sessionId"]
    print(f"  sessionId={sid}")

    print("\n== 3. session/prompt (agent streams; editor answers fs/read_text_file) ==")
    resp = client.request("session/prompt", {"sessionId": sid, "prompt": [{"type": "text", "text": "Summarize this project"}]})
    print(f"\n  prompt response: stopReason={resp['result']['stopReason']}")
    client.close()
    print("\n# agent subprocess exited")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--agent", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--verbose", action="store_true", help="print every JSON line on the wire")
    args = parser.parse_args()
    if args.agent:
        agent_loop()
    else:
        run_client(args.verbose)


if __name__ == "__main__":
    main()
