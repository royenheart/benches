# Agent 连接与协议 教学专题（连接层）

一个 agent 系统有四条对外边界，每条边界一种协议：**MCP** = agent↔工具，**A2A** = agent↔agent，**Zed ACP** = editor↔编码 agent，**AG-UI** = agent↔用户界面。它们的共同点比差异重要：全都以 JSON-RPC 2.0 为语义核心，区别只在**载体**与**边界**。本章按边界逐个打通，从概念、最小实现一直讲到**线上字节**（真实 HTTP/JSON-RPC/SSE 与真实子进程 stdio），最后给组合选型。

> 分层定位：**连接层（L2）**。协作模式与工作流引擎（控制面）在 [`../orchestration/`](../orchestration/README.md)；进程内的 tool-call 契约（本章 MCP 的 L1 版本）在 [`../agent-runtime/`](../agent-runtime/README.md)。原 `mcp/` 专题已并入本章 00–02。

## 目标

1. MCP：理解 Client-Server 架构与生命周期（initialize → initialized → tools/list → tools/call → shutdown），动手实现 Tool Server（计算/查询工具）、Resource Server（文件内容）、Prompt Templates。
2. 建立协议边界心智：MCP / A2A / ACP / AG-UI 各管哪条边（`images/fig1_protocol_boundaries.png`）。
3. A2A v1：Agent Card 发现、三种传输绑定（JSON-RPC 2.0 / gRPC / REST）、Task 状态机（HITL = 一次状态迁移）、SSE 帧封帧、错误码区间、鉴权模型——跑真实 socket 的 wire demo。
4. Zed ACP：stdio 上的双向 JSON-RPC、initialize 能力握手、"编辑器握有文件系统"的角色反转——跑真实子进程 demo。
5. AG-UI 事件流与 HITL 中断/恢复的概念模型（执行层的审批形态见 orchestration/）。
6. 组合选型：MCP + A2A + AG-UI 的分工、组合架构与反模式。

## 目录结构

```text
agents/protocols/
├── README.md
├── notebooks/
│   ├── 00_mcp_architecture.ipynb      # MCP 架构、生命周期、JSON-RPC 消息
│   ├── 01_tool_server.ipynb           # tools/list + tools/call 实战
│   ├── 02_resources_and_prompts.ipynb # resources 与 prompt templates
│   ├── 03_a2a_protocol.ipynb          # A2A 概念（进程内 toy；形状为 0.x 时代，线级实现见 06）
│   ├── 04_ag_ui_and_hitl.ipynb        # AG-UI 事件流 + HITL 中断/恢复
│   ├── 05_protocol_interop.ipynb      # 协议组合与选型决策树
│   └── 06_wire_protocols.ipynb        # 线级实验：A2A over HTTP/JSON-RPC/SSE + ACP over stdio
├── scripts/
│   ├── mcp_server_demo.py             # MCP server（stdio，calculator/weather/file 工具）
│   ├── mcp_client_demo.py             # MCP client（可独立运行或 --use-api 让 LLM 选工具）
│   ├── a2a_wire_demo.py               # 真实 HTTP+JSON-RPC+SSE（本章线级主路径）
│   ├── acp_stdio_demo.py              # 真实 stdio 子进程 + 双向 JSON-RPC
│   ├── a2a_pair_demo.py               # A2A 概念 toy（进程内；线级以 a2a_wire_demo.py 为准）
│   └── hitl_approval_demo.py          # HITL 中断/恢复概念（工作流引擎中的审批形态见 orchestration/）
└── images/
    ├── fig1_protocol_boundaries.png   # 协议边界地图（谁↔谁、走什么传输）
    └── fig2_a2a_wire.png              # A2A v1 线级时序 + Task 状态机 + 错误模型
```

## 快速开始

```bash
# MCP（stdio 双进程）
python agents/protocols/scripts/mcp_server_demo.py --transport stdio --verbose &
python agents/protocols/scripts/mcp_client_demo.py --tool calculator --args '{"expr": "2+3*4"}'
python agents/protocols/scripts/mcp_client_demo.py --use-api --query "帮我算一下 (12+8)*5"

# 线级主路径（真实 socket / 真实子进程，标准库即可）
python agents/protocols/scripts/a2a_wire_demo.py --verbose
python agents/protocols/scripts/acp_stdio_demo.py --verbose

# 概念 toy（进程内，帮助理解 Task 生命周期与 HITL 中断）
python agents/protocols/scripts/a2a_pair_demo.py --task research --verbose
python agents/protocols/scripts/hitl_approval_demo.py --scenario mixed --auto-approve --verbose

jupyter notebook agents/protocols/notebooks
```

## Notebook 顺序

### 00. MCP 架构模型

- Client-Server 拓扑：一个 Client 连接多个 Server。
- JSON-RPC 2.0 消息格式：request（id + method + params）、response（id + result/error）、notification。
- 生命周期时序图：initialize → initialized → ... → shutdown。
- 动手：用 subprocess 启动一个 server 进程，通过 stdin/stdout 交换 JSON-RPC 消息。

### 01. Tool Server 实战

- 实现 `tools/list`：返回工具列表及 inputSchema。
- 实现 `tools/call`：接收 name + arguments，执行后返回 content（text/image/resource）。
- 三个玩具工具：calculator（安全 eval）、weather（查静态数据）、file_reader（读文件）。
- 错误处理：工具不存在、参数校验失败、执行超时。

### 02. Resources 与 Prompts

