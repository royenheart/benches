# ch08 · 答案骨架

## Q1 hint

```python
import numpy as np
rng = np.random.default_rng(seed=0)
N = 1000; lam_true = 0.7
mles = [1.0 / rng.exponential(scale=1/lam_true, size=200).mean() for _ in range(N)]
mles = np.array(mles)
print("Var(MLE):", mles.var(), "CRB:", lam_true**2 / 200)
```

期望: ~4.9e-4 vs ~2.45e-3 → 实际 var 略低于 CRB 几成; 因 exp 分布为常见 eminent Liam.

## Q2 hint
```python
import numpy as np
rng = np.random.default_rng(seed=0)
emp0 = []; emp1 = []
for _ in range(1000):
    X = rng.normal(0, 1, 20)
    emp0.append(X.var(ddof=0))
    emp1.append(X.var(ddof=1))
print(f"ddof=0 mean = {np.mean(emp0):.4f} (bias = -{1-np.mean(emp0):.4f})")
print(f"ddof=1 mean = {np.mean(emp1):.4f} (bias = -{1-np.mean(emp1):.4f}, should be ~0)")
```

## Q3 hint
```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
rng = np.random.default_rng(seed=0)
lam = 1.4
fig, axes = plt.subplots(1, 4, figsize=(14, 4), dpi=110, constrained_layout=True)
for ax, n in zip(axes, [10, 50, 200, 1000]):
    mles = []
    for _ in range(1000):
        mles.append(1.0 / rng.exponential(scale=1/lam, size=n).mean())
    mles = np.array(mles)
    se = np.sqrt(lam**2 / n)
    z = (mles - lam) / se
    ax.hist(z, bins=40, density=True, color="lightgray", alpha=0.7)
    xs = np.linspace(-4, 4)
    ax.plot(xs, norm.pdf(xs), color="crimson", lw=2)
    ax.set_title(f"n={n}")
plt.show()
```

## Q4 hint
```python
import numpy as np
import torch
torch.manual_seed(0)
rng = np.random.default_rng(seed=0)
N, D = 500, 50
X = torch.tensor(rng.normal(0, 1, size=(N, D)), dtype=torch.float32)
true_w = torch.tensor(rng.normal(0, 1, size=D), dtype=torch.float32)
logits = X @ true_w
y = torch.tensor((rng.uniform(0, 1, N) < torch.sigmoid(logits).numpy()).astype(np.float32))
w = torch.zeros(D, requires_grad=True)
opt = torch.optim.LBFGS([w], lr=0.1, max_iter=100)
def closure():
    opt.zero_grad()
    loss = torch.nn.functional.binary_cross_entropy_with_logits(X @ w, y)
    loss.backward(); return loss
opt.step(closure)
err = (w - true_w).norm() / true_w.norm()
print(f"||w_hat - w_true||/||w_true|| = {err:.4f}")
```

## Q5 hint (reference). Loss ↔ MLE:

| Loss (training) | MLE 分布假设 |
|---|---|
| Squared error (regression) | Normal y|X ~ N(μ=ŷX, σ²) with σ² const |
| BCE | Bernoulli(y) with p = σ(w·X) |
| Softmax / cross-entropy | Categorical(y) with probs = softmax(Z) |
| L1 (MAE) | Laplace y|X ~ Laplace(μ=ŷ, b) |
| Gaussian NLL | Normal y|X ~ N(μ=ŷ, σ²=σ²(X)) |
| Dansing L2 | exponential family 离散特殊例 |
| Quantile loss | Asymmetric Laplace; quantile 后验 |
| KL (Variational) | 见 ch14 — ELBO 的 likelihood 项仍来自 MLE |