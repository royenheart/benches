# 编排与协作：控制面 教学专题（L3）

agent 之上、系统侧的一切：多 agent **怎么组织**（角色分工、Planner-Worker、Debate）、**用什么实现**（框架风格：raw/graph/sdk/crew）、**被什么执行**（工作流引擎、统一 YAML、审批/HITL、Temporal）、以及贯穿始终的**状态机形态**判断。这一层在 cloud-agent 设计文档里叫 "Layer 3: agent orchestration & control plane"——协作拓扑与调度引擎是同一层的两半，原 `multi-agent/` 与 `frameworks/` 专题均已并入本章。

> 分层定位：**L3 控制面**。连接 agent 的协议（MCP/A2A/ACP/AG-UI、SSE/stdio 线级细节）在 [`../protocols/`](../protocols/README.md)；agent 怎么"规划"任务属于 [`../planning/`](../planning/README.md)——本章的 DAG 是**预定义工作流的执行图**，两者同名不同义。单个 agent 的循环（隐式状态机的家）在 [`../agent-runtime/`](../agent-runtime/README.md)。执行环境（沙箱隔离）层章节规划中，对应 cloud-agent 设计的 L1。

## 目标

1. 多 agent 协作：角色分工与任务契约、Planner-Worker-Critic 流水线、Debate 与投票共识；对比集中式 / 去中心化 / 黑板三种通信模式。
2. 状态机形态判断力：隐式（控制流即状态）/ 显式（状态字段+查表）/ 声明式（依赖图）/ 持久执行（事件溯源），δ 是数据还是代码、转移权在谁手里（[`notes/state-machine-forms.md`](notes/state-machine-forms.md)）。
3. 框架风格：用 raw/graph/sdk/crew 四种风格实现同一工作流，理解 Graph-based、Handoff-based、Role-based 抽象的选型。
4. 工作流引擎：回答"能不能写一份统一 YAML 交给各种框架解析"——盘点各引擎格式，给出所有格式共有的**共同分母**。
5. Temporal 与 HITL：durable execution（事件历史重放）、审批 = Signal；审批在协议层（A2A `INPUT_REQUIRED`）、UI 层（AG-UI `TOOL_CALL`）、引擎层（Pause/approval/suspend）的不同形态。

## 目录结构

```text
agents/orchestration/
├── README.md
├── notes/
│   └── state-machine-forms.md          # 状态机形态对比（四种写法 + 转移权 + 阅读路径）
├── notebooks/
│   ├── 00_role_based_agents.ipynb      # 角色分工与任务契约（原 multi-agent/ 00）
│   ├── 01_planner_worker_critic.ipynb  # Planner-Worker-Critic 流水线
│   ├── 02_debate_and_voting.ipynb      # Debate 与投票共识
│   ├── 03_framework_landscape.ipynb    # 为什么需要框架：抽象光谱（原 frameworks/ 00）
│   ├── 04_langgraph_and_openai_sdk.ipynb
│   ├── 05_crewai_autogen_adk.ipynb
│   └── 06_workflow_dsl_temporal.ipynb  # 统一 YAML demo（含 incident-response）+ Temporal 对照
├── scripts/
│   ├── role_team_demo.py               # 角色团队 demo（research / mixed）
│   ├── debate_demo.py                  # 多轮辩论 + 投票聚合
│   ├── framework_styles_demo.py        # 同一工作流的 4 种框架风格（raw/graph/sdk/crew + sdk-live）
│   ├── decision_helper.py              # 框架选型决策辅助
│   ├── workflow_dsl_demo.py            # 一份文档 → mini 引擎执行 + 三引擎翻译（stdlib）
│   └── temporal_agent_workflow.py      # Temporal 审批工作流参考（需 temporalio）
├── examples/
│   └── incident-response/              # 同一份工作流的六种写法（共同分母/Kestra/Windmill/Argo/GHA）
└── images/
    ├── fig3_workflow_landscape.png     # 统一 YAML 格局 + Temporal 定位
    └── gen_figures.py
```

## 快速开始

