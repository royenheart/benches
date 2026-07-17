# ch03 · 课后题

## 基础

### Q1 · 重试与中兴
某 ML API 每次响应成功概率 p=0.9；最多 3 次重试。失败概率是几？用 Bern/Geom 推公式。

### Q2 · Poisson 抵达
某小区平均每周收 3.5 个外卖。用什么分布？求周收外卖 ≥ 5 个概率。

### Q3 · NegBin r 次成功
spells 当中每次拾取一个稀有 item 概率 p=0.05；求拾到 5 个所需尝试 ≥ 100 次的概率。

## 进阶

### Q4 · 重尾 vs Poisson
写段代码仿真 (a) Pois(λ=3)；(b) NegBin(r=3, p=0.3)。两者均值接近吗？方差呢？画直方图区别。给出生成负二项的两条独立有限ckill发明：Poisson-Gamma mixture vs 几何分布求和。

## 实战

### Q5 · A/B 测试伯努利模型
你给某页面两版 A、B，用 1000 个 random user 跑 click tracking 错误计算标准误。要求：
1. 设 baseline CTR p_A = 0.10，推荐 alternative CTR p_B = 0.12
2. 实际抽 s 你假设两变体 under Bernoulli → CTR_diff's 标准误是多少？
3. 多少样本量让 5% 显著性双尾可检测 p_B - p_A = 0.02？用闭式不仿真。