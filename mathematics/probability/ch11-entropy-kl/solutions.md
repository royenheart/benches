# ch11 · 答案骨架

## Q1 hint
```python
import numpy as np
p = np.array([0.1, 0.4, 0.5]); q = np.array([0.3, 0.3, 0.4])
kl_pq = np.sum(p * np.log(p/q))
kl_qp = np.sum(q * np.log(q/p))
print(kl_pq, kl_qp)  # 都 ≥ 0, 不相等
```

## Q2 hint
```python
import numpy as np
rng = np.random.default_rng(seed=0)
N = 10000
X = rng.normal(0, 1, N); Y = X**2
print("Corr:", np.corrcoef(X, Y)[0,1])  # 应 ~0
def mi_disc(x, y, n_bins=20):
    joint, _, _ = np.histogram2d(x, y, n_bins); pxy = joint / joint.sum()
    px = np.histogram(x, n_bins)[0] / len(x); py = np.histogram(y, n_bins)[0] / len(y)
    pxy_safe = pxy[pxy > 0]; outer = (px[:,None]*py[None,:])[pxy > 0]
    return np.sum(pxy_safe * np.log(pxy_safe / outer))
print("MI:", mi_disc(X, Y))  # 显著大
# 加噪声降低:
for noise in [0.5, 1.0, 2.0]:
    Xn = X + rng.normal(0, noise, N)
    print(f"noise={noise}, MI:", mi_disc(Xn, Xn**2))
```

## Q3 hint
```python
import numpy as np
p = 0.3
for q in [0.1, 0.3, 0.5]:
    H_p = -(p*np.log2(p) + (1-p)*np.log2(1-p))
    kl = p*np.log2(p/q) + (1-p)*np.log2((1-p)/(1-q))
    ce = -p*np.log2(q) - (1-p)*np.log2(1-q)
    print(f"q={q}: H(p)={H_p:.4f}, KL={kl:.4f}, CE={ce:.4f}, H+KL={H_p+kl:.4f}")
    assert np.isclose(ce, H_p + kl)
```