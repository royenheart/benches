# ch05 · 课后题

## Q1 · Var(X+Y) 当 Cov 不为 0
设 X,Y 联合正态, mu_X=1, mu_Y=2, σ_X²=4, σ_Y²=9, ρ=0.4. 求 Var(X+Y) 和 Var(X-Y)。

## Q2 · 辛普森构造
设计一个 Python 模拟, 用 N=2000, 男女各一半, 经药品治疗, 男成功率 60%、女 55%, 但 Drug A 在男性集中, Drug B 在女性集中 — 通过构造两组样本, 验证 Simpson 反转。

## Q3 · confounder 通过偏相关
写一段代码: 给 N=2000 样本 (X, Y, Z) jointly normal, 真正因果 X→Y 被 Z 提供 spurious correlation. 控制 Z 后 partial correlation 接近 0。

## Q4 (进阶) · 非线性独立不相关
设 X ~ Uniform[-1, 1], Y = X². 写代码采样 + 计算 Corr(X, Y) 与 Corr(X, Y) === 0, 同时画出 X-Y scatter。

## Q5 (实战) · feature filter via correlation
写一段 sklearn-free 代码, 给 50 features, 部分为 label-relevant, 部分为冗余特征 (highly correlated 互相 copy); 做 pairwise correlation filter 去掉 duplicate; 用 cross-validation 计算 precision/recall of "保留 true signal" 集合。