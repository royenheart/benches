"""A2A wire-level demo: real HTTP + JSON-RPC 2.0 + SSE, standard library only.

Teaches the actual A2A v1 transport stack instead of an in-process mock:

  1. Agent Card discovery  — GET /.well-known/agent-card.json (RFC 8615)
  2. JSON-RPC 2.0 binding  — POST /rpc, methods SendMessage / SendStreamingMessage / GetTask / CancelTask
  3. SSE streaming         — SendStreamingMessage answers ``Content-Type: text/event-stream``; each ``data:`` frame carries a JSON-RPC envelope whose ``result`` is a StreamResponse (statusUpdate / artifactUpdate / task)
  4. Error ranges          — JSON-RPC standard -32601 vs. A2A-specific -32001

The server runs in a background thread; the built-in client talks to it over real TCP sockets, so with --verbose you see the exact bytes on the wire.

Usage:
    python a2a_wire_demo.py            # server + client in one process
    python a2a_wire_demo.py --verbose  # additionally dump raw bodies / SSE frames
    python a2a_wire_demo.py --port 9999
"""

from __future__ import annotations

import argparse
import json
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import request as urlrequest

HOST = "127.0.0.1"
DEFAULT_PORT = 9911

# In-memory task store; a real server persists this (Postgres / task store).
TASKS: dict[str, dict] = {}


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _new_message(text: str, role: str) -> dict:
    return {"messageId": uuid.uuid4().hex[:8], "role": role, "parts": [{"text": text}]}


def build_agent_card(port: int) -> dict:
    """A2A v1 discovery document. Note supportedInterfaces: the card itself
    declares one URL per protocol binding (JSONRPC / GRPC / HTTP+JSON)."""
    return {
        "name": "Echo Route Planner",
        "description": "Toy A2A v1 agent that echoes your message back.",
        "version": "0.1.0",
        "supportedInterfaces": [
            {
                "url": f"http://{HOST}:{port}/rpc",
                "protocolBinding": "JSONRPC",
                "protocolVersion": "1.0",
            }
        ],
        "capabilities": {"streaming": True, "pushNotifications": False},
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "skills": [
            {
                "id": "echo",
                "name": "Echo",
                "description": "Replies with a hello plus your message.",
                "tags": ["demo"],
                "examples": ["hello"],
            }
        ],
        "securitySchemes": {},
    }


def build_task(user_text: str) -> dict:
    task = {
        "id": f"task-{uuid.uuid4().hex[:6]}",
        "contextId": f"ctx-{uuid.uuid4().hex[:6]}",
        "status": {"state": "TASK_STATE_SUBMITTED", "timestamp": _ts()},
        "artifacts": [],
        "history": [_new_message(user_text, "ROLE_USER")],
    }
    TASKS[task["id"]] = task
    return task


