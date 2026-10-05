"""Multi-agent role team demo: researcher + writer + fact-checker.

Toy mode (default): keyword-based agent responses.
API mode (--use-api): uses DeepSeek for each agent's response.
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
class Agent:
    name: str
    role: str
    expertise: list[str]

    def execute_toy(self, task: str, context: str) -> str:
        kb = {
            "climate": "Climate change is driven by greenhouse gas emissions. Global temperatures risen 1.1°C.",
            "python": "Python used by 49% of developers. Excels in ML, web dev, automation.",
            "default": f"Research findings on '{task}': topic documented with reliable sources.",
        }
        for k in kb:
            if k in task.lower():
                return kb[k]
        return kb["default"]

    def execute_llm(self, client, task: str, context: str, model: str) -> str:
        from scripts.llm_client import chat

        prompt = f"""You are a {self.role}. Your expertise: {', '.join(self.expertise)}.
Task: {task}
Context from previous agents: {context if context else 'none'}

Provide a SHORT, factual response (2-4 sentences)."""
        resp = chat(
            client,
            prompt,
            model=model,
            system=f"You are a {self.role} agent. Be concise and factual.",
        )
        return resp if not resp.startswith("[") else self.execute_toy(task, context)


class Researcher(Agent):
    def __init__(self):
        super().__init__("Researcher", "Research", ["fact-finding", "source-gathering"])


class Writer(Agent):
    def __init__(self):
        super().__init__("Writer", "Synthesis", ["writing", "structuring"])


class FactChecker(Agent):
    def __init__(self):
        super().__init__("FactChecker", "Verification", ["accuracy", "consistency"])

    def execute_toy(self, task: str, context: str) -> str:
        if "climate" in context.lower() and "2.0" not in context:
            return "ISSUES: temperature claim needs verification"
        return "VERIFIED: All claims consistent."


def run_team(scenario: str, verbose: bool, client=None, model: str = "deepseek-chat") -> str:
    researcher = Researcher()
    writer = Writer()
    checker = FactChecker()
    ctx = (
        researcher.execute_llm(client, scenario, "", model)
        if client
        else researcher.execute_toy(scenario, "")
    )
    if verbose:
        print(f"[{researcher.name}] {ctx[:80]}...\n")
    report = (
        writer.execute_llm(client, scenario, ctx, model)
        if client
        else writer.execute_toy(scenario, ctx)
    )
    if verbose:
        print(f"[{writer.name}] {report[:120]}...\n")
    verdict = (
        checker.execute_llm(client, scenario, report, model)
        if client
        else checker.execute_toy(scenario, report)
    )
    if verbose:
        print(f"[{checker.name}] {verdict}\n")
    return verdict


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Multi-agent role team — toy or LLM.")
    p.add_argument("--scenario", default="climate impacts")
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
    print(f"Scenario: {args.scenario} [{'LLM' if client else 'toy'}]\n")
    verdict = run_team(args.scenario, args.verbose, client, args.model)
    if not args.verbose:
        print(f"Result: {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
