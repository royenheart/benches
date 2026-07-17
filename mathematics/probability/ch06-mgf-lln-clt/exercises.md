# ch06 · 课后题

## Q1 · 标准化 Bernoulli 收敛
设 X_i ~ Bern(0.4) iid, n=100. 写一段代码画 1000 次复跑 X̄ 的归一化直方 (减 μ 除 σ/√n) 并对比 N(0,1) PDF.

## Q2 · Hoeffding 决策
若 X_i ~ Uniform[-1, 1], 求 n 使均值估计误差 < 0.02 以 99% 概率. 用 Hoeffding 给上界 vs Monte Carlo 验证之。

## Q3 · 指数样本 - CLT 仍稳?
取 Exp(1) n=10 时, 比较理论 $\\bar X_n$ 分布 vs Normal CLT 近似. 写 KS = max(|empirical - normal cdf|), 报出. 试 n=10, 100, 1000 看 KS 减小.

## Q4 (进阶) · 重尾 Cauchy 不收敛
生成 Cauchy 样本 10000 个, 多次 (100 次) take mean — 看分布. 与你 N(0,1)/√n 假设差几倍. 写一段文字结论。

## Q5 (实战) · 法 Hoeffding 造停止规则

写一个 in-line estimator 接受事件流 (mean μ true 未知)，每收到 100 个观测就一起归并; 每次检查 Hoeffding 边给"若 |x̄_obs - μ|<0.05"持续 100 帧就停 — 你需要写停下决策的操作器。也就是监控 stop condition 是 "Hoeffding 给保证 μ in 区间 [\hat μ - 0.05, \hat μ + 0.05] 不少于 95% ".