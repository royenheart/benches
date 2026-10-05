# Agent 运行时：循环、工具契约与 Harness（L1 基座）

单个 agent 的本体工程。一个可生产 agent 的最小闭环由五个可替换构件组成——**model**（决策）、**tools**（副作用）、**state**（记忆载体）、**budget**（终止保证）、**loop**（控制流）。本专题自下而上把这层讲成契约：最小循环 → ReAct / Plan-Act → tool-call 合同 → Progressive Disclosure → Claude Code 式 Harness → 自建 Skill 系统。

> 分层定位：L1 运行时基座（原 `paradigms/` 与 `agent-skills/` 已合并为本章）。往上：规划策略 [`../planning/`](../planning/README.md)、记忆 [`../memory/`](../memory/README.md)；往外：连接协议 [`../protocols/`](../protocols/README.md)、编排与状态机形态 [`../orchestration/`](../orchestration/README.md)。隐式状态机的"家"在 00–01（ReAct loop），四种状态机形态的系统对比见 [`../orchestration/notes/state-machine-forms.md`](../orchestration/notes/state-machine-forms.md)。

## 目标

1. 把 Agent = Model + Tools + Loop + State 拆成五个可替换构件，明确每个构件的输入输出契约和替换点。
2. 实现带预算的 ReAct 循环（max_steps、可重试/不可重试错误分类）——"循环会终止"是工程保证，不是默认假设。
3. 掌握 Tool Use 的合同：JSON Schema 定义、参数校验、错误分类（可重试/参数错/权限拒绝）、幂等键——它是 agent 与工具之间的唯一合同，也是 MCP（L2，见本章 00–02）的进程内版本。
4. 理解 Progressive Disclosure 三层加载的工程必然性（metadata 常驻 → instructions 触发时 → resources 用到时；100 个 skill 全量注入 = 100K token）。
5. 解剖 Claude Code 式 Harness：主循环、subagents、hooks（工具调用前后的确定性检查点）、权限模型；并动手自建 Skill 系统验证注入前后的行为差异。

## 目录结构

```text
agents/agent-runtime/
├── README.md
├── notes/
│   └── from-toy-to-production.md      # toy loop → 生产 loop 的差距清单
├── notebooks/
│   ├── 00_what_is_agent.ipynb         # 最小循环：goal → reason → act → observe
│   ├── 01_react_loop.ipynb            # ReAct：Thought → Action → Observation
│   ├── 02_plan_act_and_tool_use.ipynb # Plan-Act 与 tool-call 契约
│   ├── 03_progressive_disclosure.ipynb
│   ├── 04_harness_design.ipynb
│   └── 05_build_a_skill_system.ipynb
├── scripts/
│   ├── react_loop_demo.py
│   ├── plan_act_demo.py
│   ├── skill_loader_demo.py
│   └── mini_harness_demo.py
└── skills/                            # 示例 skill（供 loader 扫描）
    └── unit-converter/
        └── SKILL.md
```

## 快速开始

```bash
# Toy mode — 关键词匹配 + 模板回答，看清控制流
python agents/agent-runtime/scripts/react_loop_demo.py --scenario search --verbose
python agents/agent-runtime/scripts/plan_act_demo.py --goal "build a REST API" --verbose
python agents/agent-runtime/scripts/mini_harness_demo.py --scenario review --verbose

# API mode — 接入 DeepSeek 真实推理
cp agents/.env.example agents/.env    # 编辑填入 DEEPSEEK_API_KEY
uv sync --extra agents
python agents/agent-runtime/scripts/react_loop_demo.py --scenario search --use-api --verbose
python agents/agent-runtime/scripts/skill_loader_demo.py --query "把 5 公里换算成英里" --use-api --verbose
jupyter notebook agents/agent-runtime/notebooks
```

## Notebook 顺序

### 00. Agent 是什么

