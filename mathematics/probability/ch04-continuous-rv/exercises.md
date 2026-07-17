# ch04 · 课后题

## 基础

### Q1 · 指数无记忆验证
设 `X ~ Exp(1/2)`。写 numpy 抽 50000 个样本, 经验估计 `P(X > 5 | X > 3)`, 与解析公式 `exp(-(5-3)/2)` 吻合?

### Q2 · Gamma 加和闭合
若 `X_i ~ Exp(λ)` 独立 i=1..n, 求 `Y = sum_i X_i` 的分布与方差。给 numpy 验证 n=5, λ=0.2。

### Q3 · Weibull shape 物理意义
shape=1 时 Weibull 退化为哪种分布? 写出 PDF 与 λ 关系。

## 进阶

### Q4 · 三种分布拟合 API 延迟
从 web 服务 fake 5000 个 lognoronf.rvs(s=0.7, scale=120) 延迟样本, 用 Normal / Lognormal / Gamma 三种拟合, 计算 AIC, 比较三者 fit p99 哪个最稳。

## 实战

### Q5 · SLO 设计
设计 SLO "P95 延迟 ≤ 200ms 在 95% of 7 day 滑动时间窗"。用 ch04 案例 API 延迟样本估计 7-day 的 P95 与达不到 SLO 的概率 (在 lognormal 假设下)。
- 给出 95% CI 的方法
- 给出 N_samples=200 时的误差范围