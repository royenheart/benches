# ch10 · 泊松过程与排队论速写

> 把指数分布与 Poisson 分布组合成时间过程; 排队论 M/M/1 与工程容量规划。

## 学习目标

- 推 Poisson 过程的计数 (Poisson) 与间隔 (Exp) 等价性
- 推 M/M/1 的稳态队长分布与 Little 律
- 用 numpy 模拟 Poisson 过程轨迹与到达间隔
- 算出 SLO 设计中"达到 P95 等待时间 ≤ X ms"的 service rate 估计
- 解释 Little 律 ρ = λ W 的工程意义

## 场景
1. **API 限流**: 请求到达率为 λ req/s; 设 service rate μ; ρ=λ/μ 要 < 1
2. **容量规划**: 给 P95 等待 ≤ 200ms 求所需 server 数
3. **后台任务调度**: burst arrival 处理的 backlog 概率

## 参考
- Stat 110 §13.1-13.3
- Bertsekas §6.1-6.3
- Murphy §19.4