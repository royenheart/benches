# ch09 · 课后题

## Q1 · 2 状态 Markov 与混时间
构造 2 状态对称 Markov 链 P=[[0.9, 0.1],[0.1, 0.9]], 从状态 0 出发, 模拟 5000 条 trajectory N=200 步; 画出 P(X_n=0) 随 n 变化 vs 解析 (1/2(1 + 0.8^n)). 求混时间.

## Q2 · PageRank 自造
构造 8 节点图: 1->2->3->1, 4->5, 5->6->4, 7->8, 8->7, plus random cross edges 1->4, 2->5, 3->7. 求 d=0.85 下 PageRank 与 d=0.95 下; 对比排序.

## Q3 · Detailed Balance 验
构造一条三状态链满足 detailed balance: π=[0.2, 0.5, 0.3], 设 P[0,1]=0.4. 反推 P[1,0]; 自由选 P[0,2]=0.1, 反推 P[2,0]; 写代码构造该 P + 验证 row sums=1 加上 πP_immutable=π.

## Q4 (进阶) · 非周期重要性
构造 irreducible 但周期 d=2 的链 (例如二分图); 从 δ_0 出发看 P_n(0,0) 的极限 - 不收敛.

## Q5 (实战) · MCMC 验证
离散目标分布 p = [0.1, 0.2, 0.4, 0.3]. 用 Metropolis 算法构造满足 detailed balance 的 P; 模拟 100k 步看经验频率 vs 解析.