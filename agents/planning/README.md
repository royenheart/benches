# Agent 规划与搜索 教学专题

从任务分解到搜索策略：掌握 Agent 如何将复杂目标拆解为可执行的子任务，以及如何使用 Tree of Thoughts、Beam Search 等方法在解空间中搜索最优路径。

> 分层定位：L1 运行时——**单个 agent 怎么规划**。预定义工作流的执行图（DAG 调度、引擎、审批门）属于编排层，见 [`../orchestration/`](../orchestration/README.md)；本章的 DAG 是 agent 的思考产物，两者同名不同义。

## 目标

1. 理解任务分解的核心原则：可检查的子目标、依赖关系、并行机会。
2. 实现 DAG（有向无环图）调度器，自动识别可并行的任务。
3. 跑通 Tree of Thoughts：BFS/DFS/Beam Search 在 puzzle 求解中的应用。
4. 理解 ReWOO 的效率权衡：解耦规划与观察，减少冗余 LLM 调用。

## 目录结构

```text
agents/planning/
├── README.md
├── notebooks/
│   ├── 00_task_decomposition.ipynb
│   ├── 01_tree_of_thoughts.ipynb
│   └── 02_search_strategies.ipynb
└── scripts/
    ├── task_decomposer_demo.py
    └── tot_solver_demo.py
```

## 快速开始

```bash
python agents/planning/scripts/task_decomposer_demo.py --goal "build a REST API" --strategy dag --verbose
python agents/planning/scripts/tot_solver_demo.py --problem 24game --strategy beam --beam-width 3
# API mode
python agents/planning/scripts/tot_solver_demo.py --strategy llm --numbers 3 3 8 8 --use-api
python agents/planning/scripts/task_decomposer_demo.py --goal "build a REST API" --use-api
jupyter notebook agents/planning/notebooks
```

## Notebook 顺序

### 00. 任务分解与依赖

- 学习如何将高层目标拆解为带依赖关系的子任务。
- 实现拓扑排序和 DAG 并行调度。
- 练习：设计完成条件（acceptance criteria），避免分解后无法验证。

### 01. Tree of Thoughts

- 理解 BFS/DFS/Beam Search 的区别和适用场景。
- 实现启发式评估函数：对中间状态打分，剪枝低分分支。
- 在 24 点游戏上对比不同搜索策略的效率和成功率。

### 02. 搜索策略与 ReWOO

- 深入 Beam Search 的参数调优（beam width、max depth）。
- 实现 ReWOO 风格规划器：先生成带占位符的计划，再批量执行工具填充。
- 对比 ReWOO vs ReAct 的 token 消耗和执行效率。

## 可调参数

- `task_decomposer_demo.py`
  - `--goal`：待分解的目标
  - `--strategy`：sequential / dag / parallel
  - `--verbose`：打印依赖图和执行顺序

- `tot_solver_demo.py`
  - `--problem`：24game / wordladder
  - `--strategy`：bfs / dfs / beam
  - `--beam-width`：beam search 宽度
  - `--max-depth`：最大搜索深度

## 资料入口

- Tree of Thoughts: [arXiv:2305.10601](https://arxiv.org/abs/2305.10601)
- LATS (Language Agent Tree Search): [arXiv:2310.04406](https://arxiv.org/abs/2310.04406)
- ReWOO: [arXiv:2305.18323](https://arxiv.org/abs/2305.18323)
- Graph of Thoughts: [arXiv:2308.09687](https://arxiv.org/abs/2308.09687)
