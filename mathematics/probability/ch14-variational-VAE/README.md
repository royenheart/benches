# ch14 · 变分推断、重参数化、ELBO 推导

> Phase 4 的中部章节：把"贝叶斯后验太难求 → 用一个参数族去近似它"这条工程路线从直觉、公式、训练循环挖到底，能在 CPU 上跑出可看的 VAE。
> 看完这一章你能独立写出 ELBO 损失函数、解释 reparameterization trick 为什么让梯度能回传、动手实现一个最小 VAE 并诊断 posterior collapse。

## 学习目标

- 用 latex + sympy 推 ELBO 的两种分解（Jensen 形式 + KL 分解形式），并说清两种形式为什么会得到同一个目标
- 推导任意 q~N(μ_q, σ_q²) 对 p~N(0, I) 的 KL 散度闭合解 `0.5(σ_q² + μ_q² − 1 − log σ_q²)`
- 用 numpy Monte-Carlo 验证该闭合解（采样数 → 收敛到 closed form）
- 用 PyTorch 跑通 MNIST 上的 VAE（编码器+解码器+reparam 一体），看重建图与 latent 网格
- 在 beta-VAE 中改变 β 观察重建精度 vs latent 解耦的 Zusammen 拉锯
- 在 第一 cell 看到 Posterior Collapse 现象并说明 mitigation 之一（free bits）

## 三个能立刻解决的场景

1. **写 VAE 时算 KL**：编码器输出 `(μ, log σ)`，loss KL 项就该写 `−0.5 * sum(1 + log σ² − μ² − σ²)` 这种平均 over batch 的闭合式 — 不应 Monte-Carlo
2. **β-VAE 调参**：当 KL 太大占据整损失 — 你都知道这是 posterior collapse 还是 over-regularization
3. **next-step 进 Diffusion**：知道了 ELBO 与采样几何 关系，进 ch16 diffusion 看 DDIM / ODE 论文时不再卡住

## 参考课程位置

- Kingma & Welling 2014 *Auto-Encoding Variational Bayes* — VAE 主原论文
- Higgins 2017 *β-VAE* — KL 系数作为正则超参
- Murphy *PML Vol.1* §10.1 — 七节变分推断综述

## 文件清单

| 文件 | 作用 |
|---|---|
| [`notebook.ipynb`](notebook.ipynb) | 主讲：ELBO 推导 + 闭合 KL 验证 + MNIST VAE demo + β-VAE 对比。CPU 上 1 epoch 约 60 秒。 |
| [gen.py](gen.py) | 笔记本源描述。 |
| [exercises.md](exercises.md) | 5 道分级题。 |
| [solutions.md](solutions.md) | 基础 3 题关键代码骨架。 |