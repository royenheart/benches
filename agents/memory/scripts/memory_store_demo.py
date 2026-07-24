"""Memory store demo: working memory + long-term TF-IDF retrieval."""

from __future__ import annotations

import argparse
import math
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))


@dataclass
class Memory:
    id: str
    content: str
    tags: list[str] = field(default_factory=list)
    access_count: int = 0


class WorkingMemory:
    """Capacity-limited dict-based store with LRU eviction."""

    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self.store: dict[str, Memory] = {}

    def put(self, mem: Memory) -> None:
        if len(self.store) >= self.capacity and mem.id not in self.store:
            lru = min(self.store.values(), key=lambda m: m.access_count)
            del self.store[lru.id]
        self.store[mem.id] = mem

    def get(self, key: str) -> Memory | None:
        mem = self.store.get(key)
        if mem:
            mem.access_count += 1
        return mem

    def list_all(self) -> list[Memory]:
        return sorted(self.store.values(), key=lambda m: -m.access_count)


class LongTermMemory:
    """TF-IDF retrieval over stored memories."""

    def __init__(self):
        self.docs: list[Memory] = []

    def add(self, mem: Memory) -> None:
        self.docs.append(mem)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return text.lower().replace(".", "").replace(",", "").split()

    def search(self, query: str, top_k: int = 3) -> list[tuple[Memory, float]]:
        if not self.docs:
            return []
        query_tokens = self._tokenize(query)
        N = len(self.docs)
        df: Counter[str] = Counter()
        for doc in self.docs:
            for tok in set(self._tokenize(doc.content)):
                df[tok] += 1

        scores: list[tuple[Memory, float]] = []
        for doc in self.docs:
            doc_tokens = self._tokenize(doc.content)
            tf: Counter[str] = Counter(doc_tokens)
            score = 0.0
            for tok in query_tokens:
                if tok in tf:
                    idf = math.log((N + 1) / (df.get(tok, 0) + 1)) + 1
                    score += tf[tok] * idf
            scores.append((doc, score))

        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Memory store demo with working and long-term memory.")
    p.add_argument("--store-type", choices=["working", "longterm", "both"], default="both")
    p.add_argument("--query", default="agent safety")
    p.add_argument("--capacity", type=int, default=5)
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

    # Seed long-term memory with knowledge base
    ltm = LongTermMemory()
    for i, (tag, content) in enumerate(
        [
            ("agent", "An AI agent perceives its environment and takes actions to achieve goals."),
            (
                "react",
                "ReAct interleaves reasoning traces with tool-use actions for better grounding.",
            ),
            (
                "safety",
                "Agent safety includes prompt injection defense, guardrails, and sandboxing.",
            ),
            (
                "memory",
                "Agent memory systems include working, episodic, semantic, and procedural types.",
            ),
            (
                "rag",
                "RAG retrieves relevant documents to augment the agent's context before generation.",
            ),
            (
                "planning",
                "Task decomposition breaks complex goals into smaller, verifiable subtasks.",
            ),
            (
                "security",
                "OWASP Top 10 for LLM lists prompt injection as the top agent security risk.",
            ),
        ]
    ):
        ltm.add(Memory(id=f"doc_{i}", content=content, tags=[tag]))

    if args.store_type in ("working", "both"):
        wm = WorkingMemory(capacity=args.capacity)
        print(f"Working Memory (capacity={args.capacity}):")
        for i in range(7):
            mem = Memory(id=f"wm_{i}", content=f"Fact {i}: temporary working data")
            wm.put(mem)
            if args.verbose:
                print(f"  Added wm_{i}, store size: {len(wm.store)}")
        print(f"  Final store: {[m.id for m in wm.list_all()]}")
        print()

    if args.store_type in ("longterm", "both"):
        print(f"Long-Term Memory search: '{args.query}'")
        results = ltm.search(args.query, top_k=3)
        for mem, score in results:
            print(f"  [{score:.3f}] {mem.id}: {mem.content[:80]}...")
        print()
        if client is not None and results:
            from scripts.llm_client import chat

            context = "\n".join(f"- {mem.content}" for mem, _ in results)
            grounded = chat(
                client,
                f"Retrieved memories:\n{context}\n\nAnswer using ONLY these memories: {args.query}",
                model=args.model,
                system="You answer strictly from provided memories. If they are insufficient, say so.",
                max_tokens=200,
            )
            ungrounded = chat(client, args.query, model=args.model, max_tokens=200)
            print("RAG answer (grounded in retrieved memories):")
            print(f"  {grounded}\n")
            print("Same question WITHOUT retrieval (for comparison):")
            print(f"  {ungrounded}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
