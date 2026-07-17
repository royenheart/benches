# ch12 · 课后题

## Q1 · 共轭 Beta-Binomial 顺序无关于最终
先验 Beta(2, 5)。观察 (n=10, k=3) 然后再 (n=5, k=2). 验证两批顺序 (写一段 code 做 grid 后验对比) 与一次 batch $(n=15, k=5)$ 一致。

## Q2 · Normal-Normal 共轭
sigma²=4 已知, mu_0=0, tau²_0=9, n=20 样本均值 x̄=1.5。求后验 mean / var. 与频率派 sample CI 相比。

## Q3 · PyMC 诊断
对 ch12 notebook 里 trace 读 arviz `ess`, `rhat`。给一段代码把 `draws` 提升到 4000 看 rhat 是否仍为 1.0。

## Q4 (进阶) · Hierarchical 模型
设 10 个广告位的 click 数据 (clicks_i, impressions_i); 每广告位独立 CTR p_i ~ Beta(alpha, beta); 共享 (alpha, beta) ~ 弱先验。写 PyMC 多层模型; 给出 alpha/beta 后验与每 p_i 后验 95% CrI。

## Q5 (实战) · 在线 Beta-Binomial 引擎
写一个 `BayesianClickEngine` 类, 接收 (clicks, impressions) 流, 在每 observe 后内部共轭 update; 行为:
1. `update(k, n)` 一次: 更新内部 (alpha, beta)
2. `prob_better_than(p_other_engine)`: 返回 `P(this.p > other.p. posterior)`
3. `credible_interval(level=0.95)`: 返回 95% CrI 道具
计算 ≤ 50 行