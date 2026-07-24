# Agent 前沿方向 教学专题

探索 Agent 技术的最前沿：Coding Agents（SWE-agent）、Computer Use（GUI 控制）、Browser Agents、Agentic RAG。

## 目标

1. 理解 SWE-agent 的 agent-computer interface 设计：bash、editor、test runner。
2. 了解 Computer Use 的原理：screenshot → element detection → action prediction。
3. 实现一个 toy Browser Agent：HTML 解析 → link 跟随 → 表单填写。
4. 理解 Agentic RAG：Agent 自主决定何时检索、检索什么、是否需要二次检索。

## 目录结构

```text
agents/frontiers/
├── README.md
├── notebooks/
│   ├── 00_coding_agents.ipynb
│   ├── 01_computer_use.ipynb
│   └── 02_browser_and_agentic_rag.ipynb
└── scripts/
    ├── mini_coding_agent.py
    └── toy_browser_agent.py
```

## 快速开始

```bash
python agents/frontiers/scripts/mini_coding_agent.py --task find-bug --max-attempts 3 --verbose
python agents/frontiers/scripts/toy_browser_agent.py --task navigate --verbose
# API mode
python agents/frontiers/scripts/mini_coding_agent.py --task find-bug --use-api --verbose
python agents/frontiers/scripts/toy_browser_agent.py --task fill-form --use-api --verbose
jupyter notebook agents/frontiers/notebooks
```

## Notebook 顺序

### 00. Coding Agents

- SWE-agent 架构：agent-computer interface（bash、edit、submit）。
- mini-SWE-agent 的极简设计：~100 行 Python，65% SWE-bench verified。
- 实现一个 mini coding agent：read file → identify bug pattern → edit → verify test。
- 练习：给 agent 添加一个新工具（grep），扩展其能力。

### 01. Computer Use 与 GUI Agent

- Computer Use 的 pipeline：screenshot → vision model → element bbox → action (click/type/scroll)。
- 文本 UI 模拟：用 ASCII grid 表示 UI layout，Agent 解析坐标执行操作。
- OSWorld benchmark：多步 GUI 任务，当前 SOTA &lt;50%。
- 安全挑战：Agent 能看到屏幕上的密码、通知、其他应用内容。

### 02. Browser Agent 与 Agentic RAG

- Browser Agent：DOM 解析 → 语义元素定位 → 导航/填写/提取。
- Agentic RAG：self-querying、adaptive retrieval、multi-hop RAG。
- Agent 决策：用自己的 memory 回答 vs 检索外部文档 vs 执行多跳检索。
- 练习：设计一个 multi-hop RAG pipeline，Agent 自主选择检索策略。

## 可调参数

- `mini_coding_agent.py`
  - `--task`：find-bug / fix-style / add-test
  - `--max-attempts`：最大尝试次数
  - `--verbose`：打印每次读取/编辑/验证

- `toy_browser_agent.py`
  - `--task`：extract-info / fill-form / navigate
  - `--max-steps`：最大浏览器操作步数

## 资料入口

- SWE-agent: [github.com/SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent) | NeurIPS 2024
- mini-SWE-agent: [github.com/SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)
- OSWorld: [osworld.university](https://osworld.university/)
- WebVoyager: [arXiv:2401.13919](https://arxiv.org/abs/2401.13919)
- Voyager: [arXiv:2305.16291](https://arxiv.org/abs/2305.16291)
