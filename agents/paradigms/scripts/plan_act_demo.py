"""Plan-Act demo: task decomposition and DAG execution.

Toy mode (default): rule-based decomposition.
API mode (--use-api): uses DeepSeek to decompose goals and generate task plans.
  Setup: cp agents/.env.example agents/.env  # then set DEEPSEEK_API_KEY
  Install: uv sync --extra agents
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))


@dataclass
class Task:
    id: str
    description: str
    depends_on: list[str] = field(default_factory=list)
    status: str = "pending"
    result: str = ""


def decompose_toy(goal: str) -> list[Task]:
    g = goal.lower()
    if "report" in g:
        return [
            Task("T1", "Research the topic and gather facts"),
            Task("T2", "Organize facts into an outline", depends_on=["T1"]),
            Task("T3", "Write the first draft", depends_on=["T2"]),
            Task("T4", "Review and edit", depends_on=["T3"]),
            Task("T5", "Format final report", depends_on=["T4"]),
        ]
    if "api" in g or "service" in g:
        return [
            Task("T1", "Design API schema"),
            Task("T2", "Set up project structure", depends_on=["T1"]),
            Task("T3", "Implement data models", depends_on=["T1"]),
            Task("T4", "Implement endpoints", depends_on=["T2", "T3"]),
            Task("T5", "Write tests", depends_on=["T4"]),
        ]
    return [
        Task("T1", f"Analyze: {goal}"),
        Task("T2", "Design solution", depends_on=["T1"]),
        Task("T3", "Implement", depends_on=["T2"]),
        Task("T4", "Verify", depends_on=["T3"]),
    ]


def decompose_llm(client, goal: str, model: str) -> list[Task]:
    from scripts.llm_client import chat

    prompt = f"""Break down the following goal into 4-6 tasks with dependencies.
Goal: "{goal}"

Return ONLY a JSON array of tasks. Each task has: id (T1, T2...), description (short), depends_on (list of task IDs it depends on, empty list if none).
Task IDs must be sequential.

Example:
[
  {{"id": "T1", "description": "Research topic", "depends_on": []}},
  {{"id": "T2", "description": "Create outline", "depends_on": ["T1"]}}
]
"""
    response = chat(client, prompt, model=model)
    if response.startswith("[API Error") or response.startswith("[Toy mode]"):
        return decompose_toy(goal)
    try:
        start = response.find("[")
        end = response.rfind("]") + 1
        if start >= 0 and end > start:
            data = json.loads(response[start:end])
            return [Task(t["id"], t["description"], t.get("depends_on", [])) for t in data]
    except (json.JSONDecodeError, KeyError):
        pass
    return decompose_toy(goal)


def execute_dag(tasks: list[Task], verbose: bool) -> bool:
    completed: set[str] = set()
    remaining = list(tasks)
    round_num = 0
    while remaining:
        round_num += 1
        ready = [t for t in remaining if set(t.depends_on) <= completed]
        if not ready:
            print(f"Round {round_num}: DEADLOCK")
            return False
        if verbose:
            print(f"\nRound {round_num}: [{', '.join(t.id for t in ready)}]")
        for t in ready:
            t.status = "done"
            t.result = f"Completed: {t.description}"
            completed.add(t.id)
            if verbose:
                print(f"  {t.id}: {t.description} ✓")
        remaining = [t for t in remaining if t.id not in completed]
    return True


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plan-Act agent — toy or LLM decomposition.")
    p.add_argument("--goal", default="build a REST API")
    p.add_argument("--strategy", choices=["sequential", "dag"], default="dag")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--use-api", action="store_true", help="Use DeepSeek API for task decomposition")
    p.add_argument("--model", default="deepseek-v4-flash")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    client = None
    if args.use_api:
        from scripts.llm_client import get_client

        client = get_client()
        if client is None:
            print(
                "⚠️  Falling back to toy mode. Set DEEPSEEK_API_KEY in agents/.env", file=sys.stderr
            )
            print("   Install: uv sync --extra agents\n", file=sys.stderr)

    tasks = decompose_llm(client, args.goal, args.model) if client else decompose_toy(args.goal)

    print(f"Goal: {args.goal}")
    print(f"Mode: {'LLM' if client else 'toy'}, Tasks: {len(tasks)}\n")
    for t in tasks:
        deps = f" ← {t.depends_on}" if t.depends_on else ""
        print(f"  {t.id}: {t.description}{deps}")

    ok = execute_dag(tasks, args.verbose)
    done = sum(1 for t in tasks if t.status == "done")
    print(f"\nResult: {done}/{len(tasks)} completed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
