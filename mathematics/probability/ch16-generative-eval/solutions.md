# ch16 · 答案骨架

## Q1 hint
```python
import numpy as np
from scipy.linalg import sqrtm
mu1 = np.zeros(2); S1 = np.eye(2)
mu2 = 0.5 * np.ones(2); S2 = 1.2 * np.eye(2)
diff = mu1 - mu2
FID = (diff**2).sum() + np.trace(S1 + S2 - 2 * sqrtm(S1 @ S2)[0])
print(f"FID closed = {FID:.4f}")
#  = ||0.5[1,1]||^2 + trace(I + 1.2I - 2*sqrt(1.2)I)
#  = 0.5 + (1 + 1.2 - 2*1.0954)*2 = 0.5 + 0.0183
```

## Q2 hint
仿照 ch16 第 7 cell case A/B; 把 K_class=5, α=1; 给 IS 二者差异。

## Q3 hint
见 gen.py 第 4 cell `best_fwd` 与 `best_rev` 扫描; 用 0.4 替 0.4 即可。
```python
import numpy as np
from scipy.stats import norm
import itertools
xs = np.linspace(-8, 8, 500)
p_true = 0.5 * norm.pdf(xs, -3, 0.4) + 0.5 * norm.pdf(xs, 3, 0.4)
best_fwd = (0, 1); fwd_inf = np.inf
for mu in np.linspace(-3, 3, 61):
    for sig in np.linspace(0.3, 10, 100):
        q = norm.pdf(xs, mu, sig)
        fwd = np.sum(q * np.log((q+1e-12)/(p_true+1e-12)))
        if fwd < fwd_inf: fwd_inf = fwd; best_fwd = (mu, sig)
print("Best forward KL:", best_fwd, "expect mass-cover near 0, σ>>1")
```

## Q4 hint
```python
import numpy as np
from scipy.linalg import sqrtm
mu_t = np.zeros(200); S_t = np.eye(200)
mu_f = 0.3 * np.ones(200); S_f = 1.2 * np.eye(200)
diff = mu_t - mu_f
FID_true = (diff**2).sum() + (200*1 + 200*1.2 - 200*2*np.sqrt(1.2))
print("FID closed:", FID_true)
rng = np.random.default_rng(seed=0)
for N in [2000, 5000, 10000, 50000]:
    xt = rng.multivariate_normal(mu_t, S_t, N); xf = rng.multivariate_normal(mu_f, S_f, N)
    est = (xt.mean()-xf.mean())**2
    S1 = np.cov(xt.T); S2 = np.cov(xf.T)
    fid = est.sum() + np.trace(S1+S2-2*sqrtm(S1@S2)[0])
    print(f"N={N:>6} FID_est={fid:.2f}, closed={FID_true:.2f}")
```

## Q5 hint (报告框架; 因本题为开放型)
- 报 NLL 与 sample 看
- 注意"眼睛觉得更好但 FID 反升" — 原因常见于: 在 N 较小时, sample 多样性低, FID 水涨船高; 检验 sample 数随 epoch 变化同。