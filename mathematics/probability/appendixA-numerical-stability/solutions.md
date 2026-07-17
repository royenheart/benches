# appendixA · 答案骨架

## Q1 hint
```python
import numpy as np
from scipy.special import logsumexp
def my_lse(x):
    a = np.max(x)
    return a + np.log(np.sum(np.exp(x - a)))
x = np.array([1000.0, 1001.0])
print("mine:", my_lse(x), "scipy:", logsumexp(x))
# 应一致 1001.31..
```

## Q2 hint
```python
import numpy as np
from scipy.special import rel_entr
def kl_log(logp, logq):
    p = np.exp(logp); q = np.exp(logq)
    p /= p.sum(); q /= q.sum()
    logp = np.log(p + 1e-300); logq = np.log(q + 1e-300)
    return np.sum(np.exp(logp) * (logp - logq))
logp = np.log(np.array([0.3, 0.7]))
logq = np.log(np.array([0.5, 0.5]))
print("kl_log:", kl_log(logp, logq))
print("rel_entr:", np.sum(rel_entr(np.exp(logp), np.exp(logq))))
# q 接近 0 时:
logq2 = np.log(np.array([1e-50, 1 - 1e-50]))
print("kl with small q:", kl_log(logp, logq2))
```

## Q3 hint
fp16 最小 sub-normal 5.96e-8; 梯度 < 这个会变 0. Loss scaling 让梯度幅阈值乘 S; 反向后再除. S=1024 后 underflow 阈值变 6e-11.

## Q4 hint
推导: `CE(logits, target) = -log_σ_target = -logits[target] + LSE(logits)`. logits - max 是 LSE 内部减; 在 forward / backward 都稳. PyTorch 实现内部接 `F.log_softmax(logits)[target]` + negation; 自身 `log_softmax` 已用 LSE trick.

## Q5 hint
在 ch14 VAE `vae_loss` 改为:
```python
logvar = torch.clamp(logvar, -10, 10)
kl = 0.5 * torch.sum(mu.pow(2) + logvar.exp() - 1 - logvar)
```
观察训练初期不再 NaN; KL 略偏 but stable ELBO 下降.