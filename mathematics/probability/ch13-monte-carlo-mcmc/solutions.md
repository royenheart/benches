# ch13 · 答案骨架

## Q1 hint
```python
import numpy as np
from scipy.stats import beta
rng = np.random.default_rng(seed=0)
M = beta.pdf(0.7, 7, 3)  # 最大密度
print(f"M={M:.4f}, 接受率~{1/M:.4f}")
accepted: list[float] = []
for _ in range(20000):
    x = rng.uniform(0, 1)
    if rng.uniform() < beta.pdf(x, 7, 3) / M:
        accepted.append(x)
acc = np.array(accepted)
print("mean:", acc.mean(), "theoretical:", 7/10)
print("var:", acc.var(), "theoretical:", 7*3/(100*11))
```

## Q2 hint
```python
import numpy as np
from scipy.stats import norm
rng = np.random.default_rng(seed=0)
N = 10000
x = rng.normal(0, 5, N)
w = norm.pdf(x, 2, 1) / norm.pdf(x, 0, 5)
est = np.sum(w * x**2) / np.sum(w)
ess = np.sum(w)**2 / np.sum(w**2)
print("E_pi[x^2]=", est, "true=5 (1+u², u=2, var=1)")
print("ESS=", ess)
```

## Q3 hint
TRW koje accepting/ESS atówé σ.

## Q4 hint
multi-mode 1-d: RW σ=0.3 mix slow; HMC 也难跨过 valley — 需 tempering.

## Q5 hint
```python
import numpy as np
rng = np.random.default_rng(seed=0)
N = 50000; D = 5
contexts = rng.normal(0, 1, size=(N, D))
w_new = rng.normal(0, 1, D)
w_old = rng.normal(0, 0.5, D)
pi_old = 1/(1+np.exp(-contexts @ w_old))
pi_new = 1/(1+np.exp(-contexts @ w_new))
actions = (rng.uniform(0, 1, N) < pi_old).astype(float)
rewards = actions * (1.0 + 0.1*rng.normal(0, 1, N))  # E[r|a=1]~1
w_is = pi_new * actions / pi_old + (1-pi_new)*(1-actions)/(1-pi_old)
est = np.sum(w_is * rewards) / np.sum(w_is)
ess = np.sum(w_is)**2 / np.sum(w_is**2)
print(f"IS estimate E[r|pi_new]={est:.4f}; ESS={ess:.0f}")
```