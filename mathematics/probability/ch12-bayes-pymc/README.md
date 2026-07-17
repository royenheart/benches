# ch12 · 贝叶斯推断基础: 共轭先验、后验预测、可信区间

> 把 ch02 Beta-Binomial 共轭推广到 PyMC 工业级; 用 HMC / NUTS 给非共轭场景出后验。

## 学习目标

- 推 Beta-Binomial、Gamma-Poisson、Normal-Normal 三大共轭
- 用 PyMC 拟合 Beta-Binomial + 后验预测分布
- 解释可信区间 vs 置信区间的语义差异
- 用 arviz 给 trace plot、R-hat、ESS 诊断
- 复用在线 Beta 更新: 工程场景中无显式 inference question → 你能在 5 行 update 后验

## 场景
1. **广告 CTR credible interval**: 后验 95% CI 比 frequentist CI 信息更直接
2. **共轭 Beta-Binomial 在线学习**: ch02 已用, 这里给 PyMC + 经典对比
3. **后验预测分布**: 不只是后验参数, 也要"下一代观测 y 在何处分布"

## 参考
- Murphy §3.1-3.3, §5.1-5.3
- Gelman *Bayesian Data Analysis* Ch.2-3
- PyMC 文档 https://www.pymc.io/projects/docs