# ch07 · 课后题

## Q1 · 次序统计量精确 PDF
设 $X_1, ..., X_{10}$ iid Uniform(0,1). 写 X_(5) 的 PDF 公式并数值模拟验证 mean / var。

## Q2 · Bootstrap median CI 与 BCa
improve 给一段 Bootstrap median CI 实现 + 简易 BCa 实现: 同时输出 percentile 与 BCa CI 在重尾 Exp(scale=2.0), n=50, B=5000. 比较两者宽度与偏度.

## Q3 · AUC Bootstrap
用 score_pos ~ Normal(0.5, 0.4), score_neg ~ Normal(0.2, 0.4), n_pos=n_neg=50; 用 Bootstrap B=2000 给 AUC 95% CI. 给一段代码与结果数。

## Q4 (进阶) · 小样本 bootstrap 失稳
模拟 N=5, B=50000 在 Normal(0, 1) 上 mean; bootstrap CI 的覆盖率 vs 真值 (再独立 reload 反复) 是多少? Compare to N=50 — 揭示样本量在 Bootstrap 的稳定需求.

## Q5 (实战) · A/B test + Bootstrap A/B
设计 baseline 与候选, 各 2000 用户. CTR 差多少? mean - "0.001±0.001". Bootstrap CI 互, compare 者进取策略. Code 应包含: random seed, trial_ids 划分, boot B > 5000, output final decision: ≥ 95% CI 示不跨 over 0 ".