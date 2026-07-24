"""Mini coding agent: read → identify issue → edit → verify.

Toy mode (default): rule-based bug detection.
API mode (--use-api): DeepSeek analyzes code and proposes fixes.
  Setup: cp agents/.env.example agents/.env  # then set DEEPSEEK_API_KEY
  Install: uv sync --extra agents
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import subprocess
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))


def setup_sample_repo() -> str:
    tmp = tempfile.mkdtemp(prefix="mini_swe_")
    with open(os.path.join(tmp, "main.py"), "w") as f:
        f.write(
            """def add(a, b):\n    return a - b  # BUG: should be a + b\n\ndef multiply(a, b):\n    return a * b\n\nif __name__ == "__main__":\n    print(f"2+3 = {add(2, 3)}")\n    print(f"4*5 = {multiply(4, 5)}")\n"""
        )
    with open(os.path.join(tmp, "test_main.py"), "w") as f:
        f.write(
            """from main import add, multiply\nassert add(2, 3) == 5, f"got {add(2, 3)}"\nassert multiply(4, 5) == 20\nprint("OK")\n"""
        )
    return tmp


def find_bug_toy(content: str) -> list[dict]:
    issues = []
    for i, line in enumerate(content.split("\n"), 1):
        if "return a - b" in line and "BUG" in line:
            issues.append(
                {
                    "line": i,
                    "old": "return a - b  # BUG: should be a + b",
                    "new": "return a + b  # FIXED",
                    "desc": "add() uses - instead of +",
                }
            )
    return issues


def find_bug_llm(client, content: str, model: str) -> list[dict]:
    from scripts.llm_client import chat

    prompt = f"""Analyze this Python code for bugs. Return ONLY a JSON array of fixes.
Each fix: {{"old":"exact line to replace","new":"corrected line","desc":"what was wrong"}}

Code:
{content}"""
    resp = chat(client, prompt, model=model, system="You are a precise code reviewer.")
    if resp.startswith("[API Error") or resp.startswith("[Toy mode]"):
        return find_bug_toy(content)
    import json

    try:
        s = resp.find("[")
        e = resp.rfind("]") + 1
        return json.loads(resp[s:e]) if s >= 0 else find_bug_toy(content)
    except Exception:
        return find_bug_toy(content)


def run_tests(repo: str) -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, os.path.join(repo, "test_main.py")],
        capture_output=True,
        text=True,
        cwd=repo,
    )
    return r.returncode == 0, r.stdout.strip()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Mini coding agent — toy or LLM bug detection.")
    p.add_argument("--task", choices=["find-bug"], default="find-bug")
    p.add_argument("--max-attempts", type=int, default=3)
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--use-api", action="store_true")
    p.add_argument("--model", default="deepseek-v4-flash")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    client = None
    if args.use_api:
        from scripts.llm_client import get_client

        client = get_client()
        if client is None:
            print("⚠️  Falling back to toy mode.\n", file=sys.stderr)

    repo = setup_sample_repo()
    if args.verbose:
        print(f"Repo: {repo}\n")

    with open(os.path.join(repo, "main.py")) as f:
        code = f.read()
    if args.verbose:
        print(f"Code:\n{code}")

    issues = find_bug_llm(client, code, args.model) if client else find_bug_toy(code)
    print(f"\nIssues found [{'LLM' if client else 'toy'}]: {len(issues)}")
    for iss in issues:
        print(f"  {iss.get('desc', iss.get('line', '?'))}")

    for iss in issues:
        old = iss.get("old", "")
        new = iss.get("new", "")
        if old and new:
            with open(os.path.join(repo, "main.py")) as f:
                content = f.read()
            if old in content:
                with open(os.path.join(repo, "main.py"), "w") as f:
                    f.write(content.replace(old, new))
                print(f"  ✓ Applied: {old[:40]}... → {new[:40]}...")

    passed, out = run_tests(repo)
    print(f"\n{'✓ PASS' if passed else '✗ FAIL'}: {out}")
    import shutil

    shutil.rmtree(repo)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
