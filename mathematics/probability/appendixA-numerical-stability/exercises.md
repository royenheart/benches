# appendixA · 课后题

## Q1 · log-sum-exp 替代
不用 `scipy.special.logsumexp`, 自己实现 logsumexp with max-subtract trick. 验证在 x=[1000, 1001] 处与 scipy 一致.

## Q2 · 减 KL overflow
写一段 KL 数值稳定估计 in log-domain (input: logp, logq). 给 q 极小 < 1e-30 是否仍稳; 给出 与 scipy.special.rel_entr 对比.

## Q3 · fp16 训练
某 loss=1e-7. 解释 fp16 中为何梯度会 underflow; 给出 loss scaling 系数 S=1024 后, 梯度幅值范围变化.

## Q4 (进阶) · Softmax backward 稳定性
推导 softmax backward: 当 logits 接近 max 时的隐性 LSE 减常数. 解释 PyTorch 中 `F.cross_entropy` 内部做法.

## Q5 (实战) · VAE 中的 KL NaN 防御
回到 ch14 VAE. 写一段 clamp `logvar` 在 `[-10, 10]` 后训 vs 原版, 看 KL 与 ELBO 是否能在值范围极端时稳 定下来.