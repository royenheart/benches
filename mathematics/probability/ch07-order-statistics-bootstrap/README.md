# ch07 · 次序统计量、分位数、Bootstrap

> 不依赖参数化分布假设时如何给"经验分布 + 误差棒"? Bootstrap 是 ML 工业默认的 CI 估计法之一, 必须熟练运用。

## 学习目标

- 写出次序统计量 (X_(k)) 的精确分布公式
- 解释经验分布 $F_n(x)$ 与真实 CDF 的关系
- 写一段 Bootstrap 抽样估计 median 的 95% CI
- 对比 BCa vs percentile Bootstrap, 知道何时该用前者
- 给一段 Bias-Corrected CI 的实现骨架

## 场景
1. 给 median、p99 等 robust 统计的 CI; 解析 CI 在 asymmetric/重尾下偏倚
2. 模型评估时给 AUC、Recall 等指标的 Bootstrap CI
3. A/B 测试样本量很小时的 mean-difference bootstrap CI

## 参考
- Stat 110 §8.1-8.3
- Efron & Tibshirani *An Introduction to the Bootstrap*
- Murphy §2.8