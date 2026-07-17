# ch10 · 答案骨架

## Q1 hint
```python
import numpy as np
from scipy.stats import poisson
rng = np.random.default_rng(seed=0)
lam, T = 2.5, 10
counts = []
for _ in range(10000):
    t = 0; n = 0
    while True:
        t += rng.exponential(1/lam)
        if t > T: break
        n += 1
    counts.append(n)
counts = np.array(counts)
print("mean:", counts.mean(), "theory:", lam*T)
print("var:", counts.var(), "theory:", lam*T)
# Compare histogram to PMF
```

## Q2 hint
```python
import numpy as np
lam=500; mu=750
print("P95 W (ms):", np.log(20)/(mu-lam)*1000)
print("E[L]:", (lam/mu)/(1-lam/mu))
# For P95≤30ms: μ ≥ λ + ln(20)/0.030
mu_min = lam + np.log(20)/0.030
print(mu_min)
```

## Q3 hint
```python
import numpy as np
rng = np.random.default_rng(seed=0)
lam, mu = 0.3, 0.5; N = 10000
arr = np.cumsum(rng.exponential(1/lam, N))
ser = rng.exponential(1/mu, N)
end = np.zeros(N); wait = np.zeros(N)
end[0] = arr[0] + ser[0]
for k in range(1, N):
    start = max(arr[k], end[k-1])
    end[k] = start + ser[k]
    wait[k] = start - arr[k]
# L ≈ λ * W (Little)
print("λ*W:", lam * wait.mean())
# 直接 L 通过 time-average queue: integrate # in system over time
# Approximate: sum of service intervals
```

## Q5 hint
```python
import numpy as np
# Weighted average P95 W = Σ w_i * P95(rho_i)
mus = [2000]  # per instance
rhos = [0.5, 0.8, 0.95]
ws = [0.7, 0.2, 0.1]
mu_one = 2000
# needed instances for each rho
for rho in rhos:
    lam = rho * mu_one
    p95 = np.log(20)/(mu_one - lam) * 1000
    print(f"ρ={rho}: P95={p95:.2f}ms")
weighted_p95 = sum(w * np.log(20)/(mu_one - rho*mu_one)*1000 for w, rho in zip(ws, rhos))
print("weighted avg P95:", weighted_p95)
```