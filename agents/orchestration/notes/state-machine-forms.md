# 状态机的形态：隐式、显式、声明式与持久执行

任何 agent 循环本质上都是状态机——区别只在于**状态存在哪、转移函数 δ 存在哪**。这个笔记把四种形态放在一张表里，并给出本仓库每个形态的可运行代码入口。

## 核心对偶

δ(当前状态, 事件) → 下一状态，这是状态机的定义，任何写法都少不了它。区别只在于它的形态：

- **δ 是代码**（分散在 if/elif 分支里，"当前状态"= 程序计数器的位置）——隐式；
- **δ 是数据**（转移表 / 图 / needs 数组），配一个通用循环解释执行——显式；
- **δ 被事件化**（每步决策追加进日志，崩溃后重放恢复）——持久执行。

两种写法可以互相机械重构：把 if/elif 提成分支表 = 隐式→显式；把查表循环内联展开 = 显式→隐式。所以"只是实现方式不同"在计算意义上成立——但 δ 是数据还是代码，决定了图的外部性质是否存在（可打印、可检查死状态、可持久化、可测试）。

## 四种形态对比

| 形态                            | 状态存哪                       | 转移逻辑存哪                        | 可检查/可视化 | checkpoint 恢复          | 本仓库代码                                                                           | 代表系统                                            |
| ------------------------------- | ------------------------------ | ----------------------------------- | ------------- | ------------------------ | ------------------------------------------------------------------------------------ | --------------------------------------------------- |
| 直线代码                        | 无（程序位置即顺序）           | 语句顺序                            | ✗             | ✗                        | `scripts/framework_styles_demo.py --style raw`                                       | 一次性脚本                                          |
| **隐式**（控制流即状态）        | 程序计数器 + 调用栈            | if/elif 分支（LLM 每轮现算 action） | ✗             | 难（PC 不可移植）        | `agent-runtime/scripts/react_loop_demo.py`、`--style sdk`（handoff 链）              | ReAct loop、OpenAI Agents SDK、多数手写 agent       |
| **显式**（状态字段 + 查表循环） | `state` 对象（如 `step` 字段） | 转移表（数据，如 `nodes` 字典）     | ✓             | 易（只存 state，δ 不变） | `--style graph`、`protocols/scripts/a2a_pair_demo.py` 的 Task.status、`--style crew` | LangGraph StateGraph、A2A Task 状态机、状态模式代码 |
| **声明式**（依赖图）            | steps + needs 数组             | 拓扑排序（转移不写成 switch）       | ✓             | 易                       | `scripts/workflow_dsl_demo.py`                                                       | Kestra / Argo / workflows.yml / CI                  |
| **持久执行**（事件溯源）        | 追加式事件历史                 | workflow 代码 + 确定性重放          | ✓             | 天然（重放即恢复）       | `scripts/temporal_agent_workflow.py`                                                 | Temporal                                            |

## agent 特有的第三层差异：转移权在谁手里

传统状态机的 δ 是确定函数。ReAct 式隐式状态机里，**连"下一状态"都是 LLM 每轮现算的**——转移权交给了模型（概率性）。显式图则把 LLM 关在节点内部，转移由图结构决定。

对于 state graph：单个节点内 llm 可以自行探索，自行决定状态；节点外的编排要么是确定性的，要么可以让 llm 决定 state，但转移仍由代码根据转移表/if else 等决定：

1. LLM 产出自由文本 → 节点内代码解析/校验/选择字段写入 state → 边函数读 state 做转移

这是生产架构的关键决策点：**控制面（转移判断）保持确定性，概率性只留在节点内部**——cloud-agent 设计里"LLM 不进触发/转移判断、只进节点"的原则就是由此而来。检查一个系统时可以直接问：它的 δ 是确定的还是概率的？状态持久化了吗？

## 阅读路径（按上表顺序跑一遍）

```bash
python agents/agent-runtime/scripts/react_loop_demo.py --scenario search --verbose          # 隐式：PC 即状态
python agents/orchestration/scripts/framework_styles_demo.py --style graph --verbose    # 显式：state.step + nodes 表
python agents/orchestration/scripts/framework_styles_demo.py --style raw --verbose      # 直线：无环
python agents/protocols/scripts/a2a_pair_demo.py --task research --verbose              # 显式：协议级 Task.status
python agents/orchestration/scripts/workflow_dsl_demo.py --auto-approve                 # 声明式：needs → topo
```

配套 notebook：`frameworks` 原三讲已并入本章（00 框架全景 / 01 LangGraph 与 OpenAI SDK / 02 CrewAI、AutoGen、ADK）。
