"""Framework styles demo: same workflow in 4 different framework styles."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))


# --- Raw stdlib style ---


def raw_workflow(scenario: str, verbose: bool) -> str:
    """No framework: just functions and dicts."""
    state = {"goal": scenario, "results": [], "done": False}

    # Research step
    state["results"].append(f"Research: gathered facts about '{scenario}'")
    if verbose:
        print("  [raw] Research done")

    # Summarize step
    summary = f"Summary of '{scenario}': key findings documented."
    state["results"].append(summary)
    if verbose:
        print("  [raw] Summarize done")

    # Review step
    review = "Review: content verified, no errors found."
    state["results"].append(review)
    state["done"] = True
    if verbose:
        print("  [raw] Review done")

    return f"Raw output: {len(state['results'])} steps completed"


# --- Graph style (LangGraph-like) ---


@dataclass
class GraphState:
    goal: str
    research: str = ""
    summary: str = ""
    review: str = ""
    step: str = "research"


def graph_node_research(state: GraphState) -> GraphState:
    state.research = f"Gathered facts about '{state.goal}'"
    state.step = "summarize"
    return state


def graph_node_summarize(state: GraphState) -> GraphState:
    state.summary = f"Summary of '{state.goal}': key findings."
    state.step = "review"
    return state


def graph_node_review(state: GraphState) -> GraphState:
    state.review = "Verified — no errors."
    state.step = "done"
    return state


def graph_workflow(scenario: str, verbose: bool) -> str:
    state = GraphState(goal=scenario)
    nodes = {
        "research": graph_node_research,
        "summarize": graph_node_summarize,
        "review": graph_node_review,
    }
    while state.step != "done":
        prev = state.step
        state = nodes[state.step](state)
        if verbose:
            print(f"  [graph] {prev} → {state.step}")
    return f"Graph output: research='{state.research[:30]}...', summary='{state.summary[:30]}...'"


# --- SDK style (OpenAI Agents SDK-like) ---


@dataclass
class SDKAgent:
    name: str
    instructions: str
    handoff: "SDKAgent | None" = None

    def run(self, input_text: str) -> str:
        return f"[{self.name}] processed: {input_text}"


def sdk_workflow(scenario: str, verbose: bool) -> str:
    research_agent = SDKAgent("researcher", "Gather facts")
    writer_agent = SDKAgent("writer", "Synthesize report")
    reviewer_agent = SDKAgent("reviewer", "Verify accuracy")

    r = research_agent.run(scenario)
    if verbose:
        print(f"  [sdk] {r}")
    w = writer_agent.run(r)
    if verbose:
        print(f"  [sdk] {w}")
    rev = reviewer_agent.run(w)
    if verbose:
        print(f"  [sdk] {rev}")
    return "SDK output: 3 agents completed"


# --- Crew style (CrewAI-like) ---


@dataclass
class CrewTask:
    description: str
    agent: str
    expected_output: str


def crew_workflow(scenario: str, verbose: bool) -> str:
    tasks = [
        CrewTask(f"Research {scenario}", "Researcher", "Fact list"),
        CrewTask("Write report", "Writer", "Markdown report"),
        CrewTask("Review report", "Reviewer", "Approval status"),
    ]
    results = []
    for t in tasks:
        results.append(f"[{t.agent}] {t.description} → {t.expected_output}")
        if verbose:
            print(f"  [crew] {results[-1]}")
    return f"Crew output: {len(results)} tasks done"


# --- Live SDK style: real LLM calls through the OpenAI-compatible API ---


def sdk_live_workflow(scenario: str, client, model: str, verbose: bool) -> str:
    """The sdk_workflow pattern, but each agent is a real LLM call.

    This is what OpenAI Agents SDK does under the hood: instructions → system
    prompt, run() → chat completion, handoff → output becomes next input.
    """
    from scripts.llm_client import chat

    r = chat(
        client,
        scenario,
        model=model,
        system="You are 'researcher'. Gather 3 key facts on the user's topic. Bullets only.",
        max_tokens=300,
    )
    if verbose:
        print(f"  [sdk-live:researcher] {r[:100]}...")
    w = chat(
        client,
        f"Turn these findings into a 2-sentence summary:\n{r}",
        model=model,
        system="You are 'writer'. Crisp prose for a general audience.",
        max_tokens=200,
    )
    if verbose:
        print(f"  [sdk-live:writer] {w[:100]}...")
    rev = chat(
        client,
        f"Fact-check this summary and reply APPROVED or NEEDS-FIX with one reason:\n{w}",
        model=model,
        system="You are 'reviewer'. Strict but fair.",
        max_tokens=200,
    )
    if verbose:
        print(f"  [sdk-live:reviewer] {rev}")
    return f"SDK-live output: 3 real LLM agents completed — reviewer said: {rev[:60]}"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Same 3-step workflow in 4 framework styles.")
    p.add_argument("--style", choices=["raw", "graph", "sdk", "crew", "sdk-live"], default="raw")
    p.add_argument("--scenario", default="research report")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--use-api", action="store_true", help="Use DeepSeek API instead of toy logic")
    p.add_argument("--model", default="deepseek-v4-flash")
    return p.parse_args()


def main() -> int:
    args = parse_args()
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
            print("   Falling back to toy mode.\n", file=sys.stderr)
    workflows = {
        "raw": raw_workflow,
        "graph": graph_workflow,
        "sdk": sdk_workflow,
        "crew": crew_workflow,
    }
    print(f"Style: {args.style}, Scenario: {args.scenario}")
    if args.style == "sdk-live":
        if client is None:
            print("sdk-live requires --use-api with a configured agents/.env")
            return 1
        result = sdk_live_workflow(args.scenario, client, args.model, args.verbose)
    else:
        result = workflows[args.style](args.scenario, args.verbose)
    print(f"\n{result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