- 区分 Model 与 Agent：Agent 多了环境感知、行动能力和状态管理。
- 用纯 Python 实现一个最小 Agent 循环：goal → reason → act → observe → loop。
- 引入 termination condition、error handling、tool validation 概念——这是后面所有"契约"的原型。

### 01. ReAct 循环

- 运行 `react_loop_demo.py`，观察 ReAct 的 trace 输出。
- 理解 Thought → Action → Observation 三阶段以及 Observation 如何更新状态。
- 对比纯推理（Chain-of-Thought）和 ReAct 在需要外部信息时的差异；注意这是一个**隐式状态机**（转移权在 LLM 手里）。

### 02. Plan-Act 与 Tool Use

- 运行 `plan_act_demo.py`，观察先规划后执行的工作流。
- 实现 Tool Schema 定义和 JSON 格式的 Function Calling——tool-call 合同的第一次落地。
- 对比的工程维度：Plan-Act（可预测任务，延迟/token 可预算）vs ReAct（探索性任务，可恢复性差）。

### 03. Progressive Disclosure

- 三层加载解剖：扫描时只读 frontmatter（name + description，约 100 token）；触发时才读正文；正文引用的资源文件用到才读。
- 以本仓库 `.agents/skills/` 为活教材：统计每个 skill 的 metadata 与正文 token 量。
- 为什么这是唯一可扩展的方案：100 个 skill 全量注入 = 100K token；三层加载常驻成本 ≈ 10K。

### 04. Harness 设计解剖

- Claude Code 式 harness 的组件：主循环、工具集、subagent 委派、Pre/PostToolUse hooks、slash commands、权限规则。
- Hook 的本质：在工具调用前后插入确定性检查（不经过 LLM）— 安全规则的可靠落点。
- Subagent 的价值：隔离 context（探索性任务的中间噪声不进主 context）。

### 05. 动手：自建 Skill 系统

- 实现 skill loader：扫描 SKILL.md → 解析 frontmatter → LLM 选择 → 注入正文。
- 实验：同一问题，无 skill vs 注入 skill 的回答质量对比（真实 API）。
- 设计自己的 skill：为一个你熟悉的领域写 SKILL.md，验证触发率。

## 可调参数

- `react_loop_demo.py`
  - `--scenario`：calculator / search / both
  - `--max-steps`：最大循环步数
  - `--verbose`：打印完整 trace

- `plan_act_demo.py`
  - `--goal`：要分解的目标
  - `--max-retries`：失败重试次数
  - `--parallel`：启用并行执行

- `skill_loader_demo.py`
  - `--query`：用户问题
  - `--skills-dir`：skill 扫描目录（默认 `agents/agent-runtime/skills`）
  - `--use-api`：LLM 选择 skill + 真实回答

- `mini_harness_demo.py`
  - `--scenario`：review / explore
  - `--use-api`：LLM 驱动主循环与 subagent
  - `--verbose`：打印 hook 拦截与 subagent 委派 trace

## 设计取舍

**API 优先，toy 保底**。`--use-api` 模式用 DeepSeek 真实推理驱动 ReAct/Plan-Act 循环与 skill 选择，是推荐路径；无 key 时自动降级为规则引擎（keyword matching、deterministic planner），便于看清控制流和数据流。两种模式共享同一套循环骨架，差异只在「决策由谁做出」。教学实现与生产实现的差距清单见 [`notes/from-toy-to-production.md`](notes/from-toy-to-production.md)。

## 资料入口

- ReAct: [arXiv:2210.03629](https://arxiv.org/abs/2210.03629) · Toolformer: [arXiv:2302.04761](https://arxiv.org/abs/2302.04761) · PAL: [arXiv:2211.10435](https://arxiv.org/abs/2211.10435) · CoALA: [arXiv:2309.02427](https://arxiv.org/abs/2309.02427)
- Anthropic Agent Skills: [anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) · Claude Code Subagents: [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents) · Hooks: [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)
- 本仓库活教材：`../../.agents/skills/benches-development/SKILL.md`
