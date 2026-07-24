"""Reflexion demo: agent learns from failures through verbal reflection.

Toy mode (default): keyword-based reflection generation.
API mode (--use-api): uses DeepSeek to generate nuanced reflections.
  Setup: cp agents/.env.example agents/.env  # then set DEEPSEEK_API_KEY
  Install: uv sync --extra agents
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))


@dataclass
class Episode:
    task: str
    attempt: int
    action: str
    outcome: str
    success: bool
    reflection: str = ""


class ReflexionAgent:
    def __init__(self, client=None, model: str = "deepseek-chat"):
        self.client = client
        self.model = model
        self.episodes: list[Episode] = []
        self.lessons: list[str] = []

    def solve_math(self, problem: str, attempt: int) -> Episode:
        if "2+3" in problem and attempt == 1:
            return Episode(problem, attempt, "guessed 6", "wrong answer", False)
        if "2+3" in problem and attempt >= 2:
            if any("compute" in ln for ln in self.lessons):
                return Episode(problem, attempt, "calculated 2+3=5", "correct", True)
        if "15*3" in problem and attempt == 1:
            return Episode(problem, attempt, "guessed 35", "wrong answer", False)
        if "15*3" in problem and attempt >= 2:
            if any("verify" in ln for ln in self.lessons):
                return Episode(
                    problem, attempt, "calculated 15*3=45, verified 45/3=15", "correct", True
                )
        if "sqrt(144)" in problem and attempt == 1:
            return Episode(problem, attempt, "guessed 14", "wrong answer", False)
        if "sqrt(144)" in problem and attempt >= 2:
            if any("break down" in ln for ln in self.lessons):
                return Episode(problem, attempt, "12*12=144 so sqrt(144)=12", "correct", True)
        return Episode(problem, attempt, "unknown", "unable to solve", False)

    def reflect_toy(self, ep: Episode) -> str:
        if "guessed" in ep.action:
            return "Don't guess. Compute step by step and verify."
        elif "calculate" not in ep.action and ep.outcome == "wrong answer":
            return "Always verify your answer by reversing the operation."
        elif "unable" in ep.outcome:
            return "Break down problem: identify operation, compute, then verify."
        return "Review the approach and try a more systematic method."

    def reflect_llm(self, ep: Episode) -> str:
        from scripts.llm_client import chat

        history = "\n".join(
            f"- Attempt {e.attempt}: {e.action} → {e.outcome}" for e in self.episodes[-3:]
        )
        prompt = f"""You are analyzing a failed agent attempt to extract lessons.

Task: {ep.task}
Failed action: {ep.action}
Outcome: {ep.outcome}
Previous attempts:
{history}

Write a SHORT reflection (1-2 sentences) that would help the agent improve on the next attempt.
Focus on actionable advice, not vague suggestions.

Reflection:"""
        resp = chat(
            self.client, prompt, model=self.model, system="Be concise. Give actionable advice only."
        )
        if resp.startswith("[API Error") or resp.startswith("[Toy mode]"):
            return self.reflect_toy(ep)
        return resp.strip()

    def run(self, task: str, max_attempts: int, verbose: bool) -> bool:
        if verbose:
            use_llm = self.client is not None
            print(f"Task: {task} [{'LLM' if use_llm else 'toy'} mode]\n")
        for attempt in range(1, max_attempts + 1):
            ep = self.solve_math(task, attempt)
            if verbose:
                print(f"  Attempt {attempt}: {ep.action} → {ep.outcome}")
            if ep.success:
                if verbose:
                    print("  ✓ Solved!\n")
                self.episodes.append(ep)
                return True
            reflection = self.reflect_llm(ep) if self.client else self.reflect_toy(ep)
            ep.reflection = reflection
            self.lessons.append(reflection)
            self.episodes.append(ep)
            if verbose:
                print(f"  ✗ Reflection: {reflection}\n")
        if verbose:
            print(f"Failed after {max_attempts} attempts.")
        return False


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Reflexion demo — toy or LLM reflections.")
    p.add_argument("--task", choices=["math"], default="math")
    p.add_argument("--problem", default="2+3")
    p.add_argument("--max-attempts", type=int, default=3)
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--use-api", action="store_true", help="Use DeepSeek API for reflections")
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
                "⚠️  Falling back to toy mode. Set DEEPSEEK_API_KEY in agents/.env\n",
                file=sys.stderr,
            )
    agent = ReflexionAgent(client, args.model)
    ok = agent.run(args.problem, args.max_attempts, args.verbose)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