- 实现 `resources/list` 和 `resources/read`：暴露文件系统资源。
- 实现 `prompts/list` 和 `prompts/get`：参数化提示词模板。
- 练习：设计一个 code review prompt template，接受 language 和 code 参数。

### 03. A2A 协议

- Agent Card：agent 的名片（name、url、skills、capabilities），发现机制的载体。
- Task 生命周期：submitted → working → completed/failed，支持多轮 message 追加。
- 本地起两个 agent（Researcher + Writer），真实 LLM 驱动，通过 A2A 消息协作完成任务。

### 04. AG-UI 与 HITL

- AG-UI 事件流：TEXT_MESSAGE_*、TOOL_CALL_*、STATE_* 等 16 种事件类型。
- HITL 审批流：agent 执行到敏感操作 → interrupt → 人类 approve/reject → resume。
- 中断的本质：序列化 agent 状态，等外部信号后恢复 — 不是「暂停进程」。

### 05. 协议组合与选型

- MCP = agent 的「USB 接口」（接工具/数据）；A2A = agent 的「互联网」（跨框架协作）；AG-UI = agent 的「显示屏/键盘」（与人交互）。
- 组合架构实战：前端 (AG-UI) ↔ orchestrator (A2A) ↔ specialist agents ↔ tools (MCP)。
- 选型决策树 + 常见反模式（用 MCP 做 agent 间通信、用 A2A 接本地工具）。

### 06. 线级协议（wire protocols）

- A2A v1 真实 socket：Agent Card 发现 → JSON-RPC → SSE 帧（见下方「A2A v1 线级速览」）。
- Zed ACP 真实子进程：stdio 双向 JSON-RPC，编辑器握有文件系统。

## 可调参数

- `mcp_server_demo.py`
  - `--transport`：stdio
  - `--verbose`：打印所有收发的 JSON-RPC 消息
  - `--tools`：暴露哪些工具（calculator/weather/file）

- `mcp_client_demo.py`
  - `--server-cmd`：server 启动命令
  - `--tool`：要调用的工具名
  - `--args`：JSON 格式的工具参数

- `a2a_pair_demo.py`
  - `--task`：research / translate / summarize
  - `--use-api`：真实 LLM 驱动两个 agent
  - `--verbose`：打印完整 JSON-RPC 消息与 Agent Card

- `hitl_approval_demo.py`
  - `--scenario`：safe / risky / mixed
  - `--auto-approve`：自动批准（CI/notebook 用）；缺省时交互式询问
  - `--use-api`：LLM 决定执行哪些动作

- `a2a_wire_demo.py` / `acp_stdio_demo.py`
  - `--verbose`：dump 线上字节（HTTP body / SSE 帧 / stdio JSON 行）

## A2A v1 线级速览（细节在 06 notebook）

- **发现**：`GET /.well-known/agent-card.json`（RFC 8615）；卡片 `supportedInterfaces[]` 声明每种绑定的 URL；没有 `GetAgentCard` 方法，只有带鉴权的 `GetExtendedAgentCard`。
- **三种绑定**：JSON-RPC 2.0 over HTTP（`POST /rpc` + SSE 流，生态最好）／ gRPC（同一 `a2a.proto`，server-streaming）／ HTTP+JSON REST（`/message:send` 等）。
- **响应二选一**：`{"task": …}`（进入任务生命周期）或 `{"message": …}`（直接答复）。
- **SSE 帧**：每个 `data:` 行是一个完整 JSON-RPC envelope，`result` 是 `statusUpdate` / `artifactUpdate` / `task`；读到 EOF = 运行结束。
- **错误模型**：HTTP 恒 200；传输级 `-32600..-32603`，A2A 应用级 `-32001..-32099`（如 -32001 TaskNotFoundError）。
- **Task 状态机**：`SUBMITTED → WORKING → {INPUT_REQUIRED | AUTH_REQUIRED}（可恢复）→ COMPLETED | FAILED | CANCELED | REJECTED`。
- **Zed ACP 对照**：JSON-RPC over stdio；编辑器拉起 agent 子进程；`session/prompt` 期间 agent 可反向请求 `fs/read_text_file`——编辑器握有资源，这是与 A2A 对等的 HTTP 模型最本质的结构差异。

## 检查点

- [ ] 不看代码画出 A2A 从发现到流式结果的全部 HTTP 往返，标出每个 JSON-RPC envelope 字段。
- [ ] 解释为什么 ACP 里读文件是 agent→editor 请求，而 A2A 里 agent 读沙箱文件不需要惊动对端。
- [ ] `session/update` 通知与 JSON-RPC 请求在信封上的区别是什么？

## 资料入口

- MCP 官方文档: [modelcontextprotocol.io](https://modelcontextprotocol.io) · MCP Specification: [spec.modelcontextprotocol.io](https://spec.modelcontextprotocol.io) · JSON-RPC 2.0: [jsonrpc.org](https://www.jsonrpc.org/specification)
- A2A 规范 v1.0: [a2a-protocol.org](https://a2a-protocol.org/v1.0.0/specification) · [proto](https://github.com/a2aproject/A2A/blob/main/specification/a2a.proto) · [Python SDK](https://pypi.org/project/a2a-sdk/) · [JS SDK](https://www.npmjs.com/package/@a2a-js/sdk)
- Zed ACP: [agentclientprotocol.com](https://agentclientprotocol.com/protocol/v1/overview) · [repo](https://github.com/agentclientprotocol/agent-client-protocol)
- AG-UI: [github.com/ag-ui-protocol/ag-ui](https://github.com/ag-ui-protocol/ag-ui)（v1.0 事件族）
- LangGraph HITL (interrupt): [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
