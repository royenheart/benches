# ch06 · 答案骨架

## Q1 hint
```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
rng = np.random.default_rng(seed=0)
means = rng.binomial(1, 0.4, size=(5000, 100)).mean(axis=1)
mu, sigma = 0.4, np.sqrt(0.4*0.6)
zn = (means - mu) / (sigma / np.sqrt(100))
plt.hist(zn, bins=40, density=True)
xs = np.linspace(-4, 4); plt.plot(xs, norm.pdf(xs))
```

## Q2 hint
b - a = 2
n ≥ log(2/0.01) / (2 * 0.02² / 4) ≈ 7327  → 22000 例幅更大
```python
import numpy as np
n = 22000; N = 1000
rng = np.random.default_rng(seed=0)
violations = 0
for _ in range(N):
    X = rng.uniform(-1, 1, size=n)
    if abs(X.mean()) >= 0.02: violations += 1
print(violations / N)
```

## Q3 hint
```python
import numpy as np
from scipy.stats import norm
rng = np.random.default_rng(seed=0)
for n in [10, 100, 1000]:
    X = rng.exponential(1, size=(5000, n)).mean(axis=1)
    # KS statistic via direct diff
    xs_sorted = np.sort(X)
    F_emp = np.arange(1, len(xs_sorted)+1) / len(xs_sorted)
    F_norm = norm.cdf(xs_sorted, loc=1, scale=1/np.sqrt(n))
    print(f"n={n}, KS={np.max(np.abs(F_emp - F_norm)):.4f}")
```

## Q4 hint
Cauchy 均值仍 Cauchy — CLT 不成立. 多次 mean 仍 Cauchy 分布, var 无穷. sample var 报~"∞"或随样本数爆炸。
```python
rng = np.random.default_rng(seed=0)
trials = [rng.standard_cauchy(10000).mean() for _ in range(200)]
print("Trial means range:", min(trials), max(trials))  # spread 彶彶
```