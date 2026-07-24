"""Agent evaluator demo: unit test, schema validation, trajectory scoring."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))


@dataclass
class EvalResult:
    name: str
    passed: bool
    score: float
    details: str


def eval_unit_test() -> EvalResult:
    """Unit-test-style evaluation: assert correctness of tool output."""
    tests = [
        ("2+3*4", 14),
        ("10/2", 5),
        ("(1+2)*(3+4)", 21),
    ]
    passed = 0
    for expr, expected in tests:
        try:
            result = eval(expr, {"__builtins__": {}}, {})
            if abs(result - expected) < 1e-6:
                passed += 1
        except Exception:
            pass
    score = passed / len(tests)
    return EvalResult(
        name="unit_test",
        passed=score == 1.0,
        score=score,
        details=f"{passed}/{len(tests)} test cases passed",
    )


def eval_schema_validation() -> EvalResult:
    """Schema validation: check tool call JSON against expected schema."""
    schema = {
        "type": "object",
        "properties": {
            "tool": {"type": "string", "enum": ["calculator", "search", "weather"]},
            "args": {"type": "object"},
        },
        "required": ["tool", "args"],
    }
    test_cases = [
        ({"tool": "calculator", "args": {"expr": "2+2"}}, True),
        ({"tool": "unknown", "args": {}}, False),  # unknown tool
        ({"args": {}}, False),  # missing tool
        ({"tool": "search", "args": {"query": "test"}}, True),
    ]
    passed = 0
    for data, expected_ok in test_cases:
        is_valid = True
        if not all(k in data for k in schema["required"]):
            is_valid = False
        elif data["tool"] not in schema["properties"]["tool"]["enum"]:
            is_valid = False
        if is_valid == expected_ok:
            passed += 1
    score = passed / len(test_cases)
    return EvalResult(
        "schema", score == 1.0, score, f"{passed}/{len(test_cases)} validations correct"
    )


def eval_trajectory() -> EvalResult:
    """Trajectory evaluation: score a toy agent trace."""
    trace = [
        {"step": 1, "action": "search('python')", "valid": True, "efficient": True},
        {"step": 2, "action": "search('python')", "valid": True, "efficient": False},
        {"step": 3, "action": "search('python history')", "valid": True, "efficient": True},
        {"step": 4, "action": "done", "valid": True, "efficient": True},
    ]
    valid = sum(1 for t in trace if t["valid"])
    efficient = sum(1 for t in trace if t["efficient"])
    score = (valid / len(trace)) * 0.5 + (efficient / len(trace)) * 0.5
    return EvalResult(
        "trajectory",
        score > 0.7,
        score,
        f"valid={valid}/{len(trace)}, efficient={efficient}/{len(trace)}",
    )


def eval_llm_judge(client, model: str) -> EvalResult:
    """LLM-as-Judge: real model scores two candidate answers against a rubric."""
    from scripts.llm_client import chat_json

    question = "Explain why the sky is blue in one sentence."
    candidates = [
        "Rayleigh scattering: air molecules scatter short (blue) wavelengths far more than long (red) ones, so scattered skylight looks blue.",
        "The sky is blue because the ocean reflects onto it, and blue is a calming color chosen by nature.",
    ]
    rubric = "Score each answer 0-10 on: scientific accuracy (weight 2), conciseness (weight 1)."
    scores = []
    for ans in candidates:
        data = chat_json(
            client,
            f"Question: {question}\nAnswer: {ans}\nRubric: {rubric}\n"
            'Return JSON: {"accuracy": int, "conciseness": int, "total": int}',
            model=model,
            system="You are a strict science grader. JSON only.",
        )
        total = data.get("total", 0) if isinstance(data, dict) else 0
        scores.append(total)
    if len(scores) != 2 or scores[0] <= scores[1]:
        return EvalResult("llm-judge", False, 0.0, f"unexpected ranking: {scores}")
    return EvalResult(
        "llm-judge", True, 1.0, f"correct>wrong as expected: {scores[0]} vs {scores[1]}"
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Agent evaluator: unit, schema, trajectory tests.")
    p.add_argument(
        "--eval-type", choices=["unit", "schema", "trajectory", "llm-judge", "all"], default="all"
    )
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
    evaluators = {
        "unit": eval_unit_test,
        "schema": eval_schema_validation,
        "trajectory": eval_trajectory,
    }
    types = (
        list(evaluators.keys()) + (["llm-judge"] if args.eval_type == "all" else [])
        if args.eval_type == "all"
        else [args.eval_type]
    )
    if "llm-judge" in types and client is None:
        print("[SKIP] llm-judge: no API client (use --use-api with agents/.env configured)")
        types = [t for t in types if t != "llm-judge"]

    all_passed = True
    for et in types:
        if et == "llm-judge":
            result = eval_llm_judge(client, args.model)
        else:
            result = evaluators[et]()
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"[{status}] {result.name}: {result.details} (score: {result.score:.2f})")
        if not result.passed:
            all_passed = False

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
