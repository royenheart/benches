"""Framework decision helper: score requirements against framework strengths.

Toy mode: keyword scoring table.
--use-api: LLM maps free-text requirements to a ranked recommendation with reasons.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))

FRAMEWORKS = {
    "LangGraph": {
        "durable": 5,
        "multi-agent": 4,
        "learning-curve": 2,
        "openai-native": 1,
        "enterprise": 4,
    },
    "OpenAI Agents SDK": {
        "durable": 3,
        "multi-agent": 3,
        "learning-curve": 5,
        "openai-native": 5,
        "enterprise": 3,
    },
    "CrewAI": {
        "durable": 2,
        "multi-agent": 4,
        "learning-curve": 4,
        "openai-native": 2,
        "enterprise": 3,
    },
    "AutoGen": {
        "durable": 3,
        "multi-agent": 5,
        "learning-curve": 3,
        "openai-native": 2,
        "enterprise": 3,
    },
    "Google ADK": {
        "durable": 4,
        "multi-agent": 4,
        "learning-curve": 3,
        "openai-native": 1,
        "enterprise": 5,
    },
}

KEYWORDS = {
    "durable": ("durable", "持久", "checkpoint", "long-running", "恢复"),
    "multi-agent": ("multi-agent", "多 agent", "多智能体", "team", "协作"),
    "learning-curve": ("simple", "简单", "quick", "快速上手", "prototype"),
    "openai-native": ("openai", "gpt"),
    "enterprise": ("enterprise", "企业", "cloud", "governance", "合规"),
}


def score_toy(requirement: str) -> list[tuple[str, int, list[str]]]:
    req = requirement.lower()
    active = [dim for dim, kws in KEYWORDS.items() if any(k in req for k in kws)] or [
        "learning-curve"
    ]
    ranked = []
    for fw, dims in FRAMEWORKS.items():
        matched = [d for d in active if d in dims]
        total = sum(dims[d] for d in matched)
        ranked.append((fw, total, matched))
    ranked.sort(key=lambda x: -x[1])
    return ranked


def main() -> int:
    p = argparse.ArgumentParser(description="Framework selection helper.")
    p.add_argument(
        "--requirement", default="I need durable multi-agent workflows with human approval"
    )
    p.add_argument("--use-api", action="store_true")
    p.add_argument("--model", default="deepseek-v4-flash")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    ranked = score_toy(args.requirement)
    print(f"Requirement: {args.requirement}\n")
    print("Keyword scoring:")
    for fw, total, matched in ranked:
        print(f"  {fw:<22} {total:>3}  (matched: {', '.join(matched) or '-'})")

    if args.use_api:
        from scripts.llm_client import get_client, chat

        client = get_client()
        if client:
            table = "\n".join(f"{fw}: {dims}" for fw, dims in FRAMEWORKS.items())
            answer = chat(
                client,
                f"框架能力表（1-5 分）：\n{table}\n\n需求：{args.requirement}\n\n推荐一个框架并给出 3 条理由，再指出它的主要风险。",
                model=args.model,
                system="你是务实的架构师，中文简洁回答。",
                max_tokens=800,
            )
            print(f"\n=== LLM recommendation ===\n{answer}")
        else:
            print("\n⚠️  No API client; keyword scoring only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
