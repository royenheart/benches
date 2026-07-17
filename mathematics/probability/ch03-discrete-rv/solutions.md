# ch03 · 答案骨架

## Q1 hint

每次独立 Bern(p)。**最多 3 试**：3 次都失败概率 = $(1-p)^3 = 0.001$。Geom(0.9) 写成"成功为止的实验数" G；关心的是 $G > 3$ 的概率 = $(1-p)^3 = 0.001$。

```python
p = 0.9
print("P(3 次都失败):", (1-p)**3)
```

## Q2 hint

Poisson rate λ=3.5 per week。
```python
from scipy.stats import poisson
print("P(K>=5 | λ=3.5):", 1 - poisson.cdf(4, 3.5))
# 期望输出约 ~0.27
```

## Q3 hint

P(K=拾到第5个success时的尝试数 ≥ 100) = P(K_Move 在 95..99 区间内"成功数为 4")。
```python
from scipy.stats import nbinom
# k = 总试验数, r=5, p=0.05
# P(K≥100) = 1 - NBin.cdf(k=99 的 r=5: we need success_count<5 by trial 99)
# scipy nbinom.pmf(x, n, p) is count of *failures* before r-th success.
# So total trials = x + r; we want trials >= 100 -> x >= 95
print("P(trials ≥ 100):", 1 - nbinom.cdf(94, 5, 0.05))
```

## Q5 hint

两变体 CTR 均值差 $p_B - p_A = 0.02$
方差差 ≈ $\\frac{p_A(1-p_A)}{n_A} + \\frac{p_B(1-p_B)}{n_B}$。
朴素设 $n_A = n_B = n$，标准差 $\\sigma = \\sqrt{(p_A(1-p_A) + p_B(1-p_B))/n}$。
需要 $1.96\\sigma \\le |p_B - p_A| = 0.02 \\Rightarrow$

```python
import numpy as np
pA, pB = 0.10, 0.12
diff = abs(pB - pA)
n = (1.96**2) * (pA*(1-pA) + pB*(1-pB)) / diff**2
print(f"每变体需 ~{int(n)} 样本")
```