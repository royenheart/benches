# ch09 · 马尔可夫链: 平稳分布、细致平衡、收敛

> 引入时间相依随机过程; PageRank、MCMC 与强化学习中的状态转移统一就此章基。

## 学习目标

- 写出 Markov 性质 + 转移矩阵 + 平稳分布 + 不可约 + 非周期定义
- 用细致平衡 (detailed balance) 推平稳分布; 解释这是 MCMC 的根基
- 用 networkx 可视化 4 状态 Markov 链 + 收敛轨迹
- 写一段 PageRank 数值实现并验证
- 解释 mixing time 与 spectral gap 的关系

## 场景
1. **PageRank**: 网页作为状态, 链接作为转移; 平稳分布给权重
2. **MCMC**: 通过精心设计的转移矩阵让平稳分布 = 目标分布后验
3. **强化学习**: 状态转移矩阵定义 MDP 动力学; 价值迭代是它的收敛定理

## 参考
- Stat 110 §12.1-12.5
- Bertsekas §7.1-7.4
- Murphy §19.1 (MCMC)