"""Skill loader demo: progressive disclosure in ~100 lines.

Layer 1 (always): scan skills-dir, parse frontmatter only (name + description).
Layer 2 (on trigger): load the full SKILL.md body of the selected skill.
Layer 3 (on demand): referenced resource files (out of scope for this demo).

Toy mode (default): keyword match for skill selection + template answer.
API mode (--use-api): LLM selects the skill from metadata, then answers with
the skill body injected into the system prompt. Prints the with/without-skill
comparison so the effect of injection is visible.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# --- Path setup for llm_client ---
_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))

DEFAULT_SKILLS_DIR = _HERE.parent / "skills"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split '---\nkey: value\n---\nbody' into (metadata, body)."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not match:
        return {}, text
    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta, match.group(2).strip()


def scan_skills(skills_dir: Path) -> list[dict]:
    """Layer 1: metadata only — this is what stays in context permanently."""
    skills = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        meta, _body = parse_frontmatter(skill_md.read_text())
        if meta.get("name"):
            skills.append(
                {"name": meta["name"], "description": meta.get("description", ""), "path": skill_md}
            )
    return skills


def load_skill_body(skill: dict) -> str:
    """Layer 2: full instructions, loaded only when the skill triggers."""
    _meta, body = parse_frontmatter(skill["path"].read_text())
    return body


def select_toy(query: str, skills: list[dict]) -> dict | None:
    keywords = {
        "unit-converter": ("换算", "转换", "英里", "公里", "convert", "mile", "km", "磅", "温度")
    }
    for skill in skills:
        if any(k in query.lower() for k in keywords.get(skill["name"], ())):
            return skill
    return None


def select_llm(client, model: str, query: str, skills: list[dict]) -> dict | None:
    from scripts.llm_client import chat_json

    catalog = "\n".join(f"- {s['name']}: {s['description']}" for s in skills)
    data = chat_json(
        client,
        f"可用 skills：\n{catalog}\n\n用户问题：{query}\n"
        f'哪个 skill 应该处理这个问题？返回 JSON: {{"skill": "<name>"}} 或 {{"skill": null}}（都不匹配时）。',
        model=model,
    )
    name = data.get("skill") if isinstance(data, dict) else None
    return next((s for s in skills if s["name"] == name), None)


def main() -> int:
    parser = argparse.ArgumentParser(description="Mini skill loader with progressive disclosure.")
    parser.add_argument("--query", default="把 5 公里换算成英里")
    parser.add_argument("--skills-dir", type=Path, default=DEFAULT_SKILLS_DIR)
    parser.add_argument("--use-api", action="store_true")
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    client = None
    if args.use_api:
        from scripts.llm_client import get_client

        client = get_client()
        if client is None:
            print(
                "⚠️  No API client (check agents/.env). Falling back to toy mode.\n",
                file=sys.stderr,
            )

    # Layer 1: metadata scan (always resident)
    skills = scan_skills(args.skills_dir)
    print(f"=== Layer 1: metadata resident ({len(skills)} skills) ===")
    meta_tokens = 0
    for s in skills:
        line = f"- {s['name']}: {s['description']}"
        meta_tokens += len(line) // 4
        print(f"  {line[:90]}")
    print(f"  常驻成本 ≈ {meta_tokens} tokens（vs 全量注入见 Layer 2）\n")

    # Selection
    selected = (
        select_llm(client, args.model, args.query, skills)
        if client
        else select_toy(args.query, skills)
    )
    print(f"=== Selection ({'LLM' if client else 'toy'}) ===")
    if not selected:
        print("  无匹配 skill → 直接回答")
        body = ""
    else:
        print(f"  → {selected['name']}")
        # Layer 2: load body only now
        body = load_skill_body(selected)
        print(f"\n=== Layer 2: body loaded on trigger (≈{len(body) // 4} tokens) ===")
        if args.verbose:
            print(body[:400] + ("..." if len(body) > 400 else ""))

    # Answer with/without skill
    print("\n=== Answer comparison ===")
    if client:
        from scripts.llm_client import chat

        without = chat(client, args.query, model=args.model, max_tokens=300)
        print(f"[无 skill]\n{without}\n")
        if body:
            with_skill = chat(
                client,
                args.query,
                model=args.model,
                system=f"You have the following skill. Follow it exactly.\n\n{body}",
                max_tokens=300,
            )
            print(f"[注入 skill]\n{with_skill}")
    else:
        print(f"[无 skill / toy] {args.query} → 模板回答：结果约为 3.1（未展示公式与系数）")
        if body:
            print(
                "[注入 skill / toy] 按 skill 规则：结果 = 5 km × 0.621371 = 3.1069 mile（4 位有效数字）；反向验证：3.1069 × 1.60934 ≈ 5.0000 km ✓"
            )

    print("\nTakeaway: skill = 按需注入的指令包。metadata 常驻让 agent「知道会什么」，")
    print("body 触发时加载让 agent「知道怎么做」— 全量注入既贵又稀释注意力。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
