"""HITL approval demo: interrupt → human decision → resume.

The agent plans a sequence of actions. Low-risk actions auto-execute; sensitive
actions (send_email, delete_file, payment) trigger an interrupt: state is
serialized, a human approves or rejects, and the agent resumes from the
checkpoint — the core mechanism behind AG-UI / LangGraph interrupts.

Toy mode (default): scripted action plan.
API mode (--use-api): the LLM proposes the action plan as JSON.
--auto-approve: approve everything without prompting (for CI/notebooks).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --- Path setup for llm_client ---
_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))

RISK = {
    "read_file": "low",
    "search": "low",
    "send_email": "high",
    "delete_file": "high",
    "payment": "high",
}

SCENARIOS = {
    "safe": [
        {"action": "read_file", "args": {"path": "report.txt"}},
        {"action": "search", "args": {"query": "quarterly numbers"}},
    ],
    "risky": [
        {"action": "delete_file", "args": {"path": "/tmp/old_backup.zip"}},
        {"action": "payment", "args": {"amount": 500, "to": "vendor-42"}},
    ],
    "mixed": [
        {"action": "read_file", "args": {"path": "draft_email.txt"}},
        {"action": "send_email", "args": {"to": "team@corp.example", "subject": "Q3 report"}},
        {"action": "delete_file", "args": {"path": "/tmp/draft_email.txt"}},
    ],
}


@dataclass
class AgentCheckpoint:
    """Serialized agent state at an interrupt — resume needs nothing else."""

    pending_actions: list[dict]
    completed: list[dict] = field(default_factory=list)
    awaiting: dict | None = None


def plan_toy(scenario: str) -> list[dict]:
    return list(SCENARIOS[scenario])


def plan_llm(client, model: str, scenario: str) -> list[dict]:
    from scripts.llm_client import chat_json

    goal = {
        "safe": "Read report.txt and look up the quarterly numbers online.",
        "risky": "Remove /tmp/old_backup.zip and pay vendor-42 the 500 they are owed.",
        "mixed": "Email the Q3 report draft to team@corp.example, then clean up the draft file.",
    }[scenario]
    data = chat_json(
        client,
        f"Goal: {goal}\nAvailable actions: read_file(path), search(query), send_email(to, subject), delete_file(path), payment(amount, to).\n"
        f'Return JSON: {{"actions": [{{"action": "...", "args": {{...}}}}, ...]}} using 2-4 actions.',
        model=model,
    )
    actions = data.get("actions") if isinstance(data, dict) else None
    if not actions:
        print("  [planner] LLM plan unparseable, falling back to scripted plan")
        return plan_toy(scenario)
    return actions


def execute_action(action: dict) -> str:
    name, args = action.get("action", "?"), action.get("args", {})
    return f"executed {name}({json.dumps(args, ensure_ascii=False)})"


def run_plan(actions: list[dict], auto_approve: bool, verbose: bool) -> AgentCheckpoint:
    cp = AgentCheckpoint(pending_actions=list(actions))
    while cp.pending_actions:
        action = cp.pending_actions[0]
        name = action.get("action", "?")
        risk = RISK.get(name, "high")

        if risk == "high":
            # --- INTERRUPT: serialize state, hand control to the human ---
            cp.awaiting = action
            print("\n⏸️  INTERRUPT — agent wants a HIGH-risk action:")
            print(f"   {name}({json.dumps(action.get('args', {}), ensure_ascii=False)})")
            print(
                f"   [checkpoint saved: {len(cp.completed)} done, {len(cp.pending_actions)} pending]"
            )
            if auto_approve:
                print("   --auto-approve set → APPROVED (in production a human clicks this)")
                approved = True
            else:
                approved = input("   Approve? [y/N] ").strip().lower() == "y"
            # --- RESUME from checkpoint ---
            cp.awaiting = None
            if not approved:
                print("   ❌ rejected — action skipped, agent informed")
                cp.completed.append({"action": name, "result": "REJECTED by human"})
                cp.pending_actions.pop(0)
                continue
            print("   ✅ approved — resuming agent")

        result = execute_action(action)
        if verbose:
            print(f"▶ {result} (risk={risk})")
        cp.completed.append({"action": name, "result": result})
        cp.pending_actions.pop(0)
    return cp


def main() -> int:
    parser = argparse.ArgumentParser(description="HITL interrupt/approve/resume demo.")
    parser.add_argument("--scenario", choices=list(SCENARIOS), default="mixed")
    parser.add_argument(
        "--auto-approve", action="store_true", help="Approve without prompting (CI/notebooks)"
    )
    parser.add_argument("--use-api", action="store_true", help="LLM proposes the action plan")
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    client = None
    if args.use_api:
        from scripts.llm_client import get_client

        client = get_client()
        if client is None:
            print(
                "⚠️  No API client (check agents/.env). Falling back to toy plan.\n",
                file=sys.stderr,
            )

    actions = plan_llm(client, args.model, args.scenario) if client else plan_toy(args.scenario)
    if args.verbose:
        src = "LLM" if client else "scripted"
        print(f"Plan ({src}): {json.dumps(actions, ensure_ascii=False)}")

    cp = run_plan(actions, args.auto_approve, args.verbose)
    print(f"\nDone: {len(cp.completed)} actions processed.")
    rejected = [c for c in cp.completed if "REJECTED" in c["result"]]
    print(f"Rejected by human: {len(rejected)}")
    print("\nTakeaway: interrupt = serialize state + wait for external signal + resume.")
    print(
        "The agent never 'blocks on input()' in production — the harness checkpoints and re-enters."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
