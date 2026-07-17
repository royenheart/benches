# ch08 · 课后题

## Q1 · Exp MLE
设 X_i ~ Exp(λ), iid, n=200, λ_true=0.7。仿真求 MLE, 100 次重复估计 mean / var, 与 Cramer-Rao bound `λ²/n` 对比吻合到几位?

## Q2 · Normal MLE 方差有偏
n=20, X ~ N(0, 1). 计算 (a) sample var ddof=0 的均值; (b) ddof=1 的均值; 报告 bias 哪个更小.

## Q3 · MLE 渐近正态
对 Exp(λ=1.4) 取 n=[10, 50, 200, 1000]: 多次重复 (1000 次) MLE, 标准化 (减 λ_true 除 σ_MLE=√(λ²/n)) 后画 4 子图 hist vs N(0,1)。看 n 多大时形状契合.

## Q4 (进阶) · logistic MLE 数值
用 PyTorch LBFGS 求解 logistic MLE (现 gen.py 给的是 4 维)。把维度提升到 D=50, 真值 W 由 rng.normal(0, 1, D); 预测器 y_n = sigmoid(X_n @ W); 比起 100 次重复的 Frobenius matrix norm error.

## Q5 (实战) · 损失 = MLE 表
给出一个 reference 表: 列出 5 种机器学习损失函数 (MSE, BCE, AR-MSE, MAE, log-likelihood of Boltzmann) 与对应的 MLE 分布假设 (Normal, Bernoulli, L1, Normal-L1 即 Laplace, Softmax).