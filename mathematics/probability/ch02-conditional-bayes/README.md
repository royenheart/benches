# ch02 · 条件概率、贝叶斯定理、独立性

> 把第 1 章的概率公理映射到"看见证据"这件事上：当额外信息来到以后，怎么修改概率。
> 学完本章你能立刻答出来："医疗检查阳性 + 该病罕见"体系下到底要不要慌、"垃圾邮件过滤器阈值应设到多少"这种工程人爱问的题。

## 学习目标

- 用一句话说**条件概率**与**联合概率**的关系，并能从中推导全概率公式与贝叶斯公式；用 sympy 写下 Beta-Binomial 共轭后验的闭式
- 用蒙特卡洛复现 Monty Hall 三门问题，理解 P=2/3 还是 P=1/2 的混淆之处
- 给一份医疗诊断 PPV 报告 + 给一份垃圾邮件过滤器的 cut-off 设计建议
- 一同段看到 "independent"、"conditionally independent"、"exchangeable"、"i.i.d." 不混淆
- 说出**先验选错的**两个最常见错误

## 三个能立刻解决的场景

1. **医疗筛查**：罕见病 + 高灵敏度检查 + 低基础率 → 实际阳性后你患病的概率是几成。
2. **垃圾邮件过滤**：建 Posterior 时换 cut-off，估算 FP/FN 的工程平衡。
3. **多源更新**：早、中、晚分隔三批补收到新数据，后验如何顺序更新 — 重要性质：**顺序无关**。

## 参考课程位置

- Stat 110 (Blitzstein & Hwang) §2.3-2.5 + §3.2-3.3
- MacKay, *Information Theory, Inference, and Learning Algorithms*, Ch.2
- Murphy, *Probabilistic Machine Learning* Vol.1, §3.2

## 文件清单

| 文件 | 作用 |
|---|---|
| [`notebook.ipynb`](notebook.ipynb) | 主授课：概念+推导+代码+图。 |
| [gen.py](gen.py) | 生成 notebook 的 Python 源。 |
| [exercises.md](exercises.md) | 5 道课后题（3 基础 / 1 进阶 / 1 工程实战）。 |
| [solutions.md](solutions.md) | 仅基础题提示与代码骨架。 |