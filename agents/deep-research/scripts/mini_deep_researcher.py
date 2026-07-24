"""Mini deep researcher: plan → search → synthesize → verify, over a local corpus.

The retrieval layer is local TF-IDF over a small built-in corpus (no external
search API needed); planning, synthesis, and coverage verification are real LLM
calls in --use-api mode. Swap retrieve() for a web search API to go production.

Toy mode (default): keyword sub-question split + template synthesis.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path

# --- Path setup for llm_client ---
_HERE = Path(__file__).resolve().parent
_AGENTS = _HERE.parent.parent
sys.path.insert(0, str(_AGENTS))

# --- Local corpus (stand-in for the web) ---

CORPUS: list[dict] = [
    {
        "id": "D1",
        "title": "Mem0",
        "text": "Mem0 是开源的 agent 记忆层（YC S24）。ADD-only 提取管线：每轮对话提取事实并存入向量库与图存储。LoCoMo 基准 92.5 分。支持 entity linking 与多信号融合检索（dense + BM25 + entity）。",
    },
    {
        "id": "D2",
        "title": "Letta/MemGPT",
        "text": "Letta（原 MemGPT，UC Berkeley）把操作系统的虚拟内存概念搬到 LLM：主上下文是 RAM，外部存储是磁盘，agent 自己决定何时换入换出（paged memory）。学术血统深，面向 continual learning。",
    },
    {
        "id": "D3",
        "title": "Zep",
        "text": "Zep 是基于时序知识图谱的 agent 记忆服务（Context Lake）。自动处理事实失效（temporal invalidation），企业治理功能齐全（SOC 2、HIPAA）。LoCoMo 94.7 分，p95 延迟 168ms。",
    },
    {
        "id": "D4",
        "title": "RAG 与记忆的区别",
        "text": "RAG 检索的是静态文档库，回答「世界是什么样的」；agent 记忆记录的是交互历史，回答「我们经历过什么」。生产系统通常两者都需要：RAG 给知识，memory 给个性化与连续性。",
    },
    {
        "id": "D5",
        "title": "向量数据库选型",
        "text": "agent 记忆的存储层常用 pgvector（已有 Postgres 时零新增运维）、Qdrant（Rust 高性能、边缘部署）、Milvus（十亿级分布式）。Chroma 适合原型。选型先看规模与既有基础设施，再看特性。",
    },
    {
        "id": "D6",
        "title": "记忆的评估",
        "text": "LoCoMo 与 LongMemEval 是 agent 记忆的主流基准。评估维度：事实抽取准确率、时序推理（事实何时失效）、多跳检索。仅靠 dense search 不够，BM25 + entity + temporal 缺一不可。",
    },
    {
        "id": "D7",
        "title": "工作记忆与上下文工程",
        "text": "工作记忆即当前 context window 内的内容。上下文工程（compaction、隔离、caching）管理的是工作记忆；Mem0/Zep 管理的是跨会话的长期记忆。两层都要，瓶颈通常在工作记忆。",
    },
    {
        "id": "D8",
        "title": "Reflexion 与情节记忆",
        "text": "Reflexion 让 agent 把失败经验写成文字反思存入情节记忆，下次遇到类似任务时检索出来避免重蹈覆辙。这是「从经验学习」的最简实现，不需要更新模型权重。",
    },
]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+|[一-鿿]", text.lower())


class TfidfIndex:
    def __init__(self, docs: list[dict]):
        self.docs = docs
        self.df: Counter = Counter()
        self.tf: list[Counter] = []
        for d in docs:
            counts = Counter(tokenize(d["title"] + " " + d["text"]))
            self.tf.append(counts)
            for term in counts:
                self.df[term] += 1

    def search(self, query: str, top_k: int = 2) -> list[dict]:
        n = len(self.docs)
        q_terms = tokenize(query)
        scored = []
        for i, counts in enumerate(self.tf):
            score = 0.0
            for t in q_terms:
                if t in counts:
                    idf = math.log((n + 1) / (self.df[t] + 1)) + 1
                    score += counts[t] * idf
            scored.append((score, i))
        scored.sort(reverse=True)
        return [self.docs[i] for s, i in scored[:top_k] if s > 0]


# --- Research loop stages ---


def plan_toy(question: str) -> list[str]:
    return [question, "主流方案对比", "评估与选型建议"]


def plan_llm(client, model: str, question: str) -> list[str]:
    from scripts.llm_client import chat_json

    data = chat_json(
        client,
        f'研究问题："{question}"\n把它拆成 3 个递进的子问题。返回 JSON: {{"sub_questions": ["...", "...", "..."]}}',
        model=model,
    )
    subs = data.get("sub_questions") if isinstance(data, dict) else None
    return subs if subs else plan_toy(question)


def synthesize_toy(question: str, notes: list[tuple[str, list[dict]]]) -> str:
    lines = [f"# 研究报告：{question}", ""]
    for sub, docs in notes:
        lines.append(f"## {sub}")
        for d in docs:
            lines.append(f"- [{d['id']}] {d['text'][:60]}...")
    return "\n".join(lines)


def synthesize_llm(client, model: str, question: str, notes: list[tuple[str, list[dict]]]) -> str:
    from scripts.llm_client import chat

    material = "\n\n".join(
        f"子问题：{sub}\n" + "\n".join(f"[{d['id']}] {d['text']}" for d in docs)
        for sub, docs in notes
    )
    return chat(
        client,
        f"基于以下检索材料，为研究问题「{question}」写一份 200 字以内的中文报告。\n"
        f"要求：每个论断后用 [D?] 标注来源；最后列「未覆盖」的方面（如有）。\n\n{material}",
        model=model,
        system="你是严谨的研究员。只使用材料中的事实，每个论断必须标注来源。",
        max_tokens=800,
    )


def verify_llm(client, model: str, question: str, report: str) -> str:
    from scripts.llm_client import chat

    return chat(
        client,
        f"研究问题：{question}\n\n报告：\n{report}\n\n评估：1) 覆盖度(0-10) 2) 缺失的方面（一句话）。",
        model=model,
        system="你是苛刻的评审。只输出评分和缺失方面。",
        max_tokens=200,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Mini deep researcher over a local corpus.")
    parser.add_argument("--question", default="agent 记忆系统有哪些主流方案，如何选型")
    parser.add_argument("--rounds", type=int, default=2)
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

    index = TfidfIndex(CORPUS)
    mode = "API" if client else "toy"
    print(f"=== Mini Deep Researcher ({mode}) ===")
    print(f"Question: {args.question}\n")

    # Round 1: plan → search per sub-question
    subs = plan_llm(client, args.model, args.question) if client else plan_toy(args.question)
    print(f"Plan ({len(subs)} sub-questions):")
    for s in subs:
        print(f"  - {s}")

    notes: list[tuple[str, list[dict]]] = []
    for sub in subs:
        hits = index.search(sub, top_k=2)
        notes.append((sub, hits))
        if args.verbose:
            print(f"\n[search] {sub}")
            for h in hits:
                print(f"  [{h['id']}] {h['title']}")

    # Round 2 (optional): a coverage-driven follow-up search
    if args.rounds > 1:
        follow_up = f"{args.question} 评估 选型 基准"  # toy follow-up query
        extra = index.search(follow_up, top_k=2)
        if extra:
            notes.append(("补充检索：评估与选型", extra))
            if args.verbose:
                print(f"\n[round 2] coverage follow-up → {[d['id'] for d in extra]}")

    report = (
        synthesize_llm(client, args.model, args.question, notes)
        if client
        else synthesize_toy(args.question, notes)
    )
    print(f"\n=== Report ===\n{report}\n")

    if client:
        verdict = verify_llm(client, args.model, args.question, report)
        print(f"=== Coverage check ===\n{verdict}\n")

    print(f"Corpus: {len(CORPUS)} docs | sub-questions: {len(notes)} | mode: {mode}")
    print("Takeaway: deep research = RAG 的主动版 — agent 自己决定查什么、查几轮、何时停。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
