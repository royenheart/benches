"""Cost manager demo: token budget + tool-call limits with three strategies.

Strategies: hard-limit (stop), graceful (finish current step then stop), warn (log only).
With --use-api, each "step" is a real (small) LLM call so token accounting is real.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))


class BudgetExceeded(Exception):
    pass


class CostManager:
    def __init__(self, budget_tokens: int, budget_tool_calls: int, strategy: str):
        self.budget_tokens = budget_tokens
        self.budget_tool_calls = budget_tool_calls
        self.strategy = strategy
        self.tokens = 0
        self.tool_calls = 0

    def charge_tokens(self, n: int) -> str:
        self.tokens += n
        if self.tokens > self.budget_tokens:
            if self.strategy == "hard-limit":
                raise BudgetExceeded(f"token budget exceeded ({self.tokens}/{self.budget_tokens})")
            if self.strategy == "warn":
                return f"⚠️ over token budget: {self.tokens}/{self.budget_tokens}"
            return "graceful: will stop after this step"
        return "ok"

    def charge_tool_call(self) -> str:
        self.tool_calls += 1
        if self.tool_calls > self.budget_tool_calls:
            if self.strategy == "hard-limit":
                raise BudgetExceeded(
                    f"tool-call budget exceeded ({self.tool_calls}/{self.budget_tool_calls})"
                )
            if self.strategy == "warn":
                return f"⚠️ over tool-call budget: {self.tool_calls}/{self.budget_tool_calls}"
            return "graceful: will stop after this step"
        return "ok"


def run_agent(cm: CostManager, client, model: str, steps: int, verbose: bool) -> None:
    for i in range(1, steps + 1):
        try:
            status = cm.charge_tool_call()
            if verbose:
                print(f"step {i}: tool_call budget → {status}")
            if client is not None:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": f"Say 'step {i}' and nothing else."}],
                    max_tokens=10,
                )
                used = resp.usage.total_tokens
            else:
                used = 120  # toy: pretend each step costs 120 tokens
            status = cm.charge_tokens(used)
            if verbose:
                print(f"step {i}: +{used} tokens (total {cm.tokens}/{cm.budget_tokens}) → {status}")
            if cm.strategy == "graceful" and "graceful" in status:
                print("graceful stop: finishing cleanly after current step")
                break
        except BudgetExceeded as e:
            print(f"🛑 {e} — agent halted at step {i}")
            break


def main() -> int:
    p = argparse.ArgumentParser(description="Token/tool-call budget enforcement demo.")
    p.add_argument("--budget-tokens", type=int, default=1000)
    p.add_argument("--budget-tool-calls", type=int, default=10)
    p.add_argument("--strategy", choices=["hard-limit", "graceful", "warn"], default="hard-limit")
    p.add_argument("--steps", type=int, default=15)
    p.add_argument("--use-api", action="store_true")
    p.add_argument("--model", default="deepseek-v4-flash")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    client = None
    if args.use_api:
        from scripts.llm_client import get_client

        client = get_client()
        if client is None:
            print("⚠️  No API client; using toy token counts.\n", file=sys.stderr)

    cm = CostManager(args.budget_tokens, args.budget_tool_calls, args.strategy)
    run_agent(cm, client, args.model, args.steps, args.verbose)
    print(f"\nFinal: {cm.tokens} tokens, {cm.tool_calls} tool calls, strategy={args.strategy}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