```bash
# 协作模式
python agents/orchestration/scripts/role_team_demo.py --scenario "climate impacts" --verbose
python agents/orchestration/scripts/debate_demo.py --question "Is Python or Rust better for systems programming?" --rounds 3

# 状态机形态：同一工作流的 4 种风格（先看 notes/state-machine-forms.md）
python agents/orchestration/scripts/framework_styles_demo.py --style graph --scenario "research report" --verbose
python agents/orchestration/scripts/framework_styles_demo.py --style raw --verbose
python agents/orchestration/scripts/decision_helper.py --requirement "durable multi-agent workflows with human approval"

# 工作流引擎（全部 toy demo 仅依赖标准库）
python agents/orchestration/scripts/workflow_dsl_demo.py --auto-approve
python agents/orchestration/scripts/workflow_dsl_demo.py --workflow incident-response --auto-approve
python agents/orchestration/scripts/workflow_dsl_demo.py --show-ports
ls agents/orchestration/examples/incident-response/   # 六种写法对照（README 有逐元素表格）

# Temporal 参考 demo（需要额外环境）
pip install temporalio && temporal server start-dev   # 终端 1
python agents/orchestration/scripts/temporal_agent_workflow.py worker   # 终端 2
python agents/orchestration/scripts/temporal_agent_workflow.py start    # 终端 3

jupyter notebook agents/orchestration/notebooks
```

**注意**：`framework_styles_demo.py` 的 raw/graph/sdk/crew 四种风格为 toy 模拟（不导入实际框架库），目的是理解设计模式；`--style sdk-live --use-api` 提供真实 LLM 的 agent 链。如需真实框架实操：`pip install langgraph openai-agents crewai`（可选，非本专题依赖）。

## Notebook 顺序

### 00. 角色分工 Agent

- 角色定义：researcher（收集事实）、writer（综合报告）、fact-checker（验证）。
- 任务契约：每个角色有明确的 inputs、outputs、acceptance criteria。
- 练习：设计一个软件开发团队的角色分工（PM、Architect、Developer、Tester）。

### 01. Planner-Worker-Critic

- Planner：分解目标为子任务，分配 worker。
- Worker：执行子任务，返回结果。
- Critic：检查结果是否满足标准，决定通过还是反馈修正。
- 对比 Planner-Worker vs Round-Robin vs Hierarchical 三种协作模式。

### 02. Debate 与投票共识

- 3 个 Agent 独立提出方案 → 互相 critique → judge 聚合打分。
- 投票机制：majority vote、ranked choice、weighted voting。
- 辩论的陷阱：群体思维、verbosity bias、position bias。

### 03. 框架全景图

- 为什么需要框架：从 raw loop 到生产级 Agent 的需求演进。
- 抽象光谱：low-level（LangGraph 精确控制）↔ high-level（Agno 一行部署）。
- 用 raw stdlib 实现一个 3-step workflow，对比框架风格代码量。

### 04. LangGraph 与 OpenAI Agents SDK

- LangGraph 风格：State schema → Nodes → Conditional edges → Checkpointer。
- OpenAI SDK 风格：Agent with instructions → Handoff between specialists → Guardrails。
- 同一场景（research → summarize → review）的两种实现对比。

### 05. CrewAI / AutoGen / ADK

- CrewAI 风格：定义 Role（goal + backstory）、Task（context + expected_output）、Crew（process）。
- AutoGen 风格：AssistantAgent → SelectorGroupChat → termination_condition。
- ADK 风格：LlmAgent → SequentialWorkflow → A2A Server。

### 06. 工作流 DSL 与 Temporal

- 统一 YAML：一份 JSON(⊂YAML) 文档真实执行 DAG + 审批门 + 账本，并翻译成 Kestra/OpenFlow/Argo。
- 六种写法对照：`examples/incident-response/`。
- Temporal：workflow-as-code、审批 = Signal、`temporal server start-dev` 本地实验。

## 可调参数

- `role_team_demo.py`
  - `--scenario`：任务描述
  - `--use-api`：真实 LLM 驱动角色团队
  - `--verbose`：打印每个 Agent 的输出和交互

- `debate_demo.py`
  - `--question`：辩论题目
  - `--agents`：参与 Agent 数量（2-5）
  - `--rounds`：辩论轮数
  - `--strategy`：投票策略（majority / ranked）

- `framework_styles_demo.py`
  - `--style`：raw / graph / sdk / crew
  - `--scenario`：场景描述
  - `--verbose`：打印中间状态

- `workflow_dsl_demo.py`
  - `--workflow`：nightly-report / incident-response
  - `--show-ports`：打印 Kestra/OpenFlow/Argo 翻译
  - `--auto-approve`：审批门自动通过

## 框架速览（原 frameworks/ 专题）

