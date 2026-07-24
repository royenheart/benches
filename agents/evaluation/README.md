# Agent 评估 教学专题

掌握 Agent 评估的完整方法论：从单元测试到端到端 Benchmark，从 LLM-as-Judge 到轨迹评估。

## 目标

1. 区分结果评估（outcome）和过程评估（process/trajectory）。
2. 实现多种评估器：schema validator、unit test evaluator、trajectory scorer。
3. 理解 LLM-as-Judge 的优势与陷阱：position bias、rubric design、calibration。
4. 了解主要 Benchmark：SWE-bench、GAIA、WebArena、AgentBench。

## 目录结构

```text
agents/evaluation/
├── README.md
├── notebooks/
│   ├── 00_evaluation_methods.ipynb
│   ├── 01_llm_as_judge.ipynb
│   └── 02_benchmarks_and_trajectories.ipynb
└── scripts/
    ├── evaluator_demo.py
    └── trajectory_replay.py
```

## 快速开始

```bash
python agents/evaluation/scripts/evaluator_demo.py --eval-type unit --data-dir .
python agents/evaluation/scripts/trajectory_replay.py --trajectory-file sample_traj.jsonl --gold-file sample_gold.jsonl
jupyter notebook agents/evaluation/notebooks
```

## Notebook 顺序

### 00. 评估方法总览

- 评估维度：正确性、效率、鲁棒性、安全性、用户体验。
- 评估层次：unit test → component test → integration test → end-to-end benchmark。
- Schema validation：Pydantic-style 的类型/范围校验。
- 练习：定义一个 Agent 输出 schema，编写 validator。

### 01. LLM-as-Judge

- 评分方法：pairwise comparison、rubric-based scoring、Likert scale。
- 偏置问题：position bias（先看的不公平）、verbosity bias（长的更好）、self-enhancement bias。
- 校准策略：multi-judge aggregation、锚定样本、人工校准。
- toy 模式用 keyword + pattern matching 模拟 judge；`--use-api` 用真实 LLM 评分（见 `evaluator_demo.py --eval-type llm-judge`），可实测 position/verbosity bias。

### 02. Benchmark 与轨迹评估

- SWE-bench 格式：issue description + repo snapshot + patch evaluation。
- 轨迹回放：从 JSONL 日志重建 Agent 的执行过程。
- 逐步评分：tool call 准确率、恢复率、步数效率。
- 练习：分析一段 toy trajectory，找出 Agent 的决策错误。

## 可调参数

- `evaluator_demo.py`
  - `--eval-type`：unit / schema / trajectory / llm-judge
  - `--strictness`：校验严格度

- `trajectory_replay.py`
  - `--metrics`：all / success-rate / step-efficiency / tool-accuracy

## 资料入口

- SWE-bench: [swebench.com](https://www.swebench.com) | [arXiv:2310.06770](https://arxiv.org/abs/2310.06770)
- GAIA: [arXiv:2311.12983](https://arxiv.org/abs/2311.12983)
- WebArena: [arXiv:2307.13854](https://arxiv.org/abs/2307.13854)
- AgentBench: [arXiv:2308.03688](https://arxiv.org/abs/2308.03688)
