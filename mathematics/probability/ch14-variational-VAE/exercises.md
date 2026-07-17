# ch14 · 课后题

## 基础

### Q1 · 手写 `rsample()` 等价

不使用 `torch.distributions.Normal(...).rsample()`，自己定义函数 `reparam(mu, log_var)`，输入为 `(mu, log_var)` 的张量，返回 `z = μ + σ·ε`，其中 $\\epsilon \\sim \\mathcal N(0, 1)$。要求：
1. 数学严格可导
2. 在 backward 时梯度能传回 (μ, log_var) — 写一段验证代码：用 `z.sum().backward()` 看 (μ, log_var) 的 `.grad` 是否非零。

### Q2 · β-VAE 复现

把 notebook 中 `betas = [0.0, 0.5, 1.0, 4.0]` 改为 `betas = [0.0, 0.25, 1.0, 2.0, 10.0]`。要求：
1. 把 5 个 final KL/BCE 输出列表
2. 用 matplotlib 画 (β, final_KL) 双对数图
3. 用观察印证过压过低的 posterer collapse 在哪个 β 开始

### Q3 · 监督 latent dim 扫描

跑 latent_dim ∈ {2, 4, 8, 16, 32} 并记录 epoch=1 后的最终 ELBO 值。然后画 (latent_dim, ELBO) 曲线。

## 进阶

### Q4 · 等 divergences

VAE 用 forward KL `KL(q‖p)`。如果改用 reverse KL `KL(p‖q)`（reverse-KL），数学上当 $q_\\phi$ 拉向 p, 会倾向哪种行为（mass-covering vs. mode-seeking）？请用 2D 高斯对高斯示例画图对比两种 KL 选 q 时 q 形态。

## 工程实战

### Q5 · 解 Posterior Collapse

让 notebook 中 decoder 故意过简 (单层 32 维 hidden)，再跑 epoch=1，观察 KL 是否 collapse 到 ≈0。然后实现 free-bits trick：每步 KL per latent dim 当低于 threshold 时把该维度 KL 锁住不计入 loss。报告：
1. 修复前 final KL 值
2. 修复后 final KL 值
3. 重建按键 110 最终 BCE 改善是几 %