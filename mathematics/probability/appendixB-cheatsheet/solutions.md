# appendixB · 答案骨架

## Q1 hint
1. 在线 CTR 每周 → Beta-Binomial 共轭, 在线 Beta 更新; CrI = `scipy.stats.beta.ppf([0.025, 0.975], α+k, β+n-k)`
2. 回归像素 → Normal N(μ, σ²) with MLE (MSE loss); σ² 用无偏估计 ddof=1
3. API P95 延迟 vs SLO → M/M/1 analytic (ρ<0.8 设计); Bootstrap 给 P95 经验 CI; Gamma/log-normal 拟合用以发现延迟重尾

## Q2 hint
- VAE (forward KL(q‖p)): mass-covering, q 在 p 高密度处不漏 mode (conjugate = ELBO 形式)
- EM (reverse KL(p‖q)): mode-seeking, 经典 EM 的 E-step 给 Q(z) ≈ posterior
- Diffusion:score matching 接近 forward KL 的隐式; DDPM 最终降噪的 score 函数本身就是 forward KL 的梯度

## Q3 hint
5 行 RNG header 模板:
```python
# ---- RNG header ----
# SEED: 20240717
# RNG sources in this script: np.random.default_rng(SEED), torch.manual_seed(SEED)
# CUDA determinism: torch.use_deterministic_algorithms(True) if needed
import numpy as np, torch
SEED = 20240717
rng = np.random.default_rng(seed=SEED)
torch.manual_seed(SEED)
```

## Q4 hint
差别:
- 分类: Bernoulli/Categorical likelihood → MLE = BCE/CE loss
- A/B 测试: Beta-Binomial 共轭 → closed form 更新, 不需训练
- LLM 对齐: BT/PL preference 的隐含 reward, 推断 → 用比重 log π_θ(y_w|x) − log π_θ(y_l|x)
相似: 三者都要报 CI/CrI; 三者都用 likelihood 启动贝叶斯/频率派决策

## Q5 hint (1 页 cheat sheet 骨架)
```
# 概率建模 cheat sheet

## RNG header (每脚本开头)
SEED = 20240717
rng = np.random.default_rng(SEED)
torch.manual_seed(SEED)

## N<1000 时的分布选择
- 已知共轭族 (Beta-Binomial/Gamma-Poisson/Normal-Normal) → closed-form
- 共轭不可用 → Bootstrap CI (ch07)
- 需要 prior 表达 → numpyro NUTS (ch13)

## CI/CrI 报告:
- frequentist CI 用: percentile + BCa (ch07)
- Bayesian CrI 用: posterior 2.5 / 97.5 分位 (ch12)

## 默认 loss 对应:
MSE → Normal MLE; BCE → Bernoulli MLE; CE → Categorical MLE
```