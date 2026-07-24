"""Task decomposer: DAG-aware decomposition with optional LLM planning.

Toy mode (default): rule-based decomposition for common goal patterns.
API mode (--use-api): uses DeepSeek to decompose arbitrary goals into DAG tasks.
  Setup: cp agents/.env.example agents/.env  # then set DEEPSEEK_API_KEY
  Install: uv sync --extra agents
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))


@dataclass
class Task:
    id: str
    name: str
    deps: list[str] = field(default_factory=list)
    done: bool = False


def topo_sort(tasks: list[Task]) -> list[list[Task]]:
    name_to_task = {t.id: t for t in tasks}
    indeg = {t.id: len(t.deps) for t in tasks}
    children: dict[str, list[str]] = {t.id: [] for t in tasks}
    for t in tasks:
        for d in t.deps:
            children[d].append(t.id)
    queue = deque(tid for tid, d in indeg.items() if d == 0)
    rounds: list[list[Task]] = []
    while queue:
        round_tasks = []
        for _ in range(len(queue)):
            tid = queue.popleft()
            round_tasks.append(name_to_task[tid])
            for child in children[tid]:
                indeg[child] -= 1
                if indeg[child] == 0:
                    queue.append(child)
        rounds.append(round_tasks)
    return rounds


def decompose_toy(goal: str) -> list[Task]:
    g = goal.lower()
    if "report" in g or "research" in g:
        return [
            Task("T1", "Gather sources"),
            Task("T2", "Read and annotate", ["T1"]),
            Task("T3", "Create outline", ["T2"]),
            Task("T4", "Write draft", ["T3"]),
            Task("T5", "Review", ["T4"]),
            Task("T6", "Finalize", ["T5"]),
        ]
    if "api" in g or "service" in g:
        return [
            Task("T1", "Design schema"),
            Task("T2", "Setup project", ["T1"]),
            Task("T3", "Implement models", ["T1"]),
            Task("T4", "Implement handlers", ["T2", "T3"]),
            Task("T5", "Test", ["T4"]),
            Task("T6", "Deploy", ["T5"]),
        ]
    return [
        Task("T1", "Analyze"),
        Task("T2", "Design", ["T1"]),
        Task("T3", "Implement", ["T2"]),
        Task("T4", "Verify", ["T3"]),
    ]


def decompose_llm(client, goal: str, model: str) -> list[Task]:
    from scripts.llm_client import chat

    prompt = f"""Break down this goal into 4-6 tasks with dependencies: "{goal}"
Return ONLY a JSON array. Each: {{"id":"T1","name":"...","deps":[]}}."""
    resp = chat(client, prompt, model=model)
    if resp.startswith("[API Error") or resp.startswith("[Toy mode]"):
        return decompose_toy(goal)
    try:
        s = resp.find("[")
        e = resp.rfind("]") + 1
        if s >= 0 and e > s:
            return [Task(t["id"], t["name"], t.get("deps", [])) for t in json.loads(resp[s:e])]
    except Exception:
        pass
    return decompose_toy(goal)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Task decomposer — toy or LLM.")
    p.add_argument("--goal", default="build a REST API")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--use-api", action="store_true")
    p.add_argument("--model", default="deepseek-v4-flash")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    client = None
    if args.use_api:
        from scripts.llm_client import get_client

        client = get_client()
        if client is None:
            print("⚠️  Falling back to toy mode.\n", file=sys.stderr)
    tasks = decompose_llm(client, args.goal, args.model) if client else decompose_toy(args.goal)
    rounds = topo_sort(tasks)
    print(f"Goal: {args.goal} [{'LLM' if client else 'toy'}]")
    print(
        f"Tasks: {len(tasks)}, Rounds: {len(rounds)}, Max parallel: {max(len(r) for r in rounds)}\n"
    )
    for i, rnd in enumerate(rounds, 1):
        names = ", ".join(t.id for t in rnd)
        deps = set(d for t in rnd for d in t.deps)
        print(f"  Round {i} [{names}]  inputs: {deps or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
