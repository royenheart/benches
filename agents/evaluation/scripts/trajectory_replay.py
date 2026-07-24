"""Trajectory replay: rebuild an agent run from a JSONL log and score it.

Log format (one JSON object per line):
{"step": 1, "action": "search", "args": {"query": "python"}, "result": "ok", "valid": true, "efficient": true}

Usage: python agents/evaluation/scripts/trajectory_replay.py --trajectory-file <log.jsonl>
With --use-api, an LLM additionally judges each step's decision quality.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))

SAMPLE = [
    {
        "step": 1,
        "action": "search",
        "args": {"query": "python"},
        "result": "10 hits",
        "valid": True,
        "efficient": True,
    },
    {
        "step": 2,
        "action": "search",
        "args": {"query": "python"},
        "result": "10 hits",
        "valid": True,
        "efficient": False,
    },
    {
        "step": 3,
        "action": "search",
        "args": {"query": "python history"},
        "result": "5 hits",
        "valid": True,
        "efficient": True,
    },
    {"step": 4, "action": "done", "args": {}, "result": "answer", "valid": True, "efficient": True},
]


def load_trajectory(path: Path | None) -> list[dict]:
    if path and path.exists():
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    print("(no file given — replaying built-in sample trajectory)")
    return SAMPLE


def score(steps: list[dict]) -> dict:
    valid = sum(1 for s in steps if s.get("valid"))
    efficient = sum(1 for s in steps if s.get("efficient"))
    repeated = len(steps) - len({json.dumps(s.get("args", {}), sort_keys=True) for s in steps})
    return {
        "steps": len(steps),
        "valid_rate": valid / len(steps),
        "efficiency": efficient / len(steps),
        "repeated_calls": repeated,
    }


def llm_judge_steps(client, model: str, steps: list[dict]) -> str:
    from scripts.llm_client import chat

    traj = "\n".join(
        f"step {s['step']}: {s['action']}({json.dumps(s.get('args', {}), ensure_ascii=False)}) → {s.get('result', '')}"
        for s in steps
    )
    return chat(
        client,
        f"Agent trajectory:\n{traj}\n\n逐步点评决策质量，指出最差的一步及原因，最后给总体评分(0-10)。",
        model=model,
        system="你是严格的 agent 评审，用中文简洁输出。",
        max_tokens=400,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Replay and score an agent trajectory.")
    p.add_argument("--trajectory-file", type=Path, default=None)
    p.add_argument("--gold-file", type=Path, default=None, help="reserved for future diff scoring")
    p.add_argument("--use-api", action="store_true")
    p.add_argument("--model", default="deepseek-v4-flash")
    args = p.parse_args()

    steps = load_trajectory(args.trajectory_file)
    print(f"Replayed {len(steps)} steps:")
    for s in steps:
        flag = "" if s.get("valid") else " [INVALID]"
        slow = "" if s.get("efficient") else " [REDUNDANT]"
        print(
            f"  step {s['step']}: {s['action']}({json.dumps(s.get('args', {}), ensure_ascii=False)}){flag}{slow}"
        )

    metrics = score(steps)
    print(
        f"\nMetrics: valid={metrics['valid_rate']:.0%} efficient={metrics['efficiency']:.0%} repeated={metrics['repeated_calls']}"
    )

    if args.use_api:
        from scripts.llm_client import get_client

        client = get_client()
        if client:
            print(
                f"\n=== LLM step-by-step review ===\n{llm_judge_steps(client, args.model, steps)}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
