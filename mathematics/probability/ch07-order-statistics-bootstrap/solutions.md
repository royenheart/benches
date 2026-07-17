# ch07 · 答案骨架

## Q1 hint
X_(k) ~ Beta(k, n-k+1). 即 X_(5) of n=10 ~ Beta(5, 6). 
```python
from scipy.stats import beta
print(beta.mean(5, 6), 5/11)
print(beta.var(5, 6))
# 然後 模拟
rng = np.random.default_rng(seed=0)
X_n = np.sort(rng.uniform(0,1,size=(10000, 10)), axis=1)
print(X_n[:, 4].mean(), X_n[:, 4].var())
```

## Q2 hint
```python
import numpy as np
data = np.random.default_rng(seed=0).exponential(2.0, 50)
B = 5000
rng = np.random.default_rng(seed=0)
boot = []
for _ in range(B):
    idx = rng.integers(0, 50, 50)
    boot.append(np.median(data[idx]))
boot = np.array(boot)
print("Percentile", np.percentile(boot, [2.5, 97.5]))
# BCa:
from scipy.stats import norm
z0 = norm.ppf(np.mean(boot < np.median(data)) / B)  # bias-correction
# a = 0 (中性 mean 简省)
ci_lo = np.percentile(boot, 100 * norm.cdf(2*z0 + norm.ppf(0.025)))
ci_hi = np.percentile(boot, 100 * norm.cdf(2*z0 + norm.ppf(0.975)))
print("BCa", ci_lo, ci_hi)
```

## Q3 hint
Look ch07 case with `auc` function. Change size to 50. Report "{ci_low} - {ci_hi}".

## Q4 hint
Build loop:
```python
for n in [5, 50, 200]:
    rng = np.random.default_rng(0)
    cnt = 0
    for _ in range(200):
        X = rng.normal(0, 1, n)
        boot = rng.choice(X, size=(500, n)).mean(axis=1)
        lo, hi = np.percentile(boot, [2.5, 97.5])
        if lo <= 0 <= hi: cnt += 1
    print(n, "coverage:", cnt/200)
```
Expect low coverage at n=5, climb to 0.95 by n=50.