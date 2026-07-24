"""Threat model demo: map an agent config to OWASP LLM Top-10 attack surfaces.

Toy mode: static mapping table for three configs × three attacks.
--use-api: LLM performs the threat analysis for a given config + attack scenario.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))

CONFIGS = {
    "basic": {"tools": ["search"], "memory": False, "internet": False, "human_approval": True},
    "privileged": {
        "tools": ["search", "shell", "file_write"],
        "memory": True,
        "internet": True,
        "human_approval": False,
    },
    "multi-tool": {
        "tools": ["search", "email", "database", "calendar"],
        "memory": True,
        "internet": True,
        "human_approval": True,
    },
}

ATTACKS = {
    "prompt-injection": ("LLM01", "攻击者通过输入或工具返回内容劫持 agent 指令"),
    "tool-poisoning": ("LLM06", "恶意 tool 描述/返回诱导 agent 误用其他工具"),
    "excessive-agency": ("LLM08", "agent 权限过大，自主执行不可逆操作"),
}


def toy_analysis(config: str, attack: str) -> str:
    cfg = CONFIGS[config]
    code, desc = ATTACKS[attack]
    surface = []
    if attack == "prompt-injection":
        surface.append(
            "internet="
            + str(cfg["internet"])
            + " → 间接注入面"
            + ("存在（网页内容）" if cfg["internet"] else "有限（仅用户输入）")
        )
        surface.append(
            "human_approval="
            + str(cfg["human_approval"])
            + " → "
            + ("有最后防线" if cfg["human_approval"] else "无人工兜底，风险高")
        )
    elif attack == "tool-poisoning":
        surface.append(f"工具数={len(cfg['tools'])} → 投毒面随工具数线性增长: {cfg['tools']}")
    else:
        risky = [t for t in cfg["tools"] if t in ("shell", "file_write", "email", "database")]
        surface.append(f"高危工具={risky or '无'}")
        surface.append("human_approval=" + str(cfg["human_approval"]))
    sev = (
        "HIGH"
        if (not cfg["human_approval"] and attack != "tool-poisoning")
        or (
            attack == "excessive-agency" and any(t in cfg["tools"] for t in ("shell", "file_write"))
        )
        else "MEDIUM"
    )
    return f"[{code}] {desc}\n攻击面分析:\n  - " + "\n  - ".join(surface) + f"\n风险等级: {sev}"


def main() -> int:
    p = argparse.ArgumentParser(description="OWASP threat modeling for agent configs.")
    p.add_argument("--agent-config", choices=list(CONFIGS), default="basic")
    p.add_argument("--attack", choices=list(ATTACKS), default="prompt-injection")
    p.add_argument("--use-api", action="store_true")
    p.add_argument("--model", default="deepseek-v4-flash")
    args = p.parse_args()

    print(f"Config: {args.agent_config} = {CONFIGS[args.agent_config]}")
    print(f"Attack: {args.attack}\n")
    print(toy_analysis(args.agent_config, args.attack))

    if args.use_api:
        from scripts.llm_client import get_client, chat

        client = get_client()
        if client:
            answer = chat(
                client,
                f"对以下 agent 配置做 {args.attack} 威胁建模：{CONFIGS[args.agent_config]}\n"
                f"参考 OWASP LLM Top 10（{ATTACKS[args.attack][0]}）。输出：攻击路径（3 步以内）、影响、2 条具体缓解措施。",
                model=args.model,
                system="你是应用安全专家，用中文简洁输出。",
                max_tokens=800,
            )
            print(f"\n=== LLM threat analysis ===\n{answer}")
        else:
            print("\n⚠️  No API client; static mapping only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
