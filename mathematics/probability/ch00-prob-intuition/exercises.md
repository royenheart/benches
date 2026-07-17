# ch00 · 课后题

> 建议至少做完 3 道基础题再进 ch01。
> 全部代码用 `uv run --extra probability jupyter lab` 起一个 kernel 即可跑。

## 基础

### Q1 · 闭式与数值

设 `X ~ Bern(0.4)`。理论 $E[X], \\mathrm{Var}[X]$ 是多少？再写一段 numpy 采 100000 个样本，报告样本均值与样本方差（ddof=1），看 4 位有效数字是否吻合闭式解。

**输出**：两个数对（理论 vs 经验）。

### Q2 · 收敛速度随 p

固定 `n = 10000`，让 $p \\in \\{0.01, 0.05, 0.1, 0.3, 0.5\\}$ 取值，每个 p 重复 1000 次（即每次采 n 个 Bernoulli）。对每个 p：

1. 算 1000 个 $\\hat p$ 的样本均值与样本标准差；
2. 把样本标准差与理论值 $\\sqrt{p(1-p)/n}$ 比较。

**问**：什么 p 下边界处的标准差最小（最稳定）？

### Q3 · 用种子的好姿势

写一段满足以下三点的脚本：

1. 全局只用一个 `default_rng(seed=...)`；
2. 先抽 array A = `rng.integers(0, 100, size=10)`，再抽 B = `rng.standard_normal(size=5)`；
3. 第二次用同一 seed 重启 `rng2`，预测 A 和 B 的值；用 `assert` 验证两次结果一致。

**输出**：A 和 B 的具体值，以及一段 assert 通过的提示字符串。

## 进阶

### Q4 · 几何概率而成

单位圆内随机投点（均匀分布子经度 vs 余弦均匀纬度）。问点离圆心距离小于 $0.5$ 的概率 $P(r < 0.5) = ?$。要求：

1. 解析推导（提示：均匀圆盘上 $r \\in [0, R]$ 的边缘 pdf 是 $2r/R^2$）；
2. 用 numpy 采样 1000000 个均匀点，用频率估概率。两者吻合到第几位？

把你的解析与 numpy 代码贴出来。

## 工程实战

### Q5 · benchmark 报告的 RNG 头部

设想你要写一个跨微基准重复实验的报告。要求：

1. 每次重复都给一个 seed（有 list）；
2. 整份报告总览有一段实现："本报告所有随机来源均由 `np.random.default_rng(seed=MASTER_SEED)` 派生。MASTER_SEED=20240717"。
3. 把运行 5 次 microbenchmark 计算结果（每次跑出 mean / p50 / p99）以 markdown 表达表呈现。

约束：用 `default_rng` 创建一个 master，再用 `master.spawn(5)` 给每次派生 child generator；你不能给每次手打 `default_rng(seed=…)`。报告里印出 `master.spawn` 的 5 个 bit_generator 的子种子，便于别人验证。

把你的 README + 代码贴出来；目标不只是可重现，而是**修正别人凭直觉想再跑了的事**。