# MCP 协议与实践 教学专题

深入理解 Model Context Protocol（MCP）：从 JSON-RPC 传输层到 Tool/Resource/Prompt 三层模型，从零构建一个 toy MCP Server 和 Client。

## 目标

1. 理解 MCP 的架构模型：Client-Server、JSON-RPC 2.0、Transport（stdio/SSE）。
2. 掌握 MCP 的生命周期：initialize → initialized → tools/list → tools/call → shutdown。
3. 动手实现 Tool Server（暴露计算、查询工具）、Resource Server（提供文件内容）。
4. 理解 Prompt Templates 的设计：参数化提示词模板，服务端管理，客户端调用。

## 目录结构

```text
agents/mcp/
├── README.md
├── notebooks/
│   ├── 00_mcp_architecture.ipynb
│   ├── 01_tool_server.ipynb
│   └── 02_resources_and_prompts.ipynb
└── scripts/
    ├── mcp_server_demo.py
    └── mcp_client_demo.py
```

## 快速开始

```bash
python agents/mcp/scripts/mcp_server_demo.py --transport stdio --verbose &
python agents/mcp/scripts/mcp_client_demo.py --tool calculator --args '{"expr": "2+3*4"}'
# API mode — LLM 自动选择工具
python agents/mcp/scripts/mcp_client_demo.py --use-api --query "帮我算一下 (12+8)*5"
jupyter notebook agents/mcp/notebooks
```

所有实现仅使用 Python 标准库（json、subprocess、sys），不依赖 MCP SDK。

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

## 可调参数

- `mcp_server_demo.py`
  - `--transport`：stdio
  - `--verbose`：打印所有收发的 JSON-RPC 消息
  - `--tools`：暴露哪些工具（calculator/weather/file）

- `mcp_client_demo.py`
  - `--server-cmd`：server 启动命令
  - `--tool`：要调用的工具名
  - `--args`：JSON 格式的工具参数

## 资料入口

- MCP 官方文档: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- MCP Specification: [spec.modelcontextprotocol.io](https://spec.modelcontextprotocol.io)
- JSON-RPC 2.0: [jsonrpc.org](https://www.jsonrpc.org/specification)