class A2AHandler(BaseHTTPRequestHandler):
    server_version = "ToyA2A/1.0"

    def log_message(self, *args):  # keep the wire dump readable
        pass

    # -- response helpers ------------------------------------------------
    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_sse(self, frames: list[dict]):
        """SSE framing: one JSON-RPC envelope per ``data:`` line, blank line
        between events. Stream ends (client sees EOF) when the handler returns."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        for frame in frames:
            self.wfile.write(f"data: {json.dumps(frame)}\n\n".encode())
            self.wfile.flush()
            time.sleep(0.2)  # fake "thinking" so individual frames are observable

    # -- HTTP routes ------------------------------------------------------
    def do_GET(self):
        if self.path == "/.well-known/agent-card.json":
            self._send_json(build_agent_card(self.server.server_port))
        else:
            self._send_json({"error": "not found"}, status=404)

    def do_POST(self):
        if self.path != "/rpc":
            self._send_json({"error": "not found"}, status=404)
            return
        rpc = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        method, rpc_id, params = rpc.get("method"), rpc.get("id"), rpc.get("params", {})
        handler = {
            "SendMessage": self._rpc_send_message,
            "SendStreamingMessage": self._rpc_send_streaming,
            "GetTask": self._rpc_get_task,
            "CancelTask": self._rpc_cancel_task,
        }.get(method)
        if handler is None:
            # JSON-RPC standard error range (-32600..-32603)
            self._send_json(
                {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
            )
            return
        handler(rpc_id, params)

    # -- JSON-RPC methods ---------------------------------------------------
    def _rpc_send_message(self, rpc_id, params):
        text = params["message"]["parts"][0]["text"]
        task = build_task(text)
        reply = f"Hello! You said: {text}"
        task["status"] = {"state": "TASK_STATE_COMPLETED", "timestamp": _ts()}
        task["artifacts"] = [
            {"artifactId": f"art-{uuid.uuid4().hex[:6]}", "name": "Reply", "parts": [{"text": reply}]}
        ]
        task["history"].append(_new_message(reply, "ROLE_AGENT"))
        self._send_json({"jsonrpc": "2.0", "id": rpc_id, "result": {"task": task}})

    def _rpc_send_streaming(self, rpc_id, params):
        text = params["message"]["parts"][0]["text"]
        task = build_task(text)
        tid, cid = task["id"], task["contextId"]

        def status(state: str, msg: str | None = None) -> dict:
            update = {"taskId": tid, "contextId": cid, "status": {"state": state, "timestamp": _ts()}}
            if msg:
                update["status"]["message"] = _new_message(msg, "ROLE_AGENT")
            return {"jsonrpc": "2.0", "id": rpc_id, "result": {"statusUpdate": update}}

        def artifact(chunk: str, last: bool) -> dict:
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "artifactUpdate": {
                        "taskId": tid,
                        "contextId": cid,
                        "artifact": {"artifactId": "art-1", "parts": [{"text": chunk}]},
                        "append": True,
                        "lastChunk": last,
                    }
                },
            }

        reply = f"Hello! You said: {text}"
        task["status"] = {"state": "TASK_STATE_COMPLETED"}
        self._send_sse(
            [
                status("TASK_STATE_WORKING", "Processing..."),
                artifact(reply[:10], last=False),
                artifact(reply[10:], last=True),
                status("TASK_STATE_COMPLETED"),
            ]
        )

    def _rpc_get_task(self, rpc_id, params):
        task = TASKS.get(params.get("id"))
        if not task:
            # A2A-specific application error range (-32001..-32099)
            self._send_json(
                {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {"code": -32001, "message": "TaskNotFoundError"},
                }
            )
            return
        self._send_json({"jsonrpc": "2.0", "id": rpc_id, "result": {"task": task}})

    def _rpc_cancel_task(self, rpc_id, params):
        task = TASKS.get(params.get("id"))
        if not task:
            self._send_json(
                {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {"code": -32001, "message": "TaskNotFoundError"},
                }
            )
            return
        task["status"] = {"state": "TASK_STATE_CANCELED", "timestamp": _ts()}
        self._send_json({"jsonrpc": "2.0", "id": rpc_id, "result": {"task": task}})


# --- Client side: plain urllib over real sockets ----------------------------


def _wire(label: str, raw: str, verbose: bool):
    if verbose:
        print(f"\n----- {label} -----\n{raw.strip()}\n----- end -----")


def http_json(method: str, url: str, payload: dict | None, verbose: bool, headers: dict | None = None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urlrequest.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("A2A-Version", "1.0")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    with urlrequest.urlopen(req) as resp:
        body = resp.read().decode()
        _wire(f"{method} {url} -> {resp.status}", body, verbose)
        return resp.status, dict(resp.headers), body


def run_client(port: int, verbose: bool):
    base = f"http://{HOST}:{port}"

    print("== 1. Discovery: GET /.well-known/agent-card.json ==")
    _, _, body = http_json("GET", f"{base}/.well-known/agent-card.json", None, verbose)
    card = json.loads(body)
    iface = card["supportedInterfaces"][0]
    print(f"  name={card['name']!r}  binding={iface['protocolBinding']}  url={iface['url']}")
    rpc_url = iface["url"]

    print("\n== 2. Unary: SendMessage (request -> one Task response) ==")
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "SendMessage",
        "params": {"message": {"messageId": "m-1", "role": "ROLE_USER", "parts": [{"text": "hello a2a"}]}},
    }
    _wire("POST /rpc SendMessage (request)", json.dumps(req, indent=2), verbose)
    _, _, body = http_json("POST", rpc_url, req, verbose)
    task = json.loads(body)["result"]["task"]
    print(f"  task.id={task['id']}  state={task['status']['state']}")
    print(f"  artifact: {task['artifacts'][0]['parts'][0]['text']}")

    print("\n== 3. Streaming: SendStreamingMessage (SSE frames) ==")
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "SendStreamingMessage",
        "params": {"message": {"messageId": "m-2", "role": "ROLE_USER", "parts": [{"text": "stream please"}]}},
    }
    _wire("POST /rpc SendStreamingMessage (request)", json.dumps(req, indent=2), verbose)
    data = json.dumps(req).encode()
    http_req = urlrequest.Request(rpc_url, data=data, method="POST")
    http_req.add_header("Content-Type", "application/json")
    http_req.add_header("Accept", "text/event-stream")
    streamed_tid = None
    with urlrequest.urlopen(http_req) as resp:
        print(f"  HTTP {resp.status}  Content-Type={resp.headers.get('Content-Type')}")
        event_lines: list[str] = []
        for raw_line in resp:  # read until the server closes the stream (EOF)
            line = raw_line.decode().rstrip("\n")
            if line == "":
                if event_lines:
                    frame = json.loads(event_lines[0][len("data: "):])
                    _wire("SSE frame", json.dumps(frame, indent=2), verbose)
                    result = frame["result"]
                    kind = "statusUpdate" if "statusUpdate" in result else "artifactUpdate"
                    payload = result[kind]
                    streamed_tid = payload.get("taskId", streamed_tid)
                    print(f"  frame: {kind} -> {json.dumps(payload)[:100]}")
                    event_lines = []
            elif line.startswith("data:"):
                event_lines.append(line)
        print("  (server closed the stream = end of run)")

    print("\n== 4. GetTask on the streamed task ==")
    req = {"jsonrpc": "2.0", "id": 3, "method": "GetTask", "params": {"id": streamed_tid}}
    _, _, body = http_json("POST", rpc_url, req, verbose)
    print(f"  fetched task state={json.loads(body)['result']['task']['status']['state']}")

    print("\n== 5. Errors: GetTask on unknown id, then CancelTask ==")
    req = {"jsonrpc": "2.0", "id": 4, "method": "GetTask", "params": {"id": "task-nope"}}
    _, _, body = http_json("POST", rpc_url, req, verbose)
    err = json.loads(body)["error"]
    print(f"  JSON-RPC error: code={err['code']} message={err['message']}")
    print("  # note: HTTP stays 200 — JSON-RPC errors ride inside the envelope,")
    print("  #       while -32600..-32603 are transport-level and A2A apps use -32001..-32099")
    req = {"jsonrpc": "2.0", "id": 5, "method": "CancelTask", "params": {"id": streamed_tid}}
    _, _, body = http_json("POST", rpc_url, req, verbose)
    print(f"  canceled task state={json.loads(body)['result']['task']['status']['state']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--verbose", action="store_true", help="dump raw wire bodies and SSE frames")
    args = parser.parse_args()

    server = ThreadingHTTPServer((HOST, args.port), A2AHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"# server listening on http://{HOST}:{args.port} (background thread)\n")
    try:
        run_client(args.port, args.verbose)
    finally:
        server.shutdown()
        thread.join(timeout=2)
        print("\n# server stopped")


if __name__ == "__main__":
    main()
