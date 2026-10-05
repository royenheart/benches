# 从教学 Loop 到生产 Loop：差距清单

本专题的 demo 是可运行的最小骨架：隐式状态机、进程内状态、玩具工具。生产环境在每个构件上都要补一课。这张清单同时是 cloud-agent 设计的约束来源。

| 构件 | 教学做法（本专题） | 生产做法 | 去哪学 |
|---|---|---|---|
| loop 终止 | `max_steps` + `action == done` | token / tool-call 双预算 + 墙钟超时 + stall 检测（重复动作计数、硬计数器 `max_rounds/max_stalls`） | `../orchestration/`（状态机形态）、`../production/`（可靠性） |
| 决策输出 | LLM 自由文本，`startswith("ACTION:")` 解析 | 结构化输出（JSON Schema / grammar 约束），解析失败自动重试 | `../context-engineering/` |
| tool 契约 | 两个内置玩具工具，无校验层 | JSON Schema 校验、错误三分类（可重试 / 参数错 / 权限拒绝）、幂等键、超时与取消 | `../protocols/`（MCP 协议级合同）、`../safety/`（权限检查点） |
| state | 进程内 dataclass，随进程消亡 | 可持久化 / checkpoint（显式状态机），崩溃后恢复到同一状态 | `../orchestration/notes/state-machine-forms.md` |
| 权限 | 无 | 工具调用前的确定性 hook（不经 LLM），敏感操作走人工审批 | `../safety/`、`04_harness_design.ipynb` |
| 观测 | `--verbose` 打印 trace | span-based tracing（OTel GenAI 语义）、token 计量、轨迹评估 | `../production/`、`../evaluation/` |
| 转移权 | LLM 每轮现算 action（概率性 δ） | 控制面确定性：LLM 不进转移判断，只进节点 | `../orchestration/notes/state-machine-forms.md` |
| 记忆 | `state.observations` 单会话 | 跨会话记忆分工作/情节/语义/程序四层，检索后注入 | `../memory/` |
| 上下文 | 全量历史进 prompt | token 预算、compaction、subagent 隔离、prompt caching | `../context-engineering/` |

一句话总结：**本章教你把循环转起来，其余章节教你把它转得可控、可恢复、可观测、可授权。**
