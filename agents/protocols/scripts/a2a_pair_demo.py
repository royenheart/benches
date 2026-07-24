"""A2A pair demo: two agents collaborate over a minimal Agent2Agent protocol.

Implements the A2A core loop in-process (no HTTP): Agent Card discovery,
JSON-RPC 2.0 envelope, and the Task lifecycle (submitted -> working -> completed).

Toy mode (default): template-based agent replies.
API mode (--use-api): both agents are driven by real DeepSeek calls.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path

# --- Path setup for llm_client ---
_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))


# --- A2A primitives (mirroring the real spec's shapes) ---


@dataclass
class AgentCard:
    """A2A discovery document — the real spec serves this at /.well-known/agent.json."""

    name: str
    url: str
    description: str
    skills: list[dict]
    capabilities: dict = field(
        default_factory=lambda: {"streaming": False, "pushNotifications": False}
    )

    def to_json(self) -> str:
        return json.dumps(
            {
                "name": self.name,
                "url": self.url,
                "description": self.description,
                "skills": self.skills,
                "capabilities": self.capabilities,
            },
            indent=2,
            ensure_ascii=False,
        )


@dataclass
class Task:
    id: str
    status: str = "submitted"  # submitted -> working -> completed | failed
    messages: list[dict] = field(default_factory=list)
    artifacts: list[dict] = field(default_factory=list)


class JsonRpc:
    """Minimal JSON-RPC 2.0 envelope helpers (A2A's wire format)."""

    @staticmethod
    def request(method: str, params: dict) -> dict:
        return {"jsonrpc": "2.0", "id": uuid.uuid4().hex[:8], "method": method, "params": params}

    @staticmethod
    def response(req_id: str, result: dict) -> dict:
        return {"jsonrpc": "2.0", "id": req_id, "result": result}


# --- Agent implementations ---


class ResearcherAgent:
    card = AgentCard(
        name="researcher",
        url="a2a://local/researcher",
        description="Finds and verifies facts on a topic.",
        skills=[
            {"id": "research", "name": "Research", "description": "Gather key facts about a topic"}
        ],
    )

    def __init__(self, client=None, model: str = "deepseek-v4-flash"):
        self.client = client
        self.model = model

    def handle(self, task: Task, verbose: bool) -> Task:
        task.status = "working"
        query = task.messages[-1]["content"]
        if self.client is not None:
            from scripts.llm_client import chat

            findings = chat(
                self.client,
                f"List 3 concrete, verifiable facts about: {query}. One line each, no fluff.",
                model=self.model,
                system="You are a meticulous researcher. Facts only.",
            )
        else:
            findings = (
                f"[toy findings on '{query}']\n"
                f"1. Fact A about {query}: established baseline.\n"
                f"2. Fact B about {query}: recent development.\n"
                f"3. Fact C about {query}: open challenge."
            )
        task.artifacts.append({"type": "text", "name": "findings", "content": findings})
        task.status = "completed"
        if verbose:
            print(f"  [researcher] task {task.id} → completed, artifact {len(findings)} chars")
        return task


class WriterAgent:
    card = AgentCard(
        name="writer",
        url="a2a://local/writer",
        description="Turns raw material into polished prose.",
        skills=[
            {
                "id": "summarize",
                "name": "Summarize",
                "description": "Write a short summary from findings",
            }
        ],
    )

    def __init__(self, client=None, model: str = "deepseek-v4-flash"):
        self.client = client
        self.model = model

    def handle(self, task: Task, verbose: bool) -> Task:
        task.status = "working"
        material = task.messages[-1]["content"]
        if self.client is not None:
            from scripts.llm_client import chat

            summary = chat(
                self.client,
                f"Write a 2-3 sentence summary for a general audience from these findings:\n{material}",
                model=self.model,
                system="You are a crisp science writer.",
            )
        else:
            summary = f"[toy summary] Condensed version of: {material[:80]}..."
        task.artifacts.append({"type": "text", "name": "summary", "content": summary})
        task.status = "completed"
        if verbose:
            print(f"  [writer] task {task.id} → completed, artifact {len(summary)} chars")
        return task


# --- Orchestrator: client side of A2A ---

TASK_PROMPTS = {
    "research": "the ReAct pattern for LLM agents",
    "translate": "why context windows are a scarce resource",
    "summarize": "the difference between MCP and A2A protocols",
}


def run(task_kind: str, verbose: bool, client=None, model: str = "deepseek-v4-flash") -> None:
    researcher = ResearcherAgent(client, model)
    writer = WriterAgent(client, model)

    if verbose:
        print("=== Agent Card discovery ===")
        print(f"GET a2a://local/researcher/.well-known/agent.json\n{researcher.card.to_json()}\n")
        print(f"GET a2a://local/writer/.well-known/agent.json\n{writer.card.to_json()}\n")

    query = TASK_PROMPTS[task_kind]

    # Step 1: client sends tasks/send to researcher
    task1 = Task(id=uuid.uuid4().hex[:8])
    task1.messages.append({"role": "user", "content": query})
    rpc1 = JsonRpc.request(
        "tasks/send",
        {"id": task1.id, "message": {"role": "user", "parts": [{"type": "text", "text": query}]}},
    )
    if verbose:
        print(
            f"=== tasks/send → researcher ===\n{json.dumps(rpc1, indent=2, ensure_ascii=False)[:400]}\n"
        )
    task1 = researcher.handle(task1, verbose)
    if verbose:
        print(
            f"researcher response:\n{json.dumps(JsonRpc.response(rpc1['id'], {'id': task1.id, 'status': {'state': task1.status}}), indent=2)}\n"
        )

    # Step 2: client takes the artifact and sends a new task to writer
    findings = task1.artifacts[0]["content"]
    task2 = Task(id=uuid.uuid4().hex[:8])
    task2.messages.append({"role": "user", "content": findings})
    rpc2 = JsonRpc.request(
        "tasks/send",
        {
            "id": task2.id,
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": findings[:100] + "..."}],
            },
        },
    )
    if verbose:
        print(
            f"=== tasks/send → writer (payload = researcher's artifact) ===\n{json.dumps(rpc2, indent=2, ensure_ascii=False)[:400]}\n"
        )
    task2 = writer.handle(task2, verbose)

    print("=== Final pipeline result ===")
    print(f"Query   : {query}")
    print(f"Findings:\n{findings}")
    print(f"Summary :\n{task2.artifacts[0]['content']}")
    print(
        f"\nTask states: {task1.id}={task1.status}, {task2.id}={task2.status} (submitted → working → completed)"
    )
    print(f"Mode: {'API (both agents are real LLM calls)' if client else 'toy (templates)'}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal A2A two-agent collaboration.")
    parser.add_argument("--task", choices=list(TASK_PROMPTS), default="research")
    parser.add_argument("--use-api", action="store_true")
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    client = None
    if args.use_api:
        from scripts.llm_client import get_client

        client = get_client()
        if client is None:
            print(
                "⚠️  No API client (check agents/.env). Falling back to toy mode.\n",
                file=sys.stderr,
            )

    run(args.task, args.verbose, client, args.model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
