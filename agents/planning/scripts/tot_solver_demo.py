"""Tree of Thoughts solver: BFS/DFS/Beam search on 24-game puzzle."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))


@dataclass
class State:
    numbers: tuple[float, ...]
    expr: str = ""
    depth: int = 0
    parent: "State | None" = None

    def score(self, target: float = 24) -> float:
        """Heuristic: how close is the best number to target?"""
        return -min(abs(n - target) for n in self.numbers)


def generate_children(state: State) -> list[State]:
    """Generate all possible next states by combining two numbers."""
    children = []
    n = len(state.numbers)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            others = [state.numbers[k] for k in range(n) if k != i and k != j]
            a, b = state.numbers[i], state.numbers[j]
            ops = [
                (a + b, f"({a}+{b})"),
                (a - b, f"({a}-{b})"),
                (a * b, f"({a}*{b})"),
            ]
            if b != 0:
                ops.append((a / b, f"({a}/{b})"))
            for val, expr_part in ops:
                children.append(
                    State(
                        numbers=tuple(others + [val]),
                        expr=expr_part,
                        depth=state.depth + 1,
                        parent=state,
                    )
                )
    return children


def is_goal(state: State, target: float = 24, eps: float = 1e-6) -> bool:
    return len(state.numbers) == 1 and abs(state.numbers[0] - target) < eps


def bfs_solve(initial: list[float], max_depth: int = 6) -> State | None:
    queue = [State(tuple(initial))]
    for state in queue:
        if is_goal(state):
            return state
        if state.depth < max_depth:
            queue.extend(generate_children(state))
    return None


def dfs_solve(initial: list[float], max_depth: int = 6) -> State | None:
    stack = [State(tuple(initial))]
    while stack:
        state = stack.pop()
        if is_goal(state):
            return state
        if state.depth < max_depth:
            stack.extend(generate_children(state))
    return None


def beam_solve(initial: list[float], beam_width: int, max_depth: int = 6) -> State | None:
    beam = [State(tuple(initial))]
    for _ in range(max_depth):
        candidates: list[State] = []
        for state in beam:
            if is_goal(state):
                return state
            candidates.extend(generate_children(state))
        if not candidates:
            break
        candidates.sort(key=lambda s: s.score(), reverse=True)
        beam = candidates[:beam_width]
    return None


# --- LLM-driven Tree of Thoughts (--use-api --strategy llm) ---


def llm_propose(client, model: str, state: State, target: float, n: int = 3) -> list[State]:
    """LLM as thought generator: propose n candidate next operations."""
    from scripts.llm_client import chat_json

    data = chat_json(
        client,
        f"24-game: current numbers {list(state.numbers)}, target {target}. "
        f"Propose {n} DIFFERENT next steps (combine exactly two numbers with + - * /). "
        'Return JSON: {"moves": [{"a": number, "b": number, "op": "+|-|*|/"}, ...]}',
        model=model,
        system="You are a creative 24-game solver. Only propose legal moves on the given numbers.",
    )
    moves = data.get("moves", []) if isinstance(data, dict) else []
    children = []
    nums = list(state.numbers)
    for mv in moves[:n]:
        try:
            a, b, op = float(mv["a"]), float(mv["b"]), mv["op"]
            if a not in nums or b not in nums or (a == b and nums.count(a) < 2):
                continue
            val = {"+": a + b, "-": a - b, "*": a * b, "/": (a / b if b != 0 else None)}[op]
            if val is None:
                continue
            rest = nums.copy()
            rest.remove(a)
            rest.remove(b)
            children.append(
                State(
                    numbers=tuple(rest + [val]),
                    expr=f"({a}{op}{b})",
                    depth=state.depth + 1,
                    parent=state,
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    return children


def llm_beam_solve(
    client, model: str, initial: list[float], beam_width: int, max_depth: int = 4
) -> State | None:
    beam = [State(tuple(initial))]
    for _ in range(max_depth):
        candidates: list[State] = []
        for state in beam:
            if is_goal(state):
                return state
            candidates.extend(llm_propose(client, model, state, 24))
        if not candidates:
            break
        candidates.sort(key=lambda s: s.score(), reverse=True)
        beam = candidates[:beam_width]
    return None


def reconstruct_path(state: State | None) -> list[str]:
    if state is None:
        return ["No solution found"]
    path = []
    while state is not None:
        path.append(state.expr if state.expr else f"start: {state.numbers}")
        state = state.parent
    return list(reversed(path))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Tree of Thoughts 24-game solver.")
    p.add_argument("--problem", choices=["24game"], default="24game")
    p.add_argument("--strategy", choices=["bfs", "dfs", "beam", "llm"], default="bfs")
    p.add_argument("--numbers", type=int, nargs=4, default=[4, 7, 8, 8])
    p.add_argument("--beam-width", type=int, default=3)
    p.add_argument("--max-depth", type=int, default=6)
    p.add_argument("--use-api", action="store_true", help="Use DeepSeek API instead of toy logic")
    p.add_argument("--model", default="deepseek-v4-flash")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    client = None
    if args.use_api:
        from scripts.llm_client import get_client

        client = get_client()
        if client is None:
            print("⚠️  API mode requested but no client available.", file=sys.stderr)
            print(
                "   Copy agents/.env.example to agents/.env and set DEEPSEEK_API_KEY",
                file=sys.stderr,
            )
            print("   Falling back to toy mode.\n", file=sys.stderr)
    solvers: dict[str, Callable[[list[float]], State | None]] = {
        "bfs": lambda nums: bfs_solve(nums, args.max_depth),
        "dfs": lambda nums: dfs_solve(nums, args.max_depth),
        "beam": lambda nums: beam_solve(nums, args.beam_width, args.max_depth),
    }
    nums = [float(n) for n in args.numbers]
    print(f"Problem: make 24 from {args.numbers}")
    print(f"Strategy: {args.strategy} (max_depth={args.max_depth})")
    if args.strategy == "llm":
        if client is None:
            print("llm strategy requires --use-api with a configured agents/.env")
            return 1
        result = llm_beam_solve(client, args.model, nums, args.beam_width, args.max_depth)
    else:
        result = solvers[args.strategy](nums)
    print(f"\nSolution path ({len(reconstruct_path(result))-1} steps):")
    for step in reconstruct_path(result):
        print(f"  {step}")
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
