# ch05 · 答案骨架

## Q1 hint

Cov(X,Y) = ρ σ_X σ_Y = 0.4 * 2 * 3 = 2.4
Var(X+Y) = 4 + 9 + 2*2.4 = 17.8
Var(X-Y) = 4 + 9 - 2*2.4 = 8.2

## Q2 hint
```python
import numpy as np
rng = np.random.default_rng(seed=0)
n_am, n_af, n_bm, n_bf = 80, 20, 20, 80
A_cured = rng.binomial([n_am, n_af], [0.6, 0.55]).sum()
B_cured = rng.binomial([n_bm, n_bf], [0.5, 0.45]).sum()
print(f"A: {A_cured / 100:.2%}, B: {B_cured / 100:.2%}")
```

## Q3 hint
```python
import numpy as np
rng = np.random.default_rng(seed=0)
N = 2000
Z = rng.normal(0, 1, N)
X = 0.7 * Z + rng.normal(0, 0.5, N)
Y = 0.6 * Z + rng.normal(0, 0.5, N)
print("Raw Corr(X,Y):", np.corrcoef(X, Y)[0,1])
# partial Corr(X,Y | Z) = corr(X_resid, Y_resid)
Xr = X - np.polyval(np.polyfit(Z, X, 1), Z)
Yr = Y - np.polyval(np.polyfit(Z, Y, 1), Z)
print("Partial Corr:", np.corrcoef(Xr, Yr)[0,1])
```
Run, see partial drop to ~0.

## Q4 hint
X = rng.uniform(-1,1,size=10000); Y = X**2
print(np.corrcoef(X,Y)[0,1])  # ~ 0
plt.scatter(X, Y)  # 完美抛物线