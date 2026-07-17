# ch08 · 参数估计: 矩法、MLE、Fisher 信息

> 把"凭直觉估参数"扩展到三大经典方法; MLE 是 ML 训练损失 (cross-entropy / MSE) 的源头。

## 学习目标

- 推导 MLE 公式: 取似然 · log, 求极值
- 推导 Fisher 信息与 Cramer-Rao 下界的关系
- 用 PyTorch 写 Powell-ML 上的 logistic regression MLE
- 把 MLE 与损失对应: MSE = MLE of Normal; BCE = MLE of Bernoulli
- 解释 asymptotic normality of MLE

## 场景
1. 估计 Exp(λ) 速率参数: $\\hat\\lambda = 1/\\bar X$
2. 用 Normal-INCE 估 \\mu, \\sigma²
3. 解释 LR gradient 是 MLE 的数值推 (=向后, accelerated·scaling)

## 参考
- Stat 110 §8.3-8.5
- Lehmann & Casella *Theory of Point Estimation*
- Murphy §3.3-3.5