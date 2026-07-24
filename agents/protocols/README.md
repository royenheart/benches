# Agent 互操作协议 教学专题

MCP 解决 agent↔tool，但 agent↔agent、agent↔user 需要另外的协议：A2A（Agent2Agent）与 AG-UI。本专题用最小实现讲清三者的边界与组合。

## 目标

1. 实现 A2A 的核心交互：Agent Card 发现、Task 生命周期（submitted → working → completed）、JSON-RPC 2.0 消息。
2. 理解 AG-UI 的事件流模型与 HITL（Human-in-the-Loop）审批的中断/恢复机制。
3. 落地选型决策树：MCP（工具）、A2A（跨框架 agent 协作）、AG-UI（前端交互）如何组合。

## 目录结构

```text
agents/protocols/
├── README.md
├── notebooks/
│   ├── 00_a2a_protocol.ipynb
│   ├── 01_ag_ui_and_hitl.ipynb
│   └── 02_protocol_interop.ipynb
└── scripts/
    ├── a2a_pair_demo.py
    └── hitl_approval_demo.py
```

## 快速开始

```bash
# Toy mode — 本地双 agent 走通 A2A 消息流
python agents/protocols/scripts/a2a_pair_demo.py --task research --verbose
python agents/protocols/scripts/hitl_approval_demo.py --scenario mixed --auto-approve --verbose

# API mode — 真实 LLM 驱动双 agent 对话
python agents/protocols/scripts/a2a_pair_demo.py --task research --use-api --verbose
jupyter notebook agents/protocols/notebooks
```

## Notebook 顺序

### 00. A2A 协议

- Agent Card：agent 的名片（name、url、skills、capabilities），发现机制的载体。
- Task 生命周期：submitted → working → completed/failed，支持多轮 message 追加。
- 本地起两个 agent（Researcher + Writer），真实 LLM 驱动，通过 A2A 消息协作完成任务。

### 01. AG-UI 与 HITL

- AG-UI 事件流：TEXT_MESSAGE_*、TOOL_CALL_*、STATE_* 等 16 种事件类型。
- HITL 审批流：agent 执行到敏感操作 → interrupt → 人类 approve/reject → resume。
- 中断的本质：序列化 agent 状态，等外部信号后恢复 — 不是「暂停进程」。

### 02. 协议组合与选型

- MCP = agent 的「USB 接口」（接工具/数据）；A2A = agent 的「互联网」（跨框架协作）；AG-UI = agent 的「显示屏/键盘」（与人交互）。
- 组合架构实战：前端 (AG-UI) ↔ orchestrator (A2A) ↔ specialist agents ↔ tools (MCP)。
- 选型决策树 + 常见反模式（用 MCP 做 agent 间通信、用 A2A 接本地工具）。

## 可调参数

- `a2a_pair_demo.py`
  - `--task`：research / translate / summarize
  - `--use-api`：真实 LLM 驱动两个 agent
  - `--verbose`：打印完整 JSON-RPC 消息与 Agent Card

- `hitl_approval_demo.py`
  - `--scenario`：safe / risky / mixed
  - `--auto-approve`：自动批准（CI/notebook 用）；缺省时交互式询问
  - `--use-api`：LLM 决定执行哪些动作

## 资料入口

- A2A Protocol: [a2a-protocol.org](https://a2a-protocol.org) · [GitHub](https://github.com/a2aproject/A2A)
- AG-UI Protocol: [docs.ag-ui.com](https://docs.ag-ui.com/)
- MCP: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- LangGraph HITL (interrupt): [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
