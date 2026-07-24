# Agent 框架对比 教学专题

系统对比主流 Agent 开发框架：LangGraph、OpenAI Agents SDK、CrewAI、AutoGen、Google ADK。理解每个框架的设计哲学、核心抽象和适用场景，建立选型决策能力。

## 目标

1. 用同一场景在 4 种框架风格下实现，直观感受抽象层次的差异。
2. 理解 Graph-based（LangGraph）、Handoff-based（OpenAI SDK）、Role-based（CrewAI）、Event-driven（AutoGen）四种编程模型。
3. 掌握框架选型决策树：持久化需求？多 Agent 协作？部署平台？学习曲线？

## 目录结构

```text
agents/frameworks/
├── README.md
├── notebooks/
│   ├── 00_framework_landscape.ipynb
│   ├── 01_langgraph_and_openai_sdk.ipynb
│   └── 02_crewai_autogen_adk.ipynb
└── scripts/
    ├── framework_styles_demo.py
    └── decision_helper.py
```

## 快速开始

```bash
python agents/frameworks/scripts/framework_styles_demo.py --style graph --scenario "research report" --verbose
python agents/frameworks/scripts/decision_helper.py --requirement "I need durable multi-agent workflows with human approval"
jupyter notebook agents/frameworks/notebooks
```

**注意**：raw/graph/sdk/crew 四种风格为 toy 模拟（不导入实际框架库），目的是理解设计模式；`--style sdk-live --use-api` 额外提供真实 LLM 的 agent 链（instructions → system prompt，handoff → 输出传递），等价于 OpenAI Agents SDK 的核心机制。如需真实框架实操：`pip install langgraph openai-agents crewai`（可选，非本专题依赖）。

## 框架速览

| 框架 | 核心抽象 | 多 Agent 模式 | 状态模型 | 部署重点 | 学习曲线 |
|------|----------|---------------|----------|----------|----------|
| LangGraph | StateGraph (nodes/edges) | Subgraphs + Command | Persistent checkpointer | Long-running, durable | 陡峭 |
| OpenAI Agents SDK | Agent + Handoff | Handoff-as-tool | Sessions (SQL/Redis) | OpenAI-native | 低 |
| CrewAI | Role + Task + Crew | Sequential / Hierarchical | Task context + Memory | Business workflows | 中等 |
| AutoGen | Team presets | RoundRobin / Selector / Swarm | Resumable teams | Research collaboration | 中-陡 |
| Google ADK | LlmAgent + Workflows | Sequential/Loop/Parallel + A2A | Sessions + Memory | Enterprise + Cloud | 中等 |
| Smolagents | CodeAgent | Multi-agent step() | Conversation memory | Research / prototyping | 低 |
| Agno | Agent + AgentOS | Teams + Workflows | SqliteDb | FastAPI platform | 低 |

## Notebook 顺序

### 00. 框架全景图

- 为什么需要框架：从 raw loop 到生产级 Agent 的需求演进。
- 抽象光谱：low-level（LangGraph 精确控制）↔ high-level（Agno 一行部署）。
- 用 raw stdlib 实现一个 3-step workflow，对比框架风格代码量。

### 01. LangGraph 与 OpenAI Agents SDK

- LangGraph 风格：State schema → Nodes → Conditional edges → Checkpointer。
- OpenAI SDK 风格：Agent with instructions → Handoff between specialists → Guardrails。
- 同一场景（research → summarize → review）的两种实现对比。

### 02. CrewAI / AutoGen / ADK

- CrewAI 风格：定义 Role（goal + backstory）、Task（context + expected_output）、Crew（process）。
- AutoGen 风格：AssistantAgent → SelectorGroupChat → termination_condition。
- ADK 风格：LlmAgent → SequentialWorkflow → A2A Server。

## 可调参数

- `framework_styles_demo.py`
  - `--style`：raw / graph / sdk / crew
  - `--scenario`：场景描述
  - `--verbose`：打印中间状态

- `decision_helper.py`
  - `--requirement`：需求描述文本
  - `--verbose`：打印评分过程

## 资料入口

- LangGraph: [docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/overview)
- OpenAI Agents SDK: [openai.github.io/openai-agents-python](https://openai.github.io/openai-agents-python/)
- CrewAI: [docs.crewai.com](https://docs.crewai.com/en/concepts/agents)
- AutoGen: [microsoft.github.io/autogen](https://microsoft.github.io/autogen/stable/)
- Google ADK: [google.github.io/adk-docs](https://google.github.io/adk-docs/)
- Smolagents: [huggingface.co/docs/smolagents](https://huggingface.co/docs/smolagents/index)
- Agno: [docs.agno.com](https://docs.agno.com/)