| 框架 | 核心抽象 | 多 Agent 模式 | 状态模型 | 部署重点 | 学习曲线 |
|------|----------|---------------|----------|----------|----------|
| LangGraph | StateGraph (nodes/edges) | Subgraphs + Command | Persistent checkpointer | Long-running, durable | 陡峭 |
| OpenAI Agents SDK | Agent + Handoff | Handoff-as-tool | Sessions (SQL/Redis) | OpenAI-native | 低 |
| CrewAI | Role + Task + Crew | Sequential / Hierarchical | Task context + Memory | Business workflows | 中等 |
| AutoGen | Team presets | RoundRobin / Selector / Swarm | Resumable teams | Research collaboration | 中-陡 |
| Google ADK | LlmAgent + Workflows | Sequential/Loop/Parallel + A2A | Sessions + Memory | Enterprise + Cloud | 中等 |
| Smolagents | CodeAgent | Multi-agent step() | Conversation memory | Research / prototyping | 低 |
| Agno | Agent + AgentOS | Teams + Workflows | SqliteDb | FastAPI platform | 低 |

## 核心结论速览

- **统一 YAML**：今天不能整体做到。引擎格式（Kestra/OpenFlow/Argo/n8n/Dify）语法开放语义私有；跨引擎的只有 BPMN 2.0 XML（不 agent-native）与小众的 CNCF Open Workflow DSL；正在收敛的是 agent 定义层（Oracle Agent Spec、MS Agent Framework YAML）。但共同分母足够小：`triggers + steps/needs(DAG) + typed output + retries/timeout + approval 门 + 幂等账本`——自研 workflows.yml 只依赖它，翻译到任何引擎都只是"导出"。
- **Temporal**：workflow-as-code 是 durable execution 的必然（代码必须确定性，故无官方 YAML）；审批 = Signal、状态 = Query；MIT + PostgreSQL + 2GB 即可自托管；2026 年已 GA 的 agent 集成：OpenAI Agents SDK（2026-03）、LangGraph 插件（2026-07）、ADK。网传 "temporal-agent-kit" 查无此物。
- **语义私有**：同一份 intent（如 `retry 3 次间隔 30s`）在 Kestra（ISO-8601 + 类型枚举）、Windmill（秒数 + 布尔）、Argo（backoff factor）、GHA（没有）四种写法互不可执行——`examples/incident-response/README.md` 有四个典型展开。
- **与 cloud-agent 的关系**：本章的协作模式对应设计文档 §9.1 拓扑表（supervisor/handoff/blackboard/swarm）；工作流引擎消费管控面（broker）的分配语义——例子里的 `type: provision` 步骤就是调用 broker 的 `POST /sandboxes`；状态机笔记里的"转移权"原则对应其"LLM 不进触发/转移判断"。

## 检查点

- [ ] 四种状态机形态各说出一个代表系统，并解释为什么隐式形态难 checkpoint。
- [ ] 对比 Planner-Worker 与 Debate：各自的失败模式是什么，什么时候选哪个？
- [ ] 给出一份含审批门的三步工作流，手写它的 Kestra 版与 OpenFlow 版，指出哪些字段在任何引擎里都没有对应物。
- [ ] 为什么 Temporal 把审批建模成 signal 而不是轮询数据库？

## 资料入口

- MetaGPT: [arXiv:2308.00352](https://arxiv.org/abs/2308.00352) · CAMEL: [arXiv:2303.17760](https://arxiv.org/abs/2303.17760) · Multiagent Debate: [arXiv:2305.14325](https://arxiv.org/abs/2305.14325) · ChatDev: [arXiv:2307.07924](https://arxiv.org/abs/2307.07924)
- LangGraph: [docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/overview) · OpenAI Agents SDK: [openai.github.io/openai-agents-python](https://openai.github.io/openai-agents-python/) · CrewAI: [docs.crewai.com](https://docs.crewai.com/en/concepts/agents) · AutoGen: [microsoft.github.io/autogen](https://microsoft.github.io/autogen/stable/) · Google ADK: [google.github.io/adk-docs](https://google.github.io/adk-docs/) · Smolagents: [huggingface.co/docs/smolagents](https://huggingface.co/docs/smolagents/index) · Agno: [docs.agno.com](https://docs.agno.com/)
- 工作流格式: [CNCF Open Workflow](https://www.cncf.io/projects/serverless-workflow/) · [Kestra](https://kestra.io) · [Windmill OpenFlow](https://www.windmill.dev) · [Argo](https://argoproj.github.io/argo-workflows/) · [Oracle Agent Spec](https://github.com/oracle/agent-spec)
- Temporal: [docs.temporal.io](https://docs.temporal.io) · [OpenAI Agents 集成](https://temporal.io/blog/announcing-openai-agents-sdk-integration) · [LangGraph 插件](https://temporal.io/blog/temporal-langgraph-plugin-durable-execution) · [HITL cookbook](https://docs.temporal.io/ai/cookbook/human-in-the-loop-python)
- 上游设计文档: [MaintainAll docs/cloud-agent-design.md](../../../softwares/MaintainAll/docs/cloud-agent-design.md) §9–12
