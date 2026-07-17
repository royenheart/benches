# ch00 · 概率是什么 + 工作流落地

> 本系列**第一章**，专门给"想用概率建模但不知从哪下手"的工程读者。
> 学完本章你应当能用 `numpy / scipy.stats / sympy / matplotlib` 写出第一段随机模拟脚本；理解随机数生成器的可复现语义；并 fueron 身边那些"看起来确定的"系统其实背后都有概率假设。

## 学习目标

- 说出概率建模的**三个何时**：何时娛到、何时是用闭式结果、何时采样
- 用 `default_rng(seed)` 写出可复现的随机实验
- 用 sympy 推导出 Bernoulli / Binomial 均值方差闭式解，与 numpy 采样均值对照
- 读懂别人代码中 `numpy.random.seed` vs `default_rng(seed)` 的差别
- 头一次遇到术语“试验实现/频率收敛/估算精度”时不会发虲

## 三个能立刻解决的场景

1. **估算一个复杂概率**：比如“一局三位决定加原宝肉复加补金” 产生指定出现概率 p ≤ 0.01 的事件，解析替代不了采样结果，动手刚模拟。
2. **写一段可复现的 benchmark 报告**：复现接口；报 RNG seed 是亓务素质。
3. **读懂科学论文中的“我们可以发现”**：不可以模拟。

## 参考课程位置

- Stat 110（Blitzstein & Hwang）§1.1-1.4：样本空间、概率公理、模拟思想
- Bertsekas §1.x：概率空间与条件概率定义
- Murphy §2.1-2.2：贝叶斯视角与频率派视角

## 文件清单

| 文件 | 作用 |
|---|---|
| [`notebook.ipynb`](notebook.ipynb) | 主讲理论 + 代码 + 实验。需 `uv run --extra probability jupyter lab`。 |
| [gen.py](gen.py) | notebook 的 cells 源描述。重生：`uv run --extra dev python -m tools.math.nb_build gen.py notebook.ipynb`。 |
| [exercises.md](exercises.md) | 5 道课后题（3 基础环上完不跳读解决、1 进阶证明过的 kindlegen结果、1 工程实战转发到你所造的多场实例。|
| [solutions.md](solutions.md) | 基础题关键提示 + 可在沙盒跑的代码骨架。进阶与实战仅出算路抽象描述。 |