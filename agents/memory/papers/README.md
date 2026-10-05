# papers/：Agent Memory 论文精读

本目录是 memory 章节的论文精读层：5 份笔记、41 篇论文/文献，覆盖 2023-2026 的 agentic memory 全谱系。所有笔记于 2026-10-05 按统一模板精读：逐篇核对 arXiv 原文（abs + HTML 全文），关键数字标注证据等级（[自报] / [独立复现] / [厂商数据] / [grey literature] / [未核实]），无法核实的声明在文中显式标出。每个论文小节配有可视化：全库共 26 个 mermaid 架构/流程图 + 8 段伪代码 + 16 张对比/数据表（已用 mermaid-cli 全量渲染验证 26/26 通过）。

## 阅读顺序

| 顺序 | 文件 | 内容 | 回答的问题 |
|---|---|---|---|
| 1 | [01-agentic-memory-foundations.md](01-agentic-memory-foundations.md) | A-MEM、MemoryBank、MemGPT、Generative Agents、Voyager、Mem0、Zep/Graphiti（7 篇） | 单个 agent 的记忆系统是怎么演化来的 |
| 2 | [02-shared-and-org-memory.md](02-shared-and-org-memory.md) | Collaborative Memory、MemClaw、Governed Memory、CoMem、AgentRoom、blackboard、G-Memory、MIRIX（8 篇） | 多个 agent / 多个用户如何共享记忆而不失控 |
| 3 | [03-decay-conflict-poisoning.md](03-decay-conflict-poisoning.md) | MPBench、FadeMem、SSGM、SF-AMS 精读 + 投毒防御速览（13 篇） | 共享且长寿命的记忆如何腐化、冲突、被投毒，怎么防 |
| 4 | [04-org-knowledge-and-adrs.md](04-org-knowledge-and-adrs.md) | Walsh & Ungson 组织记忆理论、AgenticAKM、MADR/DocDag、Glean/Onyx、MCP 连接器（7 项） | 组织级记忆：文档系统、ADR/RFC、决策对齐 |
| 5 | [05-cloud-memory-architecture.md](05-cloud-memory-architecture.md) | projectmem、ESAA、MPBench、Muse、存储工程蒸馏（6 项） | 云端分布式记忆平台的工程架构 |

与章节的对应关系：1-3 是 memory/ 章节的理论纵深（notebook 00-02 的概念在论文里长什么样）；4-5 是 cloud-agent 设计文档 §13 的完整依据（三平面组织记忆 + 事件溯源存储），orchestration/ 章节的管控面讨论与 2、4 互相印证。

## 核心结论速览

- 单 agent 记忆的演化主线：原始日志（Generative Agents）→ 遗忘曲线（MemoryBank）→ OS 分页自管理（MemGPT）→ 结构化笔记（A-MEM）→ 抽取+更新流水线（Mem0）→ 时间图谱失效（Zep）。
- 共享记忆的收敛架构（2025-26 全部严肃系统一致）：**私有层 + 受治理共享层 + 晋升闸门**；四种失效（泄露/陈旧传播/矛盾持久化/溯源坍塌）全是治理失败而非检索失败。
- 记忆投毒是注入防御不覆盖的新通道，唯一 consistently 有效的防御是**记忆层的工具门控**。
- 组织场景的实践答案：git ADR 库是决策底座，异构文档系统（Notion/飞书）经 MCP 只读接入；agent 学得的记忆经"提议→人审→提交"晋升，**组织域永远不接受 agent 直写**。
