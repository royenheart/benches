# ch05 · 联合分布、协方差、相关 vs 因果

> 从一维扩到二维随机变量; 引入协方差、相关系数、辛普森悖论, 帮助你看穿"相关 ≠ 因果"。

## 学习目标

- 写出 joint / marginal / conditional PDF 的互推公式
- 计算 Cov / Corr / Var(X±Y) 闭合解
- 论证辛普森悖论 (Simpson's paradox) 的几何来源
- 用 numpy 实证 "相关 ≠ 因果" 的两套 confounder 案例
- 写一段"去掉 confounder 后相关系数变化"的可视化

## 场景

1. **特征相关性筛选**: 高相关 ≠ 真有用, 协变量 confounder 让你误删 / 误留特征
2. **A/B 测试混杂**: 不同应变分桶中性别比例不同 → 看似胜出的变体其实由性别 confounder 主导
3. **稳定推断**: 引入协方差后稳定方差估计 (I洛赫个 VC 维背后的 rt-sconnection)

## 参考课程位置

- Stat 110 §7.1-7.3
- Murphy §2.6-2.7
- Pearl *Causality* §1-2 (intro)

## 文件清单

| 文件 | 作用 |
|---|---|
| [`notebook.ipynb`](notebook.ipynb) | 主讲 |
| [gen.py](gen.py) | 笔记本源 |
| [exercises.md](exercises.md) | 5 题 |
| [solutions.md](solutions.md) | 基础题 |