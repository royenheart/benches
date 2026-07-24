"""Context budget demo: measure the real token cost of every prompt component.

Toy mode (default): ~4 chars/token heuristic estimate.
API mode (--use-api): real prompt_tokens from the DeepSeek usage field.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# --- Path setup for llm_client ---
_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))

# --- Prompt components under measurement ---

SYSTEM_PROMPT = """You are a senior backend engineer assistant. You help the user design,
review, and debug Python web services. Rules:
1. Always prefer type-annotated code.
2. When suggesting a library, state its license.
3. If the request is ambiguous, ask at most one clarifying question.
4. Never invent API endpoints; say "I don't know" when unsure.
5. Keep answers under 300 words unless the user asks for detail."""

FEWSHOT: list[tuple[str, str]] = [
    (
        "How do I add CORS to FastAPI?",
        "Use `fastapi.middleware.cors.CORSMiddleware`: `app.add_middleware(CORSMiddleware, allow_origins=[...])`. Restrict origins in production.",
    ),
    (
        "Best way to hash passwords in 2026?",
        "Use `argon2-cffi` (MIT license). `PasswordHasher().hash(pw)` / `.verify(hash, pw)`. Avoid bare bcrypt for new systems.",
    ),
    (
        "My aiohttp client leaks connections.",
        "Reuse a single `aiohttp.ClientSession` per application lifecycle; creating one per request exhausts file descriptors.",
    ),
    (
        "How to structure a SQLAlchemy session in FastAPI?",
        "Use a dependency: `def get_db(): db = SessionLocal(); try: yield db finally: db.close()` and `Depends(get_db)`.",
    ),
]

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search internal documentation",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "search query"},
                    "top_k": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Run the project test suite and return failures",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "test file or directory"},
                    "marker": {"type": "string", "description": "pytest -m marker"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "offset": {"type": "integer"},
                    "limit": {"type": "integer"},
                },
                "required": ["path"],
            },
        },
    },
]

USER_QUERY = "My FastAPI endpoint returns 502 under load. Where do I start?"


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def build_stages() -> list[tuple[str, list[dict], str]]:
    """(stage label, messages, serialized extra content for toy estimation)."""
    stages: list[tuple[str, list[dict], str]] = []
    msgs: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_QUERY},
    ]
    stages.append(("system + query", msgs, SYSTEM_PROMPT + USER_QUERY))

    msgs2: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for q, a in FEWSHOT:
        msgs2.append({"role": "user", "content": q})
        msgs2.append({"role": "assistant", "content": a})
    msgs2.append({"role": "user", "content": USER_QUERY})
    fewshot_text = "".join(q + a for q, a in FEWSHOT)
    stages.append(("+ 4 few-shot examples", msgs2, SYSTEM_PROMPT + fewshot_text + USER_QUERY))

    tools_text = json.dumps(TOOL_SCHEMAS, ensure_ascii=False)
    stages.append(
        ("+ 3 tool schemas", msgs2, SYSTEM_PROMPT + fewshot_text + tools_text + USER_QUERY)
    )
    return stages


def measure_api(client, model: str, messages: list[dict], tools: list[dict] | None) -> int:
    kwargs: dict = {"model": model, "messages": messages, "max_tokens": 1}
    if tools:
        kwargs["tools"] = tools
    resp = client.chat.completions.create(**kwargs)
    return resp.usage.prompt_tokens


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure token cost of prompt components.")
    parser.add_argument("--use-api", action="store_true", help="Use real DeepSeek usage field")
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    client = None
    if args.use_api:
        from scripts.llm_client import get_client

        client = get_client()
        if client is None:
            print(
                "⚠️  No API client (check agents/.env). Falling back to toy estimates.\n",
                file=sys.stderr,
            )

    stages = build_stages()
    print(f"{'Component':<28} {'Tokens':>8} {'Δ vs prev':>10}  Mode")
    print("-" * 60)
    prev = 0
    for i, (label, messages, serialized) in enumerate(stages):
        if client is not None:
            tools = TOOL_SCHEMAS if i == 2 else None
            tokens = measure_api(client, args.model, messages, tools)
            mode = "API usage"
        else:
            tokens = estimate_tokens(serialized)
            mode = "heuristic"
        delta = tokens - prev
        print(f"{label:<28} {tokens:>8} {delta:>+10}  {mode}")
        prev = tokens

    if args.verbose:
        print("\n--- Component sizes (chars) ---")
        print(f"system prompt : {len(SYSTEM_PROMPT)}")
        print(f"few-shot total: {sum(len(q) + len(a) for q, a in FEWSHOT)}")
        print(f"tool schemas  : {len(json.dumps(TOOL_SCHEMAS))}")
        print(f"user query    : {len(USER_QUERY)}")

    print("\nTakeaway: tool schemas and few-shot examples often cost more than the system prompt.")
    print("Every token is paid on EVERY turn — budget them like memory, not like disk.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
