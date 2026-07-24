"""Thinking mode comparison: test-time compute in practice.

Runs the same reasoning problems with thinking off vs on, and reports
correctness, reasoning-chain preview, token cost, and latency.

Toy mode (no API key): prints the concept walkthrough only.
API mode (--use-api): real calls. DeepSeek thinking mode is enabled via
extra_body={"thinking": {"type": "enabled"}}; reasoning content is read from
message fields (reasoning_content) when present.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# --- Path setup for llm_client ---
_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))

# (problem, expected substring in answer)
PROBLEMS: list[tuple[str, str]] = [
    (
        "A farmer has 17 sheep. All but 9 run away. How many are left? Answer with just the number.",
        "9",
    ),
    (
        "If a bat and a ball cost $1.10 total and the bat costs $1.00 more than the ball, how many cents does the ball cost? Answer with just the number.",
        "5",
    ),
    (
        "Alice is taller than Bob. Bob is taller than Carol. David is shorter than Carol. Who is the shortest? Answer with just the name.",
        "David",
    ),
]


def call(client, model: str, prompt: str, thinking: bool, effort: str | None) -> dict:
    kwargs: dict = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096,
    }
    if thinking:
        kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
        if effort:
            kwargs["reasoning_effort"] = effort
    t0 = time.time()
    resp = client.chat.completions.create(**kwargs)
    latency = time.time() - t0
    msg = resp.choices[0].message
    reasoning = getattr(msg, "reasoning_content", None) or ""
    usage = resp.usage
    return {
        "answer": (msg.content or "").strip(),
        "reasoning": reasoning,
        "latency": latency,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
    }


def print_concept() -> None:
    print("Test-time compute: trade more inference tokens for higher accuracy.")
    print("Thinking mode makes the model emit a reasoning chain before the final answer.")
    print()
    print("Problems used in this demo:")
    for p, expected in PROBLEMS:
        print(f"  - {p}  (expect: {expected})")
    print()
    print("Run with --use-api to see the real comparison.")
    print("Toy mode cannot simulate reasoning — that's the whole point of thinking mode.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare thinking on/off on reasoning problems.")
    parser.add_argument("--use-api", action="store_true")
    parser.add_argument(
        "--model", default="deepseek-v4-pro", help="thinking 模式推荐 deepseek-v4-pro"
    )
    parser.add_argument("--effort", choices=["low", "medium", "high"], default=None)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    client = None
    if args.use_api:
        from scripts.llm_client import get_client

        client = get_client()
        if client is None:
            print("⚠️  No API client (check agents/.env).", file=sys.stderr)

    if client is None:
        print_concept()
        return 0

    print(f"Model: {args.model}  effort: {args.effort or 'default'}\n")
    total = {"off": 0, "on": 0}
    correct = {"off": 0, "on": 0}
    for i, (problem, expected) in enumerate(PROBLEMS, 1):
        print(f"=== Problem {i}: {problem[:60]}... (expect: {expected}) ===")
        for mode, thinking in (("off", False), ("on", True)):
            r = call(client, args.model, problem, thinking, args.effort)
            ok = expected.lower() in r["answer"].lower()
            correct[mode] += ok
            total[mode] += r["completion_tokens"]
            print(
                f"  thinking={mode:>3}: answer={r['answer'][:40]!r} correct={ok} "
                f"tokens={r['completion_tokens']} latency={r['latency']:.1f}s"
            )
            if args.verbose and r["reasoning"]:
                print(f"    reasoning preview: {r['reasoning'][:200]}...")
        print()

    print("=== Summary ===")
    for mode in ("off", "on"):
        print(
            f"  thinking={mode:>3}: {correct[mode]}/{len(PROBLEMS)} correct, {total[mode]} completion tokens total"
        )
    print("\nTakeaway: thinking mode spends more tokens to buy accuracy on multi-step problems;")
    print("on trivial recall it only adds cost. Match the mode to the problem, not to preference.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
