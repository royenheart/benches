# Deep Research 与推理模式 教学专题

从「一次性回答」到「花十分钟做研究」：test-time compute、thinking 模式与 deep research agent 模式（plan → search → synthesize → cite）的原理与实操。

## 目标

1. 理解 test-time compute：用更多推理 token 换更高正确率，用真实 thinking 模式实测对比。
2. 拆解 deep research agent 的循环：任务规划 → 多轮检索 → 信息综合 → 引用标注。
3. 学会评估研究报告质量：覆盖度、引用准确性、事实一致性。

## 目录结构

```text
agents/deep-research/
├── README.md
├── notebooks/
│   ├── 00_thinking_mode.ipynb
│   ├── 01_deep_research_pattern.ipynb
│   └── 02_research_eval.ipynb
└── scripts/
    ├── thinking_compare.py
    └── mini_deep_researcher.py
```

## 快速开始

```bash
# Toy mode — 本地语料 + 模板综合
python agents/deep-research/scripts/mini_deep_researcher.py --question "agent 记忆系统有哪些主流方案" --verbose

# API mode — 真实 thinking 对比 + LLM 驱动的研究循环
python agents/deep-research/scripts/thinking_compare.py --use-api --verbose
python agents/deep-research/scripts/mini_deep_researcher.py --question "agent 记忆系统有哪些主流方案" --use-api --verbose
jupyter notebook agents/deep-research/notebooks
```

## Notebook 顺序

### 00. Thinking 模式与 Test-time Compute

- Test-time compute：训练后不再更新权重，靠推理时「想更久」提升正确率。
- DeepSeek thinking 模式实测：同一推理题，thinking 开/关的正确率与 token 成本对比。
- Reasoning effort（low/medium/high）：成本与质量的旋钮。

### 01. Deep Research 模式

- 研究循环解剖：plan（拆子问题）→ search（逐个子问题检索）→ synthesize（综合 + 引用）→ verify（覆盖度检查，不足则第二轮）。
- 实操：mini deep researcher，本地语料检索 + 真实 LLM 规划与综合。
- 与单轮 RAG 的本质差异：多轮、自主决定「还缺什么」。

### 02. 研究报告评估

- 三个质量维度：覆盖度（子问题是否都回答了）、引用准确性（引用的文档是否支持该论断）、事实一致性（是否与源文档矛盾）。
- 用 LLM-as-judge 真实评分自己产出的研究报告。
- 评估驱动迭代：低分维度反馈给下一轮研究。

## 可调参数

- `thinking_compare.py`
  - `--use-api`：真实对比（必需，toy 模式只打印概念说明）
  - `--effort`：low / medium / high（thinking 模式下）

- `mini_deep_researcher.py`
  - `--question`：研究问题
  - `--rounds`：最大研究轮数（默认 2）
  - `--use-api`：LLM 规划与综合
  - `--verbose`：打印每轮子问题、检索命中、引用

## 资料入口

- DeepSeek Thinking Mode: [api-docs.deepseek.com/guides/thinking_mode](https://api-docs.deepseek.com/zh-cn/guides/thinking_mode)
- OpenAI Deep Research: [openai.com/index/introducing-deep-research](https://openai.com/index/introducing-deep-research/)
- STORM (Stanford, 多视角研究写作): [arXiv:2402.14207](https://arxiv.org/abs/2402.14207)
- Test-Time Compute: [arXiv:2408.03314](https://arxiv.org/abs/2408.03314)
