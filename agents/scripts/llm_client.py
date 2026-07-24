"""Shared LLM client for agents/ — reads config from agents/.env, uses OpenAI-compatible API.

DeepSeek V4 API: https://api-docs.deepseek.com/zh-cn/
- base_url: https://api.deepseek.com (no /v1 suffix)
- Models: deepseek-v4-flash (fast), deepseek-v4-pro (powerful)
- Thinking mode: extra_body={"thinking": {"type": "enabled"}}

Usage:
    from scripts.llm_client import get_client, chat

    client = get_client()
    response = chat(client, "What is an AI agent?", model="deepseek-v4-flash")
    print(response)
"""

from __future__ import annotations

import os
from pathlib import Path


def _find_agents_root() -> Path:
    p = Path(__file__).resolve().parent.parent  # scripts/ -> agents/
    return p


def _load_env() -> dict[str, str]:
    env_file = _find_agents_root() / ".env"
    env_vars: dict[str, str] = {}
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                env_vars[key] = value
    return env_vars


def get_config() -> dict:
    env = _load_env()
    return {
        "base_url": os.environ.get(
            "DEEPSEEK_BASE_URL", env.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        ),
        "api_key": os.environ.get("DEEPSEEK_API_KEY", env.get("DEEPSEEK_API_KEY", "")),
        "model": os.environ.get("DEEPSEEK_MODEL", env.get("DEEPSEEK_MODEL", "deepseek-v4-flash")),
        "max_tokens": int(
            os.environ.get("DEEPSEEK_MAX_TOKENS", env.get("DEEPSEEK_MAX_TOKENS", "4096"))
        ),
        "temperature": float(
            os.environ.get("DEEPSEEK_TEMPERATURE", env.get("DEEPSEEK_TEMPERATURE", "0.7"))
        ),
        "thinking": os.environ.get("DEEPSEEK_THINKING", env.get("DEEPSEEK_THINKING", "")),
        "reasoning_effort": os.environ.get(
            "DEEPSEEK_REASONING_EFFORT", env.get("DEEPSEEK_REASONING_EFFORT", "")
        ),
    }


def get_client():
    """Create an OpenAI-compatible client for DeepSeek API.

    Requires: pip install openai
    Returns None if openai is not installed or API key is missing (toy mode).
    """
    config = get_config()
    if not config["api_key"] or config["api_key"] == "sk-your-api-key-here":
        return None
    try:
        from openai import OpenAI

        return OpenAI(base_url=config["base_url"], api_key=config["api_key"])
    except ImportError:
        return None


def chat(
    client,
    prompt: str,
    *,
    model: str | None = None,
    system: str = "You are a helpful AI assistant.",
    max_tokens: int | None = None,
    temperature: float | None = None,
    thinking: bool = False,
    reasoning_effort: str | None = None,
    stream: bool = False,
) -> str:
    """Send a chat completion request. Falls back to toy response if client is None.

    Args:
        client: OpenAI client from get_client(), or None for toy mode.
        prompt: User message.
        model: Model name (default: DEEPSEEK_MODEL from config).
        system: System prompt.
        max_tokens: Max tokens to generate.
        temperature: Sampling temperature.
        thinking: Enable DeepSeek thinking mode (shows reasoning chain).
        reasoning_effort: "low", "medium", or "high" (requires thinking=True).
        stream: If True, print tokens as they arrive.

    Returns:
        The assistant's response text.
    """
    config = get_config()

    if client is None:
        return _toy_response(prompt)

    try:
        kwargs: dict = {
            "model": model or config["model"],
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens if max_tokens is not None else config["max_tokens"],
            "temperature": temperature if temperature is not None else config["temperature"],
            "stream": stream,
        }

        # Thinking mode (DeepSeek V4 specific)
        if thinking or config["thinking"] == "enabled":
            kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
            effort = reasoning_effort or config.get("reasoning_effort", "")
            if effort:
                kwargs["reasoning_effort"] = effort

        if stream:
            response = client.chat.completions.create(**kwargs)
            collected = []
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    print(token, end="", flush=True)
                    collected.append(token)
            print()
            return "".join(collected)
        else:
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
    except Exception as e:
        return f"[API Error: {e}]"


