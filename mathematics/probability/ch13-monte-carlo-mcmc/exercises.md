# ch13 · 课后题

## Q1 · 拒绝采样自 Beta(7, 3)
提议 q=Uniform(0,1)。给 Beta(7,3) 的最大密度 M 与接纳率。仿真 10000 个样本验证 mean/var。

## Q2 · 重要性采样示算
π=N(2, 1), q=N(0, 5)，g(x)=x²。求 E_pi[g]; 重要性采样估; 报 ESS。

## Q3 · MH RW on Beta(3, 4)
写 RWMH 在 Beta(3, 4) target 上, σ=0.1, 0.3, 0.5; 报:
1. 接受率
2. ESS
3. 哪种 σ 给出最佳混时间

## Q4 (进阶) · MH 在 multi-mode
画 target: 0.5*N(-3, 0.5²) + 0.5*N(3, 0.5²)。RWMH 取 σ=0.3 跑 50k 步, 给效率与 ESS; 尝试 HMC (numpyro NUTS) 给它跑同样 sample size, 比较 ESS。

## Q5 (实战) · 重要性采样加权历史数据
假设有 baseline policy 收的 reward 100k 条样本 r_i, contexts c_i (变量维度 D=5); 想估新 policy π_new(c) 下 E[r]; 写 importance sampling 估计 + standardized mean。提示: 给 target/prop = π_new(c) / π_old(c); 计算权重; self-normalize; 给 variance-bound ESS 与 SE.