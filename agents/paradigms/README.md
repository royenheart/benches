# Agent 范式 教学专题

从零建立 Agent 心智模型：理解 Agent 与普通 LLM 调用的本质区别，跑通 ReAct 循环、Plan-Act 模式和 Tool Use/Function Calling。

## 目标

1. 理解 Agent = Model + Tools + Loop + State 的核心公式。
2. 用 Python 标准库实现 ReAct 循环，体验「思考→行动→观察」的交替过程。
3. 对比 Plan-Act（先规划后执行）与 ReAct（边想边做）的取舍。
4. 掌握 Tool Use 的核心契约：schema 定义、参数校验、错误处理。

## 目录结构

```text
agents/paradigms/
├── README.md
├── notebooks/
│   ├── 00_what_is_agent.ipynb
│   ├── 01_react_loop.ipynb
│   └── 02_plan_act_and_tool_use.ipynb
└── scripts/
    ├── react_loop_demo.py
    └── plan_act_demo.py
```

## 快速开始

```bash
# Toy mode — 无依赖，即开即用
python agents/paradigms/scripts/react_loop_demo.py --scenario search --verbose

# API mode — 使用 DeepSeek 真实推理
cp agents/.env.example agents/.env    # 编辑填入 DEEPSEEK_API_KEY
uv sync --extra agents
python agents/paradigms/scripts/react_loop_demo.py --scenario search --use-api --verbose
python agents/paradigms/scripts/plan_act_demo.py --goal "build a REST API" --use-api
jupyter notebook agents/paradigms/notebooks
```

Toy 模式用 Python 标准库模拟，适合理解控制流。API 模式接入 DeepSeek，体验真实 Agent 推理。

## Notebook 顺序

### 00. Agent 是什么

- 区分 Model 与 Agent：Agent 多了环境感知、行动能力和状态管理。
- 用纯 Python 实现一个最小 Agent 循环：goal → reason → act → observe → loop。
- 引入 termination condition、error handling、tool validation 概念。

### 01. ReAct 循环

- 运行 `react_loop_demo.py`，观察 ReAct 的 trace 输出。
- 理解 Thought → Action → Observation 三阶段以及 Observation 如何更新状态。
- 对比纯推理（Chain-of-Thought）和 ReAct 在需要外部信息时的差异。

### 02. Plan-Act 与 Tool Use

- 运行 `plan_act_demo.py`，观察先规划后执行的工作流。
- 实现 Tool Schema 定义和 JSON 格式的 Function Calling。
- 对比：什么时候用 Plan-Act（可预测任务）vs ReAct（需要探索的任务）。

## 可调参数

- `react_loop_demo.py`
  - `--scenario`：calculator / search / both
  - `--max-steps`：最大循环步数
  - `--verbose`：打印完整 trace

- `plan_act_demo.py`
  - `--goal`：要分解的目标
  - `--max-retries`：失败重试次数
  - `--parallel`：启用并行执行

## 资料入口

- ReAct: [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)
- Toolformer: [arXiv:2302.04761](https://arxiv.org/abs/2302.04761)
- PAL (Program-aided Language Models): [arXiv:2211.10435](https://arxiv.org/abs/2211.10435)
- CoALA (Cognitive Architectures for Language Agents): [arXiv:2309.02427](https://arxiv.org/abs/2309.02427)

## 设计取舍

**API 优先，toy 保底**。`--use-api` 模式用 DeepSeek 真实推理驱动 ReAct/Plan-Act 循环，是推荐的学习路径；无 key 时自动降级为规则引擎（keyword matching、deterministic planner），便于看清控制流和数据流。两种模式共享同一套循环骨架，差异只在「决策由谁做出」。
