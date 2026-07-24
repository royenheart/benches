# Agent 学习专题

从零开始掌握 AI Agent 开发与工程的完整学习路径。覆盖 Agent 基础范式、规划与搜索、记忆系统、多 Agent 协作、MCP 协议、框架选型、评估、安全、生产化与前沿方向的渐进式课程。

每个子目录是一个独立专题，包含 notebooks、scripts 和 README，遵循与 `accels/` 统一的目录约定。

## 学习路线

```text
Phase 1 — 基础               Phase 2 — 工程               Phase 3 — 实战
───────────────────────────────────────────────────────────────────────────
paradigms/ ─────────────────> mcp/ ──────────────────> safety/
   Agent 是什么?                 MCP 协议与 Tool Server       OWASP 威胁建模
   ReAct 循环                    资源与 Prompt 管理             Guardrails 接入
   Plan-Act 模式                                            Prompt Injection 防御
   Tool Use / Function Calling

planning/ ──────────────────> multi-agent/ ────────────> production/
   任务分解                      角色分工                      可观测性
   Tree of Thoughts              Planner-Worker               部署模式
   搜索与回溯                    Debate & Critique            成本管理
                                 投票与共识

memory/ ────────────────────> evaluation/ ──────────────> frontiers/
   短期/长期记忆                  LLM-as-Judge                 Coding Agents
   RAG 检索增强                  SWE-bench 等基准              Computer Use
   情节记忆与反思                  轨迹评估                      Browser Agents

                               frameworks/ ──────────────>
                                 LangGraph / OpenAI SDK
                                 CrewAI / AutoGen / ADK
                                 框架选型决策树

context-engineering/          protocols/                   deep-research/
   Token 预算与测量              A2A 协议                     Thinking 模式
   Compaction 与摘要            AG-UI 与 HITL               Deep Research 模式
   上下文隔离与缓存              MCP+A2A 组合                 研究报告评估

agent-skills/
   Progressive Disclosure
   Harness 设计（subagents/hooks）
   自建 Skill 系统
```

## 专题列表

### Phase 1 — 基础范式

| # | 专题 | 目录 | 核心内容 |
|---|------|------|----------|
| 1 | Agent 范式从零到一 | `paradigms/` | Agent 心智模型、ReAct 循环、Plan-Act、Tool Use、Function Calling |
| 2 | 规划与搜索 | `planning/` | 任务分解、DAG 依赖、Tree of Thoughts、搜索策略、ReWOO |
| 3 | 记忆系统 | `memory/` | 工作记忆、长期记忆、RAG、情节反射、Reflexion 模式 |

### Phase 2 — 工程能力

| # | 专题 | 目录 | 核心内容 |
|---|------|------|----------|
| 4 | MCP 协议与实践 | `mcp/` | MCP 架构、Tool/Resource/Prompt 三层模型、自建 Server |
| 5 | 多 Agent 协作 | `multi-agent/` | 角色分工、Planner-Worker、Critic-Solver、Debate、投票共识 |
| 6 | Agent 框架对比 | `frameworks/` | LangGraph、OpenAI SDK、CrewAI、AutoGen、ADK、选型决策 |
| 7 | Agent 评估 | `evaluation/` | LLM-as-Judge、SWE-bench、GAIA、轨迹评估、Benchmark 设计 |

### Phase 3 — 实战与前沿

| # | 专题 | 目录 | 核心内容 |
|---|------|------|----------|
| 8 | Agent 安全 | `safety/` | OWASP Top 10 for LLM、Prompt Injection、Guardrails、Sandboxing |
| 9 | Agent 生产化 | `production/` | Observability、LangFuse/Phoenix/Tracing、部署模式、成本管理 |
| 10 | Agent 前沿 | `frontiers/` | Coding Agents (SWE-agent)、Computer Use、Browser Agents、Agentic RAG |
| 11 | Context Engineering | `context-engineering/` | Token 预算、Compaction、上下文隔离、Prompt Caching |
| 12 | Agent 互操作协议 | `protocols/` | A2A、AG-UI、HITL 审批流、MCP+A2A 组合架构 |
| 13 | Deep Research 与推理 | `deep-research/` | Thinking 模式、Test-time Compute、研究循环、报告评估 |
| 14 | Agent Skills 与 Harness | `agent-skills/` | Progressive Disclosure、Subagents/Hooks、自建 Skill 系统 |

### 相关专题

| 专题 | 位置 | 说明 |
|------|------|------|
| Agent 训练与对齐 | `../accels/agent-rl/` | SFT→DPO→RLHF/GRPO + ReAct/Tool Use/RAG/Multi-Agent |

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
python agents/paradigms/scripts/react_loop_demo.py --scenario search --verbose

# API 模式 — 接入 DeepSeek 真实推理
cp agents/.env.example agents/.env    # 编辑填入 DEEPSEEK_API_KEY
uv sync --extra agents                # 安装 openai + python-dotenv
python agents/paradigms/scripts/react_loop_demo.py --scenario search --use-api --verbose
jupyter notebook agents/paradigms/notebooks
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
