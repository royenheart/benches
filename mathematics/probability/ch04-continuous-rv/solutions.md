# ch04 · 答案骨架

## Q1 hint

```python
import numpy as np
rng = np.random.default_rng(seed=0)
N = 50_000; lam = 1/2
samples = rng.exponential(scale=1/lam, size=N)
# P(X>5 | X>3) = P(X>5 减 X>3) = E[|>5] / E[|>3]
n_above_3 = (samples > 3).sum()
n_above_5 = (samples > 5).sum()
p_cond = n_above_5 / n_above_3
print("emperical:", p_cond, "theory:", np.exp(-lam*(5-3)))
```

## Q2 hint

`Y = sum_i X_i ~ Gamma(n, 1/λ)` mean=n/λ, var=n/λ²
```python
import numpy as np
n, lam = 5, 0.2
rng = np.random.default_rng(seed=0)
Y_samps = rng.exponential(scale=1/lam, size=(10000, n)).sum(axis=1)
print(Y_samps.mean(), n/lam)  # 25
print(Y_samps.var(), n/lam**2)  # 125
```

## Q3 hint

shape=1: Weibull 退化为 Exp(scale=1/λ)
PDF = (1/λ) exp(-x/λ)
位置与 exp(scale=1/λ) 同

## Q5 hint

样本均值与方差代入正态近似, P95 的 95% CI 是 mean - 1.645 * std, 误差范围 σ/√N * 1.96