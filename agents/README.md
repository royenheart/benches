# Agent 学习专题

从零开始掌握 AI Agent 开发与工程的完整学习路径。章节按**业界 Agent 系统架构分层**组织：自底向上从模型接口走到应用形态，每一层解决一类工程问题，层间通过协议与契约连接。

每个子目录是一个独立专题，包含 notebooks、scripts 和 README，遵循统一的目录约定。

## 架构分层地图

```text
┌─ L0 模型接口 ──────────────────────────────────────────────
│  context-engineering/ 上下文工程：token 预算 / compaction / 缓存
├─ L1 Agent 运行时（单个 agent 的本体）────────────────────────
│  agent-runtime/       循环与工具契约 / Skills / Harness（运行时基座）
│  planning/            规划与搜索：任务分解 / ToT / ReWOO
│  memory/              记忆系统：工作/短期/长期 / RAG / Reflexion
├─ L2 连接与协议 ────────────────────────────────────────────
│  protocols/           连接层协议族：MCP(↔工具) / A2A(↔agent) / ACP(↔编辑器) / AG-UI(↔UI)
├─ L3 编排与协作（控制面）────────────────────────────────────
│  orchestration/       协作模式 / 框架风格 / 状态机形态 / 工作流引擎 / 统一 YAML / 审批 / Temporal
├─ L4 工程化与生产 ──────────────────────────────────────────
│  evaluation/          评估：LLM-as-Judge / Benchmark / 轨迹
│  safety/              安全：OWASP / Prompt Injection / Guardrails
│  production/          生产化：Tracing / 部署模式 / 成本
├─ L5 应用形态与前沿 ────────────────────────────────────────
│  frontiers/           Coding Agents / Computer Use / Browser Agents
│  deep-research/       Thinking 模式 / 研究循环 / 报告评估
└─ 预留：执行环境层（沙箱隔离 / 浏览器 / computer use ↔ cloud-agent L1）
```

分层依据与云侧架构一致（对照 MaintainAll `docs/cloud-agent-design.md`：其 "Layer 3: agent orchestration & control plane" 即本图的 L3，协作拓扑与调度引擎同层）。同一概念只在唯一一层有所有者——四种连接协议统一归 protocols，协作模式与状态机形态归 orchestration，循环本体与工具契约归 agent-runtime，DAG 的"规划"义归 planning、"执行"义归 orchestration。

## 专题列表

### L0 模型接口

| # | 专题 | 目录 | 核心内容 |
|---|------|------|----------|
| 1 | Context Engineering | `context-engineering/` | Token 预算、Compaction、上下文隔离、Prompt Caching |

### L1 Agent 运行时

| # | 专题 | 目录 | 核心内容 |
|---|------|------|----------|
| 2 | Agent 运行时：循环、工具契约与 Harness | `agent-runtime/` | 最小循环与 ReAct、tool-call 合同、Progressive Disclosure、Claude Code 式 Harness、自建 Skill 系统；附 toy→生产差距清单 |
| 3 | 规划与搜索 | `planning/` | 任务分解、DAG 依赖、Tree of Thoughts、搜索策略、ReWOO |
| 4 | 记忆系统 | `memory/` | 工作记忆、长期记忆、RAG、情节反射、Reflexion 模式；`papers/` 41 篇论文精读（奠基→共享组织→腐化投毒→ADR→云端架构，原文核对+证据等级标注） |

### L2 连接与协议

| # | 专题 | 目录 | 核心内容 |
|---|------|------|----------|
| 5 | Agent 连接与协议 | `protocols/` | 协议族全景：MCP（agent↔工具，实现深挖）、A2A v1 三种绑定、Zed ACP stdio、AG-UI 事件流、组合选型——从概念到线上字节 |

### L3 编排与协作（控制面）

| # | 专题 | 目录 | 核心内容 |
|---|------|------|----------|
| 6 | 编排与协作：控制面 | `orchestration/` | 角色分工/Planner-Worker/Debate（原 multi-agent/）、框架风格对比（原 frameworks/）、状态机形态、工作流引擎格局、统一 YAML、审批/HITL、Temporal、运行账本 |

### L4 工程化与生产

| # | 专题 | 目录 | 核心内容 |
|---|------|------|----------|
| 7 | Agent 评估 | `evaluation/` | LLM-as-Judge、SWE-bench、GAIA、轨迹评估、Benchmark 设计 |
| 8 | Agent 安全 | `safety/` | OWASP Top 10 for LLM、Prompt Injection、Guardrails、Sandboxing |
| 9 | Agent 生产化 | `production/` | Observability、LangFuse/Phoenix/Tracing、部署模式、成本管理 |

### L5 应用形态与前沿

| # | 专题 | 目录 | 核心内容 |
|---|------|------|----------|
| 10 | Agent 前沿 | `frontiers/` | Coding Agents (SWE-agent)、Computer Use、Browser Agents、Agentic RAG |
| 11 | Deep Research 与推理 | `deep-research/` | Thinking 模式、Test-time Compute、研究循环、报告评估 |

