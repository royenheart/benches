"""Shared LLM client for agents/ — reads config from agents/.env, OpenAI-compatible API.

DeepSeek API: https://api-docs.deepseek.com/zh-cn/
- base_url: https://api.deepseek.com (no /v1 suffix required)
- Two endpoint styles (switch with DEEPSEEK_API in .env or chat(..., api=...)):
    "chat"      — /chat/completions (OpenAI Chat Completions; default)
    "responses" — /responses (OpenAI Responses API)
- Models: deepseek-flash (= deepseek-v4-flash alias), deepseek-v4-pro
- V4.1 unified mode: reasoning runs by default and consumes max_tokens FIRST;
  small budgets can return empty content (llm_client auto-retries with a bigger one).

Usage:
    from scripts.llm_client import get_client, chat

    client = get_client()
    print(chat(client, "What is an AI agent?"))
    print(chat(client, "...", api="responses"))               # Responses endpoint
    print(chat(client, "...", show_reasoning=True))           # stream + collapsible reasoning
"""

from __future__ import annotations

import os
import sys
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
        "api": os.environ.get("DEEPSEEK_API", env.get("DEEPSEEK_API", "chat")),
        "model": os.environ.get("DEEPSEEK_MODEL", env.get("DEEPSEEK_MODEL", "deepseek-flash")),
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


# --- internals ---------------------------------------------------------------


def _in_ipython() -> bool:
    try:
        return get_ipython() is not None  # noqa: F821
    except NameError:
        return False


def _display_reasoning(reasoning: str, answer: str) -> None:
    """Render reasoning collapsibly in Jupyter (<details>), dimmed in terminal."""
    if not reasoning:
        return
    if _in_ipython():
        import html

        from IPython.display import HTML, display

        display(
            HTML(
                "<details style='border:1px solid #ccc;border-radius:6px;padding:6px 10px;margin:6px 0'>"
                "<summary>💭 思考过程（点击展开/收起）</summary>"
                f"<pre style='white-space:pre-wrap;color:#666;margin:6px 0 0'>{html.escape(reasoning)}</pre>"
                "</details>"
            )
        )
    else:
        dim, reset = ("\033[2m", "\033[0m") if sys.stdout.isatty() else ("", "")
        print(f"{dim}💭 {reasoning}{reset}")


def _reasoning_tokens_of(response) -> int:
    details = getattr(getattr(response, "usage", None), "completion_tokens_details", None)
    if details is None:
        out_details = getattr(getattr(response, "usage", None), "output_tokens_details", None)
        return getattr(out_details, "reasoning_tokens", 0) or 0
    return getattr(details, "reasoning_tokens", 0) or 0


def _responses_text_and_reasoning(resp) -> tuple[str, str]:
    """Extract (answer, reasoning) from an OpenAI-Responses-style payload."""
    texts: list[str] = []
    reasonings: list[str] = []
    for item in getattr(resp, "output", None) or []:
        item_type = getattr(item, "type", "")
        if item_type == "message":
            for block in getattr(item, "content", None) or []:
                t = getattr(block, "text", None)
                if t:
                    texts.append(t)
        elif item_type == "reasoning":
            for key in ("content", "summary"):
                for block in getattr(item, key, None) or []:
                    t = getattr(block, "text", None)
                    if t:
                        reasonings.append(t)
    return "".join(texts), "\n".join(reasonings)


def _chat_responses(client, config, prompt, *, model, system, max_tokens, show_reasoning):
    kwargs = dict(
        model=model or config["model"],
        instructions=system,
        input=prompt,
        max_output_tokens=max_tokens if max_tokens is not None else config["max_tokens"],
    )
    resp = client.responses.create(**kwargs)
    text, reasoning = _responses_text_and_reasoning(resp)

    if not text:
        new_budget = max(4096, kwargs["max_output_tokens"] * 4)
        print(
            f"[llm_client] empty content (reasoning consumed budget); retrying with max_output_tokens={new_budget}",
            file=sys.stderr,
        )
        kwargs["max_output_tokens"] = new_budget
        resp = client.responses.create(**kwargs)
        text, reasoning = _responses_text_and_reasoning(resp)

    if show_reasoning:
        _display_reasoning(reasoning, text)
    if not text:
        return f"[API Error: empty content from responses api; increase max_tokens]"
    return text


