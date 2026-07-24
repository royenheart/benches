"""Toy browser agent: navigate a synthetic mini-web, or real LLM via DeepSeek API.

Toy mode (default): keyword-based navigation rules over a static site graph.
API mode (--use-api): DeepSeek decides each action (click / type / done) from page text.

Pages are plain-text stand-ins for HTML: each page has text content and named links,
teaching the DOM → element → action pipeline without a real browser.
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


# --- Synthetic mini-web (stand-in for DOM) ---

PAGES: dict[str, dict] = {
    "home": {
        "text": "Welcome to MiniShop. We sell books and electronics. Use the catalog to browse.",
        "links": {"catalog": "/catalog", "about": "/about"},
        "forms": {},
    },
    "catalog": {
        "text": "Catalog: [book] Python Cookbook $39 | [book] Deep Learning $59 | [laptop] DevBook Pro $1299",
        "links": {"home": "/home", "cart": "/cart"},
        "forms": {},
    },
    "about": {
        "text": "MiniShop was founded in 2020 in Shanghai. Contact: hello@minishop.example",
        "links": {"home": "/home"},
        "forms": {},
    },
    "cart": {
        "text": "Your cart is empty. Add items from the catalog.",
        "links": {"catalog": "/catalog", "checkout": "/checkout"},
        "forms": {},
    },
    "checkout": {
        "text": "Checkout: please enter your name and email to place the order.",
        "links": {"cart": "/cart"},
        "forms": {"name": "", "email": ""},
    },
}


@dataclass
class BrowserState:
    page: str = "home"
    steps: int = 0
    history: list[str] = field(default_factory=list)
    forms_filled: dict = field(default_factory=dict)
    done: bool = False


def page_view(state: BrowserState) -> str:
    p = PAGES[state.page]
    links = ", ".join(f"'{k}'" for k in p["links"])
    forms = ", ".join(p["forms"]) if p["forms"] else "none"
    return f"PAGE: {state.page}\nTEXT: {p['text']}\nLINKS: {links}\nFORMS: {forms}"


# --- Toy policy (default) ---


def decide_toy(state: BrowserState, task: str) -> dict:
    if task == "navigate":
        order = ["home", "catalog", "about"]
        idx = order.index(state.page) if state.page in order else 0
        if state.steps >= len(order) - 1:
            return {"action": "done"}
        nxt = order[idx + 1]
        return {"action": "click", "target": nxt}
    if task == "extract-info":
        if state.page != "about":
            return {"action": "click", "target": "about"}
        return {"action": "done"}
    if task == "fill-form":
        if state.page != "checkout":
            # Route along actual graph edges (home→catalog→cart→checkout);
            # a plain "cart if page in (home,catalog)" ternary loops forever on cart→cart.
            nxt = {"home": "catalog", "catalog": "cart"}.get(state.page, "checkout")
            return {"action": "click", "target": nxt}
        if "name" not in state.forms_filled:
            return {"action": "type", "field": "name", "value": "Ada Lovelace"}
        if "email" not in state.forms_filled:
            return {"action": "type", "field": "email", "value": "ada@example.com"}
        return {"action": "done"}
    return {"action": "done"}


# --- LLM policy (--use-api) ---


def decide_llm(client, state: BrowserState, task: str, model: str) -> dict:
    from scripts.llm_client import chat

    history = "\n".join(state.history[-6:]) if state.history else "(none)"
    prompt = f"""You are a browser agent. Task: {task}

Current browser view:
{page_view(state)}

Recent actions:
{history}

Decide the next action. Reply with EXACTLY one JSON object on one line:
{{"action": "click", "target": "<link name>"}}
{{"action": "type", "field": "<form field>", "value": "<text>"}}
{{"action": "done"}}

Rules: click targets must come from LINKS; type fields must come from FORMS; use done only when the task is complete."""

    resp = chat(
        client,
        prompt,
        model=model,
        system="You are a precise browser agent. Reply with one JSON object only.",
    )
    if resp.startswith("[API Error") or resp.startswith("[Toy mode]"):
        return {"action": "done"}
    try:
        line = next(ln for ln in resp.split("\n") if ln.strip().startswith("{"))
        return json.loads(line)
    except (StopIteration, json.JSONDecodeError):
        return {"action": "done"}


def apply_action(state: BrowserState, decision: dict, verbose: bool) -> None:
    action = decision.get("action", "done")
    state.steps += 1

    if action == "click":
        target = decision.get("target", "")
        dest = PAGES[state.page]["links"].get(target)
        if dest:
            state.page = dest.lstrip("/")
            state.history.append(f"click('{target}') → {state.page}")
            if verbose:
                print(f"  Action: click('{target}') → page={state.page}")
        else:
            state.history.append(f"click('{target}') FAILED (no such link)")
            if verbose:
                print(f"  Action: click('{target}') FAILED — link not on page")

    elif action == "type":
        field_name = decision.get("field", "")
        value = decision.get("value", "")
        if field_name in PAGES[state.page]["forms"]:
            state.forms_filled[field_name] = value
            state.history.append(f"type('{field_name}', '{value}')")
            if verbose:
                print(f"  Action: type('{field_name}', '{value}')")
        else:
            state.history.append(f"type('{field_name}') FAILED (no such form field)")
            if verbose:
                print(f"  Action: type('{field_name}') FAILED — field not on page")

    else:
        state.done = True
        state.history.append("done")
        if verbose:
            print("  Action: DONE")


def run_agent(
    task: str, max_steps: int, verbose: bool, client=None, model: str = "deepseek-v4-flash"
) -> BrowserState:
    state = BrowserState()
    use_llm = client is not None
    while not state.done and state.steps < max_steps:
        if verbose:
            print(f"\n--- Step {state.steps + 1} [{'LLM' if use_llm else 'toy'}] ---")
            print(page_view(state))
        decision = decide_llm(client, state, task, model) if use_llm else decide_toy(state, task)
        apply_action(state, decision, verbose)
    if verbose:
        print(
            f"\nFinal: steps={state.steps}, done={state.done}, forms={state.forms_filled}, mode={'LLM' if use_llm else 'toy'}"
        )
    return state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Toy browser agent — toy rules or real LLM mode.")
    parser.add_argument(
        "--task", choices=["extract-info", "fill-form", "navigate"], default="navigate"
    )
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--use-api", action="store_true", help="Use DeepSeek API instead of toy rules"
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

    state = run_agent(args.task, args.max_steps, args.verbose, client, args.model)
    return 0 if state.done else 1


if __name__ == "__main__":
    sys.exit(main())
