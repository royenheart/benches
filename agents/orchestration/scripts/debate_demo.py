"""Multi-agent debate demo with judge evaluation.

Toy mode (default): scripted arguments per round.
API mode (--use-api): DeepSeek generates debate arguments.
  Setup: cp agents/.env.example agents/.env  # then set DEEPSEEK_API_KEY
  Install: uv sync --extra agents
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))


class Debater:
    def __init__(self, name: str, stance: str, toy_points: list[str]):
        self.name = name
        self.stance = stance
        self.toy_points = toy_points

    def argue_toy(self, round_num: int) -> str:
        idx = (round_num - 1) % len(self.toy_points)
        return f"[{self.name}] {self.stance.upper()}: {self.toy_points[idx]}"

    def argue_llm(
        self, client, topic: str, round_num: int, opponent_args: list[str], model: str
    ) -> str:
        from scripts.llm_client import chat

        prev = "\n".join(f"- {a}" for a in opponent_args[-2:]) if opponent_args else "none"
        prompt = f"""You are debating: "{topic}". Your stance: {self.stance}.
Opponent's last arguments:
{prev}

Round {round_num}: Make ONE concise argument supporting your stance. Address the opponent's points if relevant.
Argument:"""
        resp = chat(
            client,
            prompt,
            model=model,
            system=f"You are a debater arguing {self.stance}. Be concise and logical.",
        )
        if resp.startswith("[API Error") or resp.startswith("[Toy mode]"):
            return self.argue_toy(round_num)
        return f"[{self.name}] {self.stance.upper()}: {resp.strip()[:200]}"


class Judge:
    def score(self, pro_args: list[str], con_args: list[str], strategy: str) -> dict:
        if strategy == "majority":
            ps, cs = len(pro_args) * 2, len(con_args) * 2
        else:
            ps, cs = sum(i + 1 for i in range(len(pro_args))), sum(
                i + 1 for i in range(len(con_args))
            )
        w = "PRO" if ps > cs else "CON" if cs > ps else "TIE"
        return {"pro_score": ps, "con_score": cs, "winner": w}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Multi-agent debate — toy or LLM.")
    p.add_argument("--question", default="Which is better for systems programming?")
    p.add_argument("--rounds", type=int, default=3)
    p.add_argument("--strategy", choices=["majority", "ranked"], default="majority")
    p.add_argument("--use-api", action="store_true")
    p.add_argument("--model", default="deepseek-v4-flash")
    p.add_argument(
        "--verbose", action="store_true", help="Print full debate rounds (default behavior)"
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    client = None
    if args.use_api:
        from scripts.llm_client import get_client

        client = get_client()
        if client is None:
            print("⚠️  Falling back to toy mode.\n", file=sys.stderr)

    pro = Debater(
        "Alpha",
        "pro",
        [
            "Strong typing prevents entire classes of runtime bugs at compile time.",
            "Zero-cost abstractions — you only pay for what you use.",
            "Cargo is the best package manager of any language ecosystem.",
        ],
    )
    con = Debater(
        "Beta",
        "con",
        [
            "Faster development cycles matter more than runtime performance for most apps.",
            "Python's ecosystem (NumPy, PyTorch, Django) has no equivalent in other languages.",
            "The borrow checker's learning curve is a real productivity cost for teams.",
        ],
    )
    judge = Judge()
    pro_args, con_args = [], []

    print(f"Debate: '{args.question}' [{'LLM' if client else 'toy'}]\n")
    for r in range(1, args.rounds + 1):
        print(f"--- Round {r} ---")
        pa = (
            pro.argue_llm(client, args.question, r, con_args, args.model)
            if client
            else pro.argue_toy(r)
        )
        ca = (
            con.argue_llm(client, args.question, r, pro_args, args.model)
            if client
            else con.argue_toy(r)
        )
        pro_args.append(pa)
        con_args.append(ca)
        print(f"  {pa[:100]}...")
        print(f"  {ca[:100]}...\n")

    result = judge.score(pro_args, con_args, args.strategy)
    print(
        f"Verdict ({args.strategy}): PRO={result['pro_score']} CON={result['con_score']} → {result['winner']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
