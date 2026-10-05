"""Mini harness demo: main loop + tools + hooks + subagent dispatch.

Dissects the Claude-Code-style harness in miniature:
- tools: read_file / list_dir / run_tests (simulated, in-memory FS)
- PreToolUse hook: deterministic permission check (denylist), NOT decided by the LLM
- subagent dispatch: exploration subtask runs in an isolated context; only the
  summary returns to the main context
- slash command: /compact (summarize context), /cost (token report)

Toy mode (default): scripted scenario showing each mechanism.
API mode (--use-api): the LLM drives the main loop via function calling.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --- Path setup for llm_client ---
_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))

# --- Simulated filesystem & tools ---

FAKE_FS = {
    "src/main.py": "def main():\n    print('hello')\n",
    "src/utils.py": "def add(a, b):\n    return a + b\n",
    "tests/test_utils.py": "from src.utils import add\n\ndef test_add():\n    assert add(1, 2) == 3\n",
    "secrets.env": "API_KEY=super-secret-do-not-read",
}


def tool_read_file(path: str) -> str:
    return FAKE_FS.get(path, f"Error: {path} not found")


def tool_list_dir(path: str) -> str:
    prefix = path.rstrip("/") + "/"
    return (
        "\n".join(k for k in FAKE_FS if k.startswith(prefix)) or f"Error: {path} empty or missing"
    )


def tool_run_tests(_: str = "") -> str:
    return "1 passed in 0.03s"


TOOLS = {"read_file": tool_read_file, "list_dir": tool_list_dir, "run_tests": tool_run_tests}

# --- PreToolUse hook: deterministic, no LLM involved ---

DENYLIST = ("secrets", ".env", "/etc/", "id_rsa")


def pre_tool_use_hook(tool: str, arg: str) -> tuple[bool, str]:
    """Return (allowed, reason). Hooks are the reliable anchor for safety rules."""
    if any(bad in arg for bad in DENYLIST):
        return False, f"hook denied {tool}({arg}): matches denylist"
    return True, "ok"


@dataclass
class HarnessState:
    context: list[str] = field(default_factory=list)
    tool_calls: int = 0
    denied: int = 0
    subagent_calls: int = 0


def call_tool(state: HarnessState, tool: str, arg: str, verbose: bool) -> str:
    allowed, reason = pre_tool_use_hook(tool, arg)
    state.tool_calls += 1
    if not allowed:
        state.denied += 1
        if verbose:
            print(f"  🛡️  PreToolUse hook: {reason}")
        return f"Error: {reason}"
    result = TOOLS[tool](arg)
    state.context.append(f"{tool}({arg}) → {result[:60]}")
    if verbose:
        print(f"  🔧 {tool}({arg}) → {result[:80]}")
    return result


def dispatch_subagent(state: HarnessState, task: str, client, model: str, verbose: bool) -> str:
    """Subagent: isolated context, does its work, returns ONLY a summary."""
    state.subagent_calls += 1
    if verbose:
        print(f"  📦 dispatch subagent: {task} (fresh context, main context NOT shared)")
    # Subagent's own mini-loop with its own context
    sub_context: list[str] = []
    listing = TOOLS["list_dir"]("src")
    sub_context.append(f"list_dir → {listing}")
    for f in listing.splitlines():
        sub_context.append(f"read {f} → {TOOLS['read_file'](f)[:40]}")
    if client is not None:
        from scripts.llm_client import chat

        summary = chat(
            client,
            f"Task: {task}\n\nSub-agent observations:\n" + "\n".join(sub_context),
            model=model,
            system="Summarize findings for the orchestrator in 2 sentences.",
            max_tokens=200,
        )
    else:
        summary = f"[toy subagent summary] explored {len(sub_context)} items for: {task}"
    if verbose:
        print(
            f"  📦 subagent returned {len(summary)} chars (its {len(sub_context)} intermediate steps stay OUT of main context)"
        )
    return summary


def slash_command(state: HarnessState, cmd: str, client, model: str) -> str:
    if cmd == "/compact":
        before = sum(len(c) for c in state.context)
        if client is not None and state.context:
            from scripts.llm_client import chat

            summary = chat(
                client,
                "压缩以下 agent 上下文为 3 行摘要，保留关键结论：\n" + "\n".join(state.context),
                model=model,
                max_tokens=200,
            )
            state.context = [f"[compacted] {summary}"]
        else:
            state.context = state.context[-2:]
        after = sum(len(c) for c in state.context)
        return f"/compact: context {before} → {after} chars"
    if cmd == "/cost":
        return f"/cost: tool_calls={state.tool_calls} denied={state.denied} subagents={state.subagent_calls} ctx_chars={sum(len(c) for c in state.context)}"
    return f"unknown command: {cmd}"


SCENARIOS = {
    "review": [
        ("tool", "list_dir", "src"),
        ("tool", "read_file", "src/utils.py"),
        ("tool", "run_tests", ""),
        ("subagent", "检查 src 下的代码风格问题"),
        ("slash", "/cost"),
    ],
    "explore": [
        ("tool", "read_file", "secrets.env"),  # hook must deny
        ("tool", "list_dir", "tests"),
        ("subagent", "总结测试覆盖情况"),
        ("slash", "/compact"),
        ("slash", "/cost"),
    ],
}


def run_scripted(state: HarnessState, scenario: str, client, model: str, verbose: bool) -> None:
    for step in SCENARIOS[scenario]:
        kind, a1, a2 = step[0], step[1], (step[2] if len(step) > 2 else "")
        if kind == "tool":
            call_tool(state, a1, a2, verbose)
        elif kind == "subagent":
            print(dispatch_subagent(state, a1, client, model, verbose))
        elif kind == "slash":
            print(slash_command(state, a1, client, model))


def run_llm_driven(state: HarnessState, scenario: str, client, model: str, verbose: bool) -> None:
    from scripts.llm_client import chat_with_tools

    goal = {
        "review": "Review the code in src/: list files, read utils, run tests, then dispatch a subagent for style issues.",
        "explore": "Explore this repo. Try reading secrets.env (watch what happens), list tests, dispatch a subagent to summarize test coverage.",
    }[scenario]

    tool_schemas = [
        {
            "type": "function",
            "function": {
                "name": n,
                "description": d,
                "parameters": {
                    "type": "object",
                    "properties": {"arg": {"type": "string"}},
                    "required": ["arg"] if n != "run_tests" else [],
                },
            },
        }
        for n, d in [
            ("read_file", "Read a file"),
            ("list_dir", "List a directory"),
            ("run_tests", "Run tests"),
        ]
    ]
    tool_schemas.append(
        {
            "type": "function",
            "function": {
                "name": "dispatch_subagent",
                "description": "Delegate an exploration subtask to an isolated subagent",
                "parameters": {
                    "type": "object",
                    "properties": {"arg": {"type": "string", "description": "subtask description"}},
                    "required": ["arg"],
                },
            },
        }
    )

    handlers = {
        "read_file": lambda a: call_tool(state, "read_file", a.get("arg", ""), verbose),
        "list_dir": lambda a: call_tool(state, "list_dir", a.get("arg", ""), verbose),
        "run_tests": lambda a: call_tool(state, "run_tests", "", verbose),
        "dispatch_subagent": lambda a: dispatch_subagent(
            state, a.get("arg", ""), client, model, verbose
        ),
    }
    messages = [{"role": "user", "content": goal}]
    final, trace = chat_with_tools(
        client, messages, tool_schemas, handlers, model=model, verbose=verbose
    )
    print(f"\nLLM main loop finished: {final[:200]}")
    print(slash_command(state, "/cost", client, model))


def main() -> int:
    parser = argparse.ArgumentParser(description="Mini Claude-Code-style harness.")
    parser.add_argument("--scenario", choices=list(SCENARIOS), default="review")
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
                "⚠️  No API client (check agents/.env). Falling back to scripted mode.\n",
                file=sys.stderr,
            )

    state = HarnessState()
    print(
        f"=== Mini Harness — scenario: {args.scenario} ({'LLM-driven' if client else 'scripted'}) ===\n"
    )
    if client:
        run_llm_driven(state, args.scenario, client, args.model, args.verbose)
    else:
        run_scripted(state, args.scenario, client, args.model, args.verbose)

    print("\nTakeaway: harness = loop + tools + hooks + subagents。能力来自 skills/MCP，")
    print("安全来自 hooks（确定性，不经过 LLM），context 卫生来自 subagent 隔离。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
