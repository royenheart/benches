"""ReAct loop demo: pure stdlib agent with toy tools, or real LLM via DeepSeek API.

Toy mode (default): keyword-based reasoning + static knowledge base.
API mode (--use-api): uses DeepSeek chat model for thought generation and tool decisions.
  Setup: cp agents/.env.example agents/.env  # then set DEEPSEEK_API_KEY
  Install: uv sync --extra agents
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --- Path setup for llm_client ---
_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))


@dataclass
class ToolResult:
    success: bool
    content: str
    error: str = ""


@dataclass
class AgentState:
    goal: str
    steps: int = 0
    observations: list[str] = field(default_factory=list)
    done: bool = False


def tool_calculator(expr: str) -> ToolResult:
    allowed = set("0123456789+-*/().% ")
    if not all(c in allowed for c in expr):
        return ToolResult(False, "", f"Disallowed characters in '{expr}'")
    try:
        return ToolResult(True, str(eval(expr, {"__builtins__": {}}, {})))
    except Exception as e:
        return ToolResult(False, "", str(e))


def tool_search(query: str) -> ToolResult:
    kb = {
        "earth": "Earth is the third planet from the Sun, with a diameter of 12,742 km.",
        "moon": "The Moon is Earth's only natural satellite, orbiting at ~384,400 km.",
        "python": "Python is a high-level programming language created by Guido van Rossum in 1991.",
        "agent": "An AI agent perceives its environment and takes actions to achieve goals.",
        "react": "ReAct interleaves reasoning traces with tool-use actions for grounded decisions.",
        "gpu": "A GPU (Graphics Processing Unit) accelerates parallel computation.",
        "deepseek": "DeepSeek is a Chinese AI company known for DeepSeek-V3 and DeepSeek-R1 models.",
    }
    for key, value in kb.items():
        if key in query.lower():
            return ToolResult(True, value)
    return ToolResult(False, "", f"No results for '{query}'")


# --- Toy reasoning (default) ---


def reason_toy(state: AgentState, goal: str) -> tuple[str, str | None]:
    if state.steps == 0:
        return "search", goal.split()[0]
    combined = " ".join(state.observations).lower()
    if state.steps >= 3 or "python" in combined or "language" in combined:
        return "done", None
    return "search", goal.split()[0]


# --- LLM-based reasoning (--use-api) ---


def reason_llm(client, state: AgentState, goal: str, model: str) -> tuple[str, str | None]:
    from scripts.llm_client import chat

    tools_desc = """Available tools:
- search(query: str) — search a knowledge base for facts
- calculator(expr: str) — evaluate a math expression
- done() — task is complete, no more actions needed"""

    history = "\n".join(state.observations[-5:]) if state.observations else "(no observations yet)"

    prompt = f"""You are a ReAct agent. Your goal is: "{goal}"

{tools_desc}

Previous observations:
{history}

Step {state.steps + 1}: Think about what to do next. Reply with EXACTLY one line in this format:
THOUGHT: <your reasoning>
ACTION: <tool_name>
ARGS: <json arguments>

If you have enough information to answer, use ACTION: done with ARGS: {{}}.

Examples:
THOUGHT: I need to learn about Python, so I should search.
ACTION: search
ARGS: {{"query": "python"}}

THOUGHT: I now have the answer about Python.
ACTION: done
ARGS: {{}}"""

    response = chat(
        client,
        prompt,
        model=model,
        system="You are a precise ReAct agent. Always respond in the exact format specified.",
    )
    if response.startswith("[API Error") or response.startswith("[Toy mode]"):
        return "done", None

    action = "done"
    args_str = "{}"

    for line in response.split("\n"):
        line = line.strip()
        if line.upper().startswith("THOUGHT:"):
            pass
        elif line.upper().startswith("ACTION:"):
            action = line.split(":", 1)[1].strip().lower()
        elif line.upper().startswith("ARGS:"):
            args_str = line.split(":", 1)[1].strip()

    try:
        args = json.loads(args_str)
    except json.JSONDecodeError:
        args = {}

    arg_value = list(args.values())[0] if args else None
    return action, arg_value


def react_loop(
    goal: str, max_steps: int, verbose: bool, client=None, model: str = "deepseek-chat"
) -> AgentState:
    state = AgentState(goal=goal)
    use_llm = client is not None

    for _ in range(max_steps):
        state.steps += 1

        if use_llm:
            action, arg = reason_llm(client, state, goal, model)
        else:
            action, arg = reason_toy(state, goal)

        if verbose:
            print(f"\n--- Step {state.steps} ---")
            print(f"  Thought: [{'LLM' if use_llm else 'toy'}] I should {action}")

        if action in ("done", "finish", "stop"):
            if verbose:
                print("  Action: DONE")
            state.done = True
            break

        if action == "search":
            query = str(arg) if arg else goal.split()[0]
            result = tool_search(query)
            obs = f"search('{query}'): {result.content}"
            state.observations.append(obs)
            if verbose:
                print(f"  Action: search('{query}')")
                print(f"  Observation: {result.content if result.success else result.error}")

        elif action == "calculator":
            expr = str(arg) if arg else "2+2"
            result = tool_calculator(expr)
            obs = f"calc('{expr}'): {result.content}"
            state.observations.append(obs)
            if verbose:
                print(f"  Action: calc('{expr}')")
                print(f"  Observation: {result.content if result.success else result.error}")

    if verbose:
        print(
            f"\nFinal: steps={state.steps}, done={state.done}, mode={'LLM' if use_llm else 'toy'}"
        )
    return state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ReAct agent — toy or real LLM mode.")
    parser.add_argument("--scenario", choices=["calculator", "search", "both"], default="search")
    parser.add_argument("--max-steps", type=int, default=5)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--use-api", action="store_true", help="Use DeepSeek API instead of toy reasoning"
    )
    parser.add_argument(
        "--model",
        default="deepseek-v4-flash",
        help="Model: deepseek-v4-flash (fast) or deepseek-v4-pro (powerful)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_steps < 1:
        raise SystemExit("--max-steps must be >= 1")

    client = None
    if args.use_api:
        from scripts.llm_client import get_client

        client = get_client()
        if client is None:
            print("⚠️  API mode requested but no client available.", file=sys.stderr)
            print(
                "   Copy agents/.env.example to agents/.env and set DEEPSEEK_API_KEY",
                file=sys.stderr,
            )
            print("   Install: uv sync --extra agents", file=sys.stderr)
            print("   Falling back to toy mode.\n", file=sys.stderr)
            args.use_api = False

    goals = {
        "calculator": "calculate 2+3*4",
        "search": "learn about python",
        "both": "find info about earth and calculate 10*5",
    }
    goal = goals[args.scenario]
    _ = react_loop(goal, args.max_steps, args.verbose, client, args.model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