# --- public API ---------------------------------------------------------------


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
    api: str | None = None,
    show_reasoning: bool = False,
) -> str:
    """Send a chat request. Falls back to toy response if client is None.

    Args:
        client: OpenAI client from get_client(), or None for toy mode.
        prompt: User message.
        model: Model name (default: DEEPSEEK_MODEL from config).
        system: System prompt.
        max_tokens: Max tokens to generate (reasoning tokens count first on V4.1).
        temperature: Sampling temperature.
        thinking: Enable DeepSeek thinking mode (extra_body={"thinking": ...}).
        reasoning_effort: "low", "medium", or "high" (requires thinking=True).
        stream: Print content tokens as they arrive.
        api: "chat" (default, /chat/completions) or "responses" (/responses).
        show_reasoning: Surface the model's reasoning — live-streamed (dimmed) in
            terminal, or wrapped in a collapsible <details> block in Jupyter.

    Returns:
        The assistant's response text. Errors print to stderr AND return
        "[API Error: ...]" (callers can check startswith("[API Error")).
    """
    config = get_config()

    if client is None:
        return _toy_response(prompt)

    api = api or config["api"]
    if api not in ("chat", "responses"):
        return f"[API Error: unknown api {api!r}; expected 'chat' or 'responses']"

    try:
        if api == "responses":
            return _chat_responses(
                client,
                config,
                prompt,
                model=model,
                system=system,
                max_tokens=max_tokens,
                show_reasoning=show_reasoning,
            )

        kwargs: dict = {
            "model": model or config["model"],
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens if max_tokens is not None else config["max_tokens"],
            "temperature": temperature if temperature is not None else config["temperature"],
            "stream": stream or show_reasoning,
        }

        # Thinking mode (DeepSeek V4 specific)
        if thinking or config["thinking"] == "enabled":
            kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
            effort = reasoning_effort or config.get("reasoning_effort", "")
            if effort:
                kwargs["reasoning_effort"] = effort

        response = client.chat.completions.create(**kwargs)

        if kwargs["stream"]:
            collected: list[str] = []
            reasoning_parts: list[str] = []
            dim, reset = ("\033[2m", "\033[0m") if sys.stdout.isatty() else ("", "")
            for chunk in response:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                reasoning_delta = getattr(delta, "reasoning_content", None)
                if reasoning_delta:
                    if show_reasoning:
                        print(f"{dim}{reasoning_delta}{reset}", end="", flush=True)
                    reasoning_parts.append(reasoning_delta)
                if delta.content:
                    print(delta.content, end="", flush=True)
                    collected.append(delta.content)
            print()
            answer = "".join(collected)
            if show_reasoning:
                _display_reasoning("".join(reasoning_parts), answer)
            return answer

        choice = response.choices[0]
        text = choice.message.content or ""
        reasoning = getattr(choice.message, "reasoning_content", None) or ""
        reasoning_tokens = _reasoning_tokens_of(response)
        if not text and reasoning_tokens:
            new_budget = max(4096, (max_tokens or config["max_tokens"]) * 4)
            print(
                f"[llm_client] empty content (reasoning_tokens={reasoning_tokens}); retrying with max_tokens={new_budget}",
                file=sys.stderr,
            )
            kwargs["stream"] = False
            kwargs["max_tokens"] = new_budget
            response = client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            text = choice.message.content or ""
            reasoning = reasoning or getattr(choice.message, "reasoning_content", None) or ""
        if show_reasoning:
            _display_reasoning(reasoning, text)
        if not text:
            message = (
                f"[API Error: empty content (finish_reason={choice.finish_reason}, "
                f"reasoning_tokens={reasoning_tokens}); increase max_tokens]"
            )
            print(message, file=sys.stderr)
            return message
        return text
    except Exception as e:
        print(f"[llm_client] API error: {e}", file=sys.stderr)
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
        try:
            response = client.chat.completions.create(
                model=model or config["model"],
                messages=messages,
                tools=tools,
                max_tokens=config["max_tokens"],
            )
        except Exception as e:
            print(f"[llm_client] API error: {e}", file=sys.stderr)
            return f"[API Error: {e}]", trace
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