### 相关专题

| 专题 | 位置 | 说明 |
|------|------|------|
| Agent 训练与对齐 | `../accels/agent-rl/` | SFT→DPO→RLHF/GRPO + ReAct/Tool Use/RAG/Multi-Agent |
| 技术全景图 | `LANDSCAPE.md` | 协议/评估/生产/支撑设施的技术选型地图（与本目录互补：LANDSCAPE 按技术族谱，本目录按架构分层） |

## 目录约定

```text
agents/<topic-name>/
├── README.md          # 专题说明、目标、notebook 顺序、scripts 用法、参考资料
├── notebooks/         # 编号的 Jupyter notebook（00_xxx.ipynb, 01_xxx.ipynb, ...）
│   ├── 00_setup_and_concepts.ipynb
│   └── ...
└── scripts/           # 配套 Python 脚本（xxx_demo.py）
```

## 设计取舍

1. **API 优先，toy 保底**：所有专题以 DeepSeek 真实 API 调用为教学主路径（`--use-api` / notebook setup）；无 key 时自动降级为纯标准库 toy 模式，保证离线可运行。
2. **先拆状态机，再谈框架**：每个专题先把核心概念的状态流转和数据契约讲清楚，再引入具体框架。
3. **Notebook 优先**：概念讲解、代码实验和引导式练习都在 notebook 里，scripts 提供可独立运行的 demo。
4. **检查点驱动**：每个关键概念后设「检查点」— 确认理解后再继续。

## 快速开始

```bash
# Toy 模式 — 零依赖，即开即用
python agents/agent-runtime/scripts/react_loop_demo.py --scenario search --verbose

# API 模式 — 接入 DeepSeek 真实推理
cp agents/.env.example agents/.env    # 编辑填入 DEEPSEEK_API_KEY
uv sync --extra agents                # 安装 openai + python-dotenv
python agents/agent-runtime/scripts/react_loop_demo.py --scenario search --use-api --verbose
jupyter notebook agents/agent-runtime/notebooks
```

所有 Toy 模式仅需 Python 标准库。`--use-api` 模式通过 `agents/.env` 读取配置，无需在代码中反复填写 API key。
`agents/.env` 已被 `.gitignore` 排除，不会提交到版本管理。

## 参考资料

### 必读论文（按阶段）

| 阶段 | 论文 | 链接 |
|------|------|------|
| 基础 | Chain-of-Thought Prompting (2022) | [arXiv:2201.11903](https://arxiv.org/abs/2201.11903) |
| 基础 | ReAct: Synergizing Reasoning and Acting (2022) | [arXiv:2210.03629](https://arxiv.org/abs/2210.03629) |
| 基础 | PAL: Program-aided Language Models (2022) | [arXiv:2211.10435](https://arxiv.org/abs/2211.10435) |
| 基础 | Toolformer: LMs Can Teach Themselves to Use Tools (2023) | [arXiv:2302.04761](https://arxiv.org/abs/2302.04761) |
| 进阶 | Reflexion: Language Agents with Verbal RL (2023) | [arXiv:2303.11366](https://arxiv.org/abs/2303.11366) |
| 进阶 | Tree of Thoughts: Deliberate Problem Solving (2023) | [arXiv:2305.10601](https://arxiv.org/abs/2305.10601) |
| 进阶 | CoALA: Cognitive Architectures for Language Agents (2023) | [arXiv:2309.02427](https://arxiv.org/abs/2309.02427) |
| 进阶 | MetaGPT: Multi-Agent Meta Programming (2023) | [arXiv:2308.00352](https://arxiv.org/abs/2308.00352) |
| 进阶 | Generative Agents: Interactive Simulacra (2023) | [arXiv:2304.03442](https://arxiv.org/abs/2304.03442) |
| 实战 | SWE-bench: Can LMs Resolve Real-World GitHub Issues? (2023) | [arXiv:2310.06770](https://arxiv.org/abs/2310.06770) |

### 协议与标准

- **Model Context Protocol (MCP)**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Agent-to-Agent Protocol (A2A)**: [a2a-protocol.org](https://a2a-protocol.org)
- **OWASP Top 10 for LLM Applications 2025**: [genai.owasp.org](https://genai.owasp.org/llm-top-10/)

### 框架文档

- LangGraph: [docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/overview)
- OpenAI Agents SDK: [openai.github.io/openai-agents-python](https://openai.github.io/openai-agents-python/)
- CrewAI: [docs.crewai.com](https://docs.crewai.com/en/concepts/agents)
- AutoGen: [microsoft.github.io/autogen](https://microsoft.github.io/autogen/stable/)
- Google ADK: [google.github.io/adk-docs](https://google.github.io/adk-docs/)
- Smolagents: [huggingface.co/docs/smolagents](https://huggingface.co/docs/smolagents/index)
- Agno: [docs.agno.com](https://docs.agno.com/)
