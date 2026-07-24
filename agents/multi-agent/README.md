# 多 Agent 协作 教学专题

从单 Agent 到多 Agent 协作：角色分工、Planner-Worker-Critic 模式、Debate 投票共识、共享内存与消息传递。

## 目标

1. 理解多 Agent 系统的核心问题：通信协议、任务分配、冲突解决。
2. 实现 Planner-Worker-Critic 三 Agent 流水线。
3. 实现 Multi-Agent Debate：多轮辩论 + 投票聚合。
4. 对比集中式（Manager）vs 去中心化（Peer-to-Peer）vs 黑板的通信模式。

## 目录结构

```text
agents/multi-agent/
├── README.md
├── notebooks/
│   ├── 00_role_based_agents.ipynb
│   ├── 01_planner_worker_critic.ipynb
│   └── 02_debate_and_voting.ipynb
└── scripts/
    ├── role_team_demo.py
    └── debate_demo.py
```

## 快速开始

```bash
python agents/multi-agent/scripts/role_team_demo.py --team research --scenario "climate impacts" --verbose
python agents/multi-agent/scripts/debate_demo.py --question "Is Python or Rust better for systems programming?" --rounds 3
# API mode
python agents/multi-agent/scripts/role_team_demo.py --use-api --verbose
python agents/multi-agent/scripts/debate_demo.py --use-api --verbose
jupyter notebook agents/multi-agent/notebooks
```

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

## 可调参数

- `role_team_demo.py`
  - `--team`：research / mixed
  - `--scenario`：任务描述
  - `--verbose`：打印每个 Agent 的输出和交互

- `debate_demo.py`
  - `--question`：辩论题目
  - `--agents`：参与 Agent 数量（2-5）
  - `--rounds`：辩论轮数
  - `--strategy`：投票策略（majority / ranked）

## 资料入口

- MetaGPT: [arXiv:2308.00352](https://arxiv.org/abs/2308.00352)
- CAMEL: [arXiv:2303.17760](https://arxiv.org/abs/2303.17760)
- Multiagent Debate: [arXiv:2305.14325](https://arxiv.org/abs/2305.14325)
- ChatDev: [arXiv:2307.07924](https://arxiv.org/abs/2307.07924)
- A2A Protocol: [a2a-protocol.org](https://a2a-protocol.org)
