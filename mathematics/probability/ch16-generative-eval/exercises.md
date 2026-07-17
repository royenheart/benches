# ch16 · 课后题

## Q1 · FID 在真实高斯下解析
设真分布 N(μ1, Σ1), 生成 N(μ2, Σ2). FID 的闭式表达 (公式). 当 μ1=μ2、Σ1=Σ2 时 FID = 0. 取 μ1=0, μ2=0.5*[1,1], Σ1=I, Σ2=1.2*I, 求 FID 数值.

## Q2 · IS 在 mode collapse 中
按 ch16 cell 第 7 的对照实验, 改成 5 个 class: case A 每 sample dirichlet(α=1) (均匀), case B 每 sample 简同 one-hot(x→0). 给两个 IS 数值与差异.

## Q3 · KL forward/reverse 教学版
取真 p = 0.5N(-3, 0.4²) + 0.5N(3, 0.4²). 拟合一单 gauss N(μ, σ²), 用 forward 与 reverse KL 估汲 (μ, σ²), 提供代码与可视化对照 mass-covering-vs-mode-seeking.

## Q4 (进阶) · FID 与 N 的关系
对 200-d Gaussian features 取 N=[2000, 5000, 10000, 50000]: FID estimated 与 closed FID 的误差对 N 的依赖是? 写一段 simulate.

## Q5 (实战) · 多样性 vs 质量 trade-off
某 GAN 输出 N=1000 样本. 在 InceptionNet pool3 feature 4000 个 true 样本与 1000 fake 样本上年报 FID. 改 epoch 5/20/50 看 FID 下降 vs sample 列表"视觉 quality". 写一段报告: "FID 一直降但人眼觉得越来越像" 或反例.