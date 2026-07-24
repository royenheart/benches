# Agent 生产化 教学专题

将 Agent 从笔记本推向生产：可观测性、Tracing、部署模式、成本管理和可靠性工程。

## 目标

1. 实现 span-based tracing：记录 Agent 每一步的 thought、tool call、observation。
2. 掌握三种部署模式：同步 request-response、SSE 流式、后台异步任务。
3. 实现成本控制：token budget、tool-call 限额、rate limiting。
4. 掌握可靠性模式：retry with backoff、circuit breaker、idempotency。

## 目录结构

```text
agents/production/
├── README.md
├── notebooks/
│   ├── 00_observability_and_tracing.ipynb
│   ├── 01_deployment_patterns.ipynb
│   └── 02_cost_and_reliability.ipynb
└── scripts/
    ├── trace_demo.py
    └── cost_manager_demo.py
```

## 快速开始

```bash
python agents/production/scripts/trace_demo.py --scenario research_agent --output console
python agents/production/scripts/cost_manager_demo.py --budget-tokens 1000 --budget-tool-calls 10 --strategy hard-limit
# API mode — 真实 token 计量
python agents/production/scripts/trace_demo.py --use-api --output json
python agents/production/scripts/cost_manager_demo.py --budget-tokens 2000 --use-api --verbose
jupyter notebook agents/production/notebooks
```

## Notebook 顺序

### 00. 可观测性与 Tracing

- Span 模型：trace_id → span_id → parent_id → timestamps → attributes。
- Agent 特有的 span 类型：agent.thought、tool.call、tool.result、agent.output。
- 结构化日志 vs 非结构化日志：JSON Lines + 关键字段设计。
- 练习：为一段 Agent trace 添加过滤和分析逻辑。

### 01. 部署模式

- 同步模式：request → agent.execute() → response（简单，但长时间任务会超时）。
- 流式模式：SSE (Server-Sent Events) 逐 token 推送 + tool call 通知。
- 后台模式：submit task → get task_id → poll status → fetch result。
- Human-in-the-Loop：在不可逆操作前插入审批节点。

### 02. 成本控制与可靠性

- Token budget：per-task 硬限额 + 软警报。
- Tool-call 限额：防止 Agent 陷入循环滥用工具。
- Retry with exponential backoff：区分 transient（网络超时）和 permanent（权限不足）。
- Circuit breaker：连续失败 N 次后熔断，防止雪崩。
- Idempotency keys：确保重试不会重复执行副作用。

## 可调参数

- `trace_demo.py`
  - `--scenario`：research_agent / coding_agent
  - `--output`：json / console

- `cost_manager_demo.py`
  - `--budget-tokens`：token 预算
  - `--budget-tool-calls`：工具调用上限
  - `--strategy`：hard-limit / graceful / warn

## 资料入口

- LangSmith: [docs.langchain.com](https://docs.langchain.com/langsmith)
- LangFuse: [langfuse.com](https://langfuse.com)
- Arize Phoenix: [docs.arize.com](https://docs.arize.com/phoenix)
- OpenTelemetry GenAI: [github.com/open-telemetry/semantic-conventions](https://github.com/open-telemetry/semantic-conventions)
