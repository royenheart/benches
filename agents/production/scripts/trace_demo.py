"""Trace demo: structured span-based observability for agent execution."""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))


@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_id: str | None
    name: str
    start_ms: float
    end_ms: float = 0.0
    attributes: dict = field(default_factory=dict)


class Tracer:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.spans: list[Span] = []
        self._counter = 0

    def start_span(self, name: str, parent_id: str | None = None) -> Span:
        self._counter += 1
        span = Span(
            trace_id=self.trace_id,
            span_id=f"span_{self._counter}",
            parent_id=parent_id,
            name=name,
            start_ms=time.time() * 1000,
        )
        return span

    def end_span(self, span: Span, attributes: dict | None = None):
        span.end_ms = time.time() * 1000
        if attributes:
            span.attributes.update(attributes)
        self.spans.append(span)


def simulate_agent_run(scenario: str, verbose: bool) -> Tracer:
    tracer = Tracer(trace_id="trace_001")

    root = tracer.start_span("agent.run")
    if verbose:
        print(f"[trace] {root.span_id}: {root.name} started")

    # Thought
    thought = tracer.start_span("agent.thought", root.span_id)
    tracer.end_span(thought, {"content": f"Analyzing: {scenario}"})
    if verbose:
        print(
            f"  [trace] {thought.span_id}: {thought.name} ({(thought.end_ms - thought.start_ms):.0f}ms)"
        )

    # Tool call
    tool = tracer.start_span("tool.call", root.span_id)
    tracer.end_span(tool, {"tool": "search", "args": scenario, "success": True})
    if verbose:
        print(f"  [trace] {tool.span_id}: {tool.name} ({(tool.end_ms - tool.start_ms):.0f}ms)")

    # Tool result
    result = tracer.start_span("tool.result", tool.span_id)
    tracer.end_span(result, {"content_length": 42, "status": "ok"})
    if verbose:
        print(f"    [trace] {result.span_id}: {result.name}")

    # Output
    output = tracer.start_span("agent.output", root.span_id)
    tracer.end_span(output, {"tokens": 150, "status": "complete"})
    if verbose:
        print(f"  [trace] {output.span_id}: {output.name}")

    tracer.end_span(root, {"total_tokens": 350, "tool_calls": 1, "status": "success"})
    if verbose:
        print(
            f"[trace] {root.span_id}: complete ({(root.end_ms - root.start_ms):.0f}ms, {len(tracer.spans)} spans)"
        )

    return tracer


def live_agent_run(scenario: str, client, model: str, verbose: bool) -> Tracer:
    """Same span tree, but agent.thought / agent.output wrap a REAL LLM call.

    Tokens and latency come from the actual API response, not constants.
    """
    from scripts.llm_client import chat

    tracer = Tracer(trace_id="trace_live_001")
    root = tracer.start_span("agent.run")
    if verbose:
        print(f"[trace] {root.span_id}: {root.name} started")

    thought = tracer.start_span("agent.thought", root.span_id)
    plan = chat(
        client,
        f"Plan one web search query for: {scenario}. Reply with the query only.",
        model=model,
        max_tokens=50,
    )
    tracer.end_span(thought, {"content": plan[:100], "llm_call": True})
    if verbose:
        print(
            f"  [trace] {thought.span_id}: {thought.name} ({(thought.end_ms - thought.start_ms):.0f}ms)"
        )

    tool = tracer.start_span("tool.call", root.span_id)
    tracer.end_span(tool, {"tool": "search", "args": plan[:60], "success": True, "simulated": True})
    if verbose:
        print(f"  [trace] {tool.span_id}: {tool.name} ({(tool.end_ms - tool.start_ms):.0f}ms)")

    output = tracer.start_span("agent.output", root.span_id)
    t0 = time.time()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": f"Write a one-line summary about: {scenario}"}],
        max_tokens=100,
    )
    usage = resp.usage
    tracer.end_span(
        output,
        {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
            "latency_ms": (time.time() - t0) * 1000,
            "status": "complete",
        },
    )
    if verbose:
        print(f"  [trace] {output.span_id}: {output.name} (real tokens: {usage.total_tokens})")

    tracer.end_span(root, {"status": "success", "spans": len(tracer.spans) + 1})
    if verbose:
        print(f"[trace] {root.span_id}: complete ({(root.end_ms - root.start_ms):.0f}ms)")
    return tracer


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Trace demo: structured span-based observability.")
    p.add_argument("--scenario", default="research agent")
    p.add_argument("--output", choices=["json", "console"], default="console")
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
    if args.use_api and client is not None:
        tracer = live_agent_run(args.scenario, client, args.model, args.output == "console")
    else:
        tracer = simulate_agent_run(args.scenario, args.output == "console")

    if args.output == "json":
        spans_json = [
            {
                "trace_id": s.trace_id,
                "span_id": s.span_id,
                "parent_id": s.parent_id,
                "name": s.name,
                "duration_ms": s.end_ms - s.start_ms,
                "attributes": s.attributes,
            }
            for s in tracer.spans
        ]
        print(json.dumps(spans_json, indent=2))
    else:
        total_duration = sum(s.end_ms - s.start_ms for s in tracer.spans)
        print(f"\nTrace summary: {len(tracer.spans)} spans, {total_duration:.0f}ms total duration")

    return 0


if __name__ == "__main__":
    sys.exit(main())
