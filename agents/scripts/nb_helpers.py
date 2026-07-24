"""Notebook helpers for agents/ — uniform API-first setup for teaching notebooks.

Usage (first code cell of every agents notebook):

    from nb_helpers import setup, chat, show_trace
    client = setup()

setup() locates the repo root (xmake.lua), puts agents/ on sys.path,
builds the DeepSeek client from agents/.env, and prints the current mode.
Without an API key it returns None and every call falls back to toy mode.
"""

from __future__ import annotations

import sys
from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    """Walk up from `start` (default: cwd) until a directory containing xmake.lua."""
    p = (start or Path.cwd()).resolve()
    while p != p.parent:
        if (p / "xmake.lua").exists():
            return p
        p = p.parent
    raise RuntimeError(f"repo root (xmake.lua) not found above {start or Path.cwd()}")


def setup(verbose: bool = True):
    """Prepare sys.path and return an API client (or None for toy mode)."""
    root = find_repo_root()
    agents_dir = root / "agents"
    if str(agents_dir) not in sys.path:
        sys.path.insert(0, str(agents_dir))

    from scripts.llm_client import get_client, get_config

    client = get_client()
    if verbose:
        if client is None:
            print("🔧 Toy 模式 — 未找到 API key。")
            print("   真实调用：cp agents/.env.example agents/.env 并填入 DEEPSEEK_API_KEY")
        else:
            cfg = get_config()
            print(f"🌐 API 模式 — model={cfg['model']}  base_url={cfg['base_url']}")
    return client


def chat(client, prompt: str, **kwargs) -> str:
    """Thin wrapper over llm_client.chat (auto toy fallback when client is None)."""
    from scripts.llm_client import chat as _chat

    return _chat(client, prompt, **kwargs)


def chat_with_tools(client, messages, tools, tool_handlers, **kwargs):
    """Thin wrapper over llm_client.chat_with_tools."""
    from scripts.llm_client import chat_with_tools as _cwt

    return _cwt(client, messages, tools, tool_handlers, **kwargs)


def chat_json(client, prompt: str, **kwargs) -> dict:
    """Thin wrapper over llm_client.chat_json."""
    from scripts.llm_client import chat_json as _cj

    return _cj(client, prompt, **kwargs)


def show_trace(trace: list[dict], title: str = "Tool Trace") -> None:
    """Pretty-print a tool-call trace returned by chat_with_tools."""
    print(f"=== {title} ({len(trace)} calls) ===")
    for i, entry in enumerate(trace, 1):
        print(f"[{i}] {entry['tool']}({entry['args']})")
        print(f"    → {entry['result'][:200]}")
