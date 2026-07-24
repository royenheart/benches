# Context Engineering 教学专题

上下文工程是 2025-2026 年 Agent 工程的核心学科：模型能力相同时，胜负取决于你往 context window 里放了什么、什么时候放、什么时候拿走。

## 目标

1. 建立 token 预算直觉：system prompt、few-shot、tool schema 各占多少 token，用真实 API 的 usage 字段测量。
2. 掌握长对话 compaction：滚动摘要 vs 全量历史 vs 滑动窗口的成本与质量权衡。
3. 理解上下文隔离（sub-agent 只看自己需要的切片）与 prompt caching 的命中条件。

## 目录结构

```text
agents/context-engineering/
├── README.md
├── notebooks/
│   ├── 00_context_window_and_budgets.ipynb
│   ├── 01_compaction_and_summarization.ipynb
│   └── 02_context_isolation_and_caching.ipynb
└── scripts/
    ├── context_budget_demo.py
    └── compaction_demo.py
```

## 快速开始

```bash
# Toy mode — 估算模式（4 chars/token 启发式）
python agents/context-engineering/scripts/context_budget_demo.py --verbose
python agents/context-engineering/scripts/compaction_demo.py --strategy all --verbose

# API mode — 真实 usage 字段测量
python agents/context-engineering/scripts/context_budget_demo.py --use-api --verbose
python agents/context-engineering/scripts/compaction_demo.py --strategy all --use-api --verbose
jupyter notebook agents/context-engineering/notebooks
```

## Notebook 顺序

### 00. Context Window 与 Token 预算

- context window 是稀缺资源：每多 1K token 的成本（钱 + 延迟 + 注意力稀释）。
- 用真实 API usage 字段测量：system prompt / few-shot / tool schema 各占多少。
- 「context rot」现象：长上下文中模型对中间信息的利用率下降。

### 01. Compaction 与摘要

- 三种历史管理策略对比：全量 / 滑动窗口 / 滚动摘要。
- 真实 API 演示：同一问题在三种策略下的回答质量与 token 成本。
- 摘要的信息损失：什么该进摘要（决策、约束、事实），什么该丢（寒暄、中间试错）。

### 02. 上下文隔离与缓存

- Sub-agent 上下文隔离：orchestrator 只把相关切片传给 sub-agent，回收时只拿结论。
- Prompt caching：前缀稳定才能命中；动态内容放尾部。
- Tool result 裁剪：原始返回 vs 摘要返回的 token 对比。

## 可调参数

- `context_budget_demo.py`
  - `--use-api`：用真实 usage 字段替代启发式估算
  - `--verbose`：打印每个组件的内容预览

- `compaction_demo.py`
  - `--strategy`：full / window / summary / all（依次对比全部）
  - `--use-api`：真实摘要与回答
  - `--verbose`：打印每种策略构造的完整 prompt

## 资料入口

- Anthropic: Effective Context Engineering for AI Agents: [anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Lost in the Middle: [arXiv:2307.03172](https://arxiv.org/abs/2307.03172)
- DeepSeek Context Caching: [api-docs.deepseek.com/guides/kv_cache](https://api-docs.deepseek.com/zh-cn/guides/kv_cache)
- MemGPT / Letta (paged context): [arXiv:2310.08560](https://arxiv.org/abs/2310.08560)
