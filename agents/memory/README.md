# Agent 记忆系统 教学专题

理解 Agent 如何记住、检索和利用过去的信息：从工作记忆到长期记忆，从 TF-IDF 检索到 RAG 增强，从经验积累到 Reflexion 自省模式。

## 目标

1. 区分四种记忆类型：工作记忆、短期记忆、长期记忆（情节/语义/程序）。
2. 动手实现 TF-IDF 检索和简单的 RAG pipeline。
3. 理解 Reflexion 模式：失败 → 反思 → 存储教训 → 改进重试。
4. 掌握记忆系统的核心取舍：容量 vs 精度、检索延迟 vs 相关性。

## 目录结构

```text
agents/memory/
├── README.md
├── notebooks/
│   ├── 00_memory_types.ipynb
│   ├── 01_rag_retrieval.ipynb
│   └── 02_episodic_reflexion.ipynb
└── scripts/
    ├── memory_store_demo.py
    └── reflexion_demo.py
```

## 快速开始

```bash
python agents/memory/scripts/memory_store_demo.py --store-type both --query "agent safety" --verbose
python agents/memory/scripts/reflexion_demo.py --task math --max-attempts 3 --verbose
# API mode
python agents/memory/scripts/memory_store_demo.py --store-type longterm --query "agent safety" --use-api
python agents/memory/scripts/reflexion_demo.py --task math --use-api --verbose
jupyter notebook agents/memory/notebooks
```

## Notebook 顺序

### 00. 记忆分类与工作记忆

- 工作记忆：dict-based state store，容量限制和驱逐策略。
- 短期 vs 长期：context window 的有限性，以及何时需要外部存储。
- 实现一个带记忆读写接口的 Agent 状态管理器。

### 01. RAG 与检索增强

- 从零实现 TF-IDF 索引：文档分词 → IDF 计算 → 查询向量 → Cosine 相似度排序。
- 扩展到 metadata filtering 和 hybrid search（关键词 + 语义）。
- 对比有无 RAG 时 Agent 回答质量的差异。

### 02. 情节记忆与 Reflexion

- 运行 `reflexion_demo.py`，观察 Agent 如何在多次失败中积累经验。
- 情节记忆的数据结构：task、action、outcome、lesson。
- 反思合成：从多条情节中提取通用教训，而非记住所有细节。

## 可调参数

- `memory_store_demo.py`
  - `--store-type`：working / longterm / both
  - `--query`：检索查询词
  - `--capacity`：工作记忆容量上限

- `reflexion_demo.py`
  - `--task`：math / puzzle
  - `--max-attempts`：最大尝试次数
  - `--verbose`：打印每次尝试的反思内容

## 资料入口

- Reflexion: [arXiv:2303.11366](https://arxiv.org/abs/2303.11366)
- Generative Agents: [arXiv:2304.03442](https://arxiv.org/abs/2304.03442)
- MemGPT / Letta: [letta.com](https://letta.com)
- Mem0: [github.com/mem0ai/mem0](https://github.com/mem0ai/mem0)