def chat_with_tools(
    client,
    messages: list[dict],
    tools: list[dict],
    tool_handlers: dict,
    *,
    model: str | None = None,
    max_turns: int = 8,
    verbose: bool = False,
) -> tuple[str, list[dict]]:
    """Run a real function-calling loop (OpenAI tools API).

    Args:
        client: OpenAI client from get_client(), or None for toy fallback.
        messages: Conversation so far ( mutated in place across turns).
        tools: OpenAI tool schemas, e.g. [{"type": "function", "function": {"name": ..., "description": ..., "parameters": {...}}}].
        tool_handlers: {tool_name: callable(args: dict) -> str} executing each call.
        model: Model name (default: DEEPSEEK_MODEL from config).
        max_turns: Safety bound on loop iterations.
        verbose: Print each tool call and result.

    Returns:
        (final assistant text, trace) where trace is a list of
        {"tool": name, "args": dict, "result": str} entries.
    """
    import json as _json

    config = get_config()
    if client is None:
        return (
            "[Toy mode] chat_with_tools needs an API client. Set DEEPSEEK_API_KEY in agents/.env.",
            [],
        )

    trace: list[dict] = []
    for _ in range(max_turns):
        response = client.chat.completions.create(
            model=model or config["model"],
            messages=messages,
            tools=tools,
            max_tokens=config["max_tokens"],
        )
        msg = response.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not getattr(msg, "tool_calls", None):
            return msg.content or "", trace

        for call in msg.tool_calls:
            name = call.function.name
            try:
                args = _json.loads(call.function.arguments or "{}")
            except _json.JSONDecodeError:
                args = {}
            handler = tool_handlers.get(name)
            result = handler(args) if handler else f"Error: unknown tool '{name}'"
            result = str(result)
            trace.append({"tool": name, "args": args, "result": result})
            if verbose:
                print(f"  🔧 {name}({args}) → {result[:120]}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    return "[Max turns reached without final answer]", trace


def chat_json(
    client,
    prompt: str,
    *,
    model: str | None = None,
    system: str = "You are a helpful AI assistant. Respond with valid JSON only — no markdown fences, no commentary.",
    max_tokens: int | None = None,
) -> dict:
    """Ask for a structured JSON response and parse it.

    Returns {} on toy mode, API error, or unparseable output.
    """
    import json as _json
    import re as _re

    text = chat(client, prompt, model=model, system=system, max_tokens=max_tokens)
    if client is None or text.startswith("[API Error") or text.startswith("[Toy mode]"):
        return {}
    # Strip markdown code fences if the model adds them despite instructions.
    cleaned = _re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=_re.MULTILINE)
    try:
        return _json.loads(cleaned)
    except _json.JSONDecodeError:
        match = _re.search(r"\{.*\}", cleaned, _re.DOTALL)
        if match:
            try:
                return _json.loads(match.group(0))
            except _json.JSONDecodeError:
                return {}
        return {}


def _toy_response(prompt: str) -> str:
    """Toy fallback when no API client is available."""
    keywords = {
        "agent": "An AI agent is a system that perceives its environment through sensors and acts upon it through actuators to achieve specific goals. Key components: model/controller, state/memory, tools/actions, and a control loop.",
        "react": "ReAct (Reasoning + Acting) interleaves thought traces with tool-use actions. Unlike pure Chain-of-Thought, ReAct grounds reasoning in external observations, reducing hallucination.",
        "tool": "Tool use in agents involves: 1) defining a tool schema (name, description, inputSchema), 2) the agent deciding which tool to call, 3) executing the tool, 4) incorporating results into context.",
        "mcp": "MCP (Model Context Protocol) is an open standard by Anthropic for AI-tool communication. It uses JSON-RPC 2.0 over stdio or SSE, with three primitives: Tools, Resources, and Prompts.",
        "rag": "RAG (Retrieval-Augmented Generation) enhances LLM responses by retrieving relevant documents before generation. Pipeline: query → embed → search index → retrieve top-K → augment context → generate.",
        "safety": "Agent safety covers prompt injection defense, tool-call validation, output guardrails, sandboxing, and least-privilege access. OWASP Top 10 for LLM 2025 lists Prompt Injection as the #1 risk.",
        "planning": "Agent planning involves task decomposition (breaking goals into subtasks), dependency management (DAG scheduling), and search strategies (BFS, DFS, Beam Search, Tree of Thoughts).",
        "memory": "Agent memory includes working memory (current task state), short-term memory (conversation context), long-term memory (persistent knowledge via RAG/vector DB), and episodic memory (past experiences for learning).",
        "multi-agent": "Multi-agent systems coordinate specialized agents through patterns like Planner-Worker-Critic, Debate, Role-based teams, and Blackboard architectures. Key challenges: communication protocols, task allocation, conflict resolution.",
        "evaluation": "Agent evaluation spans unit tests (tool correctness), component tests (decision quality), and end-to-end benchmarks (SWE-bench, GAIA, WebArena). LLM-as-Judge is common but prone to position/verbosity bias.",
    }
    for kw, resp in keywords.items():
        if kw in prompt.lower():
            return resp
    return f"[Toy mode] I received your prompt about '{prompt[:50]}...'. To get real responses, copy agents/.env.example to agents/.env and set your DEEPSEEK_API_KEY."
