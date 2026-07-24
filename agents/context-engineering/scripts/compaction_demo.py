"""Compaction demo: full history vs sliding window vs rolling summary.

A scripted 10-turn conversation plants a fact in turn 1 ("power budget: 40W").
The final question requires that fact. Three strategies are compared:
  full   — send everything (expensive, accurate)
  window — last 4 turns only (cheap, loses early facts)
  summary— LLM/extractive summary of old turns + last 2 turns (middle ground)

Toy mode (default): extractive summary + template answers, heuristic token counts.
API mode (--use-api): real summary, real answers, real usage tokens.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# --- Path setup for llm_client ---
_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))

# --- Scripted conversation (turn 1 plants the critical fact) ---

DIALOGUE: list[tuple[str, str]] = [
    (
        "We're designing a cubesat. The solar panels give us a power budget of 40W total.",
        "Noted: 40W total power budget. That constrains every subsystem choice — compute, radio, heaters.",
    ),
    (
        "What OBC should we use?",
        "For 40W total, a Raspberry Pi CM4 (5-7W) leaves margin; a Jetson Nano (10W) is feasible but tight with the radio duty cycle.",
    ),
    (
        "And the radio?",
        "A UHF transceiver at 8W transmit works if you limit downlink windows to 10% duty cycle.",
    ),
    (
        "What about thermal?",
        "In LEO, expect -20°C to +50°C internal. The CM4 is rated 0-70°C, so add a small heater for eclipse phases.",
    ),
    (
        "Can we add a camera?",
        "A 2W camera module fits if imaging sessions are scheduled outside downlink windows.",
    ),
    (
        "Ground station options?",
        "Amateur UHF/VHF stations can work; SatNOGS network is free. For daily passes, budget 2-3 contacts.",
    ),
    (
        "What's the total mass estimate?",
        "A 3U cubesat is typically 4-5 kg: structure 1 kg, OBC+radio 0.8 kg, battery 0.6 kg, payload rest.",
    ),
    (
        "Battery sizing?",
        "With that peak draw and 30% eclipse time, a 60Wh battery gives ~2 orbits of margin.",
    ),
    (
        "Launch options?",
        "Rideshare (SpaceX Transporter) ~$300K for 3U. University programs sometimes get free ESA/NASA slots.",
    ),
    (
        "Final question: given all constraints, can we run a 15W payload continuously? Why or why not?",
        "",
    ),
]

QUESTION = DIALOGUE[-1][0]


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def dialogue_text(turns: list[tuple[str, str]]) -> str:
    return "\n".join(f"User: {u}\nAssistant: {a}" for u, a in turns if a)


# --- Strategies ---


def build_full() -> str:
    return dialogue_text(DIALOGUE[:-1])


def build_window(n: int = 4) -> str:
    return dialogue_text(DIALOGUE[-(n + 1) : -1])


def build_summary_toy() -> str:
    """Extractive toy summary: keep sentences with constraint keywords."""
    keywords = ("budget", "40w", "constraint", "noted", "total")
    kept = []
    for u, a in DIALOGUE[:-3]:
        for sent in (u + " " + a).split(". "):
            if any(k in sent.lower() for k in keywords):
                kept.append(sent.strip())
    return (
        "SUMMARY OF EARLIER DISCUSSION:\n"
        + "\n".join(f"- {k}" for k in kept[:8])
        + "\n\nRECENT:\n"
        + dialogue_text(DIALOGUE[-3:-1])
    )


def build_summary_api(client, model: str) -> str:
    from scripts.llm_client import chat

    old = dialogue_text(DIALOGUE[:-3])
    summary = chat(
        client,
        f"Summarize this engineering discussion. Preserve ONLY: hard constraints (numbers, budgets), decisions made, and open issues. Drop chit-chat. Under 120 words.\n\n{old}",
        model=model,
        system="You are a precise technical summarizer. Output bullet points only.",
    )
    return f"SUMMARY OF EARLIER DISCUSSION:\n{summary}\n\nRECENT:\n{dialogue_text(DIALOGUE[-3:-1])}"


def answer_toy(context: str) -> str:
    if "40W" in context or "40w" in context:
        return (
            "No. A 15W continuous payload against the 40W total budget leaves only 25W for OBC (5-7W), "
            "radio (8W transmit), heaters, and battery charging — with no margin for eclipse. "
            "Duty-cycling the payload (e.g., 50%) would fit."
        )
    return (
        "Insufficient context: I don't have the power budget figure in what I can see, "
        "so I can't determine whether 15W continuous fits. (This is the failure mode of naive truncation.)"
    )


ANSWER_SYSTEM = (
    "You are the assistant in this conversation. Answer using the facts in the provided context; "
    "simple arithmetic on provided numbers is expected. If a needed fact is genuinely missing, "
    "say so explicitly."
)


def answer_prompt(context: str) -> str:
    return f"Here is the conversation so far:\n\n{context}\n\nAnswer the final question: {QUESTION}"


def answer_api(client, model: str, context: str) -> str:
    from scripts.llm_client import chat

    return chat(
        client,
        answer_prompt(context),
        model=model,
        system=ANSWER_SYSTEM,
    )


STRATEGIES = ("full", "window", "summary", "all")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare context compaction strategies.")
    parser.add_argument("--strategy", choices=STRATEGIES, default="all")
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
                "⚠️  No API client (check agents/.env). Falling back to toy mode.\n",
                file=sys.stderr,
            )

    selected = ("full", "window", "summary") if args.strategy == "all" else (args.strategy,)
    print(f"Question: {QUESTION}")
    print(f"Critical fact location: turn 1 of {len(DIALOGUE) - 1} ('40W power budget')\n")

    for name in selected:
        if name == "full":
            context = build_full()
        elif name == "window":
            context = build_window()
        else:
            context = build_summary_api(client, args.model) if client else build_summary_toy()

        if client:
            # Measure real prompt tokens with a 1-token probe carrying the exact
            # messages the answer call bills, then answer for real.
            probe = client.chat.completions.create(
                model=args.model,
                messages=[
                    {"role": "system", "content": ANSWER_SYSTEM},
                    {"role": "user", "content": answer_prompt(context)},
                ],
                max_tokens=1,
            )
            tokens = probe.usage.prompt_tokens
            answer = answer_api(client, args.model, context)
            mode = "API"
        else:
            tokens = estimate_tokens(context + QUESTION)
            answer = answer_toy(context)
            mode = "toy"

        has_fact = "40W" in context or "40w" in context
        print(f"=== Strategy: {name} ({mode}) ===")
        print(f"  Context tokens: {tokens}  | early fact present: {has_fact}")
        print(f"  Answer: {answer[:400]}")
        if args.verbose:
            print(f"  --- context sent ---\n{context[:800]}\n  --- end context ---")
        print()

    print("Takeaway: window is cheapest but amnesiac; full is accurate but pays for every turn;")
    print(
        "summary keeps early constraints at ~1/3 the cost — compaction is a quality/cost dial, not a bug fix."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
