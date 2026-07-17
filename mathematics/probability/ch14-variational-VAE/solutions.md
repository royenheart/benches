# ch14 · 课后题答案

## Q1 · 手写 reparam

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class SimpleEncoder(nn.Module):
    def __init__(self, in_dim=784, h=64, lat=8):
        super().__init__()
        self.fc1 = nn.Linear(in_dim, h)
        self.fc_mu = nn.Linear(h, lat)
        self.fc_logvar = nn.Linear(h, lat)

    def forward(self, x):
        h = F.relu(self.fc1(x))
        return self.fc_mu(h), self.fc_logvar(h)


def reparam(mu, log_var):
    std = torch.exp(0.5 * log_var)
    eps = torch.randn_like(std)
    return mu + std * eps

# Verification
torch.manual_seed(0)
enc = SimpleEncoder()
x = torch.randn(64, 784)
mu, log_var = enc(x)
z = reparam(mu, log_var)
z.sum().backward()

print("mu.grad not None:", mu.is_leaf, " grad is not None")
# Note: 因为 mu 是 intermediate output，is_leaf=False，需查 enc.parameters() grad:
g_mu = enc.fc_mu.weight.grad
g_lv = enc.fc_logvar.weight.grad
print("fc_mu weight grad max:", g_mu.abs().max().item())
print("fc_logvar weight grad max:", g_lv.abs().max().item())
# Both must > 0
```

期望：fc_mu 与 fc_logvar 均非零 grad（说明 reparam 的 backward 通过）。

## Q2 · β-VAE 复现 — hint

- 直接改 notebook 中 `betas` 列表，重跑 last cell
- 双对数图：`plt.loglog(betas, final_kls, "o-")`
- 经验：β≥4 已经 regime-changing（KL→0），Q2 中具体观察到的看你电脑。报告可见 **posterior collapse 典型 β threshold 约在 β=5-10 之间**

## Q3 · latent dim scan — hint

```python
results = []
for lat in [2, 4, 8, 16, 32]:
    m = VAE(latent_dim=lat).to("cpu")
    h = train_vae(m, get_train_loader(128), n_epochs=1)
    results.append((lat, np.median(h["loss"][-50:])))

import matplotlib.pyplot as plt
lats = [r[0] for r in results]
losses = [r[1] for r in results]
plt.plot(lats, losses, "o-")
plt.xlabel("latent dim"); plt.ylabel("ELBO loss (per sample)")
plt.title("ELBO vs latent dim (1 epoch)")
plt.show()
```

期望：loss 随 dim 增加单调下降，但有 amortization bottleneck（圆过10+ 不再显著降）。

## Q4 · forward vs reverse KL — hint

forward KL (q 在前)：mode-seeking 模式下 q 抗拒 zero-region → mass-covering；reverse KL (p 在前)：mode-seeking q 朝 modes 拉丢掉其它 mode。

代码骨架：拿 `multivariate_normal.pdf` 之 contour 配以 `minimize` over (μ_q, σ_q)；分别用两种 KL 闭合公式。
闭式解均在 stats 上容易推：
- Forward KL：`0.5*(mu_q - mu_p)^2 / sigma_p^2 + log(sigma_p/sigma_q) + (sigma_q² / sigma_p² − 1)/2`
- Reverse KL：`0.5*(mu_p - mu_q)^2 / sigma_q^2 + log(sigma_q/sigma_p) + (sigma_p² / sigma_q² − 1)/2`

## Q5 hint · free bits

关键是 per-dim KL 计算 + clip mask:

```python
def vae_loss_free_bits(x, x_logits, mu, logvar, kl_min_per_dim=0.5, beta=1.0):
    bce = F.binary_cross_entropy_with_logits(x_logits, x, reduction="sum")
    # per-dim KL
    kl_per_dim = 0.5 * (mu.pow(2) + logvar.exp() - 1 - logvar)  # shape (batch, lat)
    kl_masked = torch.where(
        kl_per_dim > kl_min_per_dim,
        kl_per_dim,
        torch.full_like(kl_per_dim, kl_min_per_dim),
    )
    kl = kl_masked.sum()
    return bce + beta * kl, bce.item(), kl.item()
```

记录对比前 final KL ≈ 0、final KL ≈ lat * 0.5 * batch_size。重建 BCE 不会明显变差（free bits 因为给 latent dimension 自由度，重建还会好起来）。