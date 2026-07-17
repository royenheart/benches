# ch11 · 课后题

## Q1 · KL 非对称
p = [0.1, 0.4, 0.5], q = [0.3, 0.3, 0.4]. 计算 KL(p||q) 和 KL(q||p); 验证不对称且都 ≥ 0.

## Q2 · 互信息与独立
设 X ~ N(0,1), Y = X². 计算 (a) Corr(X, Y) (~0); (b) discretized MI (20 bins). 试 X 含多少噪声后 MI 降到 ~0.1.

## Q3 · 交叉熵 = H(p) + KL
写一段代码: p 真分布 Bernoulli(0.3); 模型 q ∈ {0.1, 0.3, 0.5}; 算 H(p), KL(p||q), CE(p,q); 验证 CE = H(p) + KL.

## Q4 (进阶) · KL 链式
构造 joint p(x,y)≠q(x,y) 但 marginal p(x)=q(x); 验证 KL(p||q) = E_p[KL(p(y|x)||q(y|x))]. 数值模拟.

## Q5 (实战) · MI 特征筛选
造 数据 N=2000, D=20 中 5 个为真实 signal feature, 其余冗余/噪声; 用 MI 排序 vs |corr| 排序; 报 precision@5 的差别.