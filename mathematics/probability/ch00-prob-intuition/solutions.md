# ch00 · 课后题答案

仅给 3 道基础题的关键 hint 与代码骨架；进阶与工程实战答案不唯一，鼓励自行探索。

## Q1 · 闭式与数值

理论解：

$$E[X] = p = 0.4, \\quad \\mathrm{Var}[X] = p(1-p) = 0.24$$

代码骨架：

```python
import numpy as np
from scipy.stats import bernoulli

p = 0.4
n = 100_000
rng = np.random.default_rng(seed=20240717)
x = bernoulli.rvs(p=p, size=n, random_state=rng)
print("theoretical mean:", p)
print("sample mean:     ", x.mean())
print("theoretical var: ", p * (1 - p))
print("sample var (ddof=1):", x.var(ddof=1))
```

期望输出：理论 0.4 / 0.24，样本均值的差异在 0.001 量级，样本方差差异在 0.001 量级；n 越大越准。

## Q2 · 收敛速度随 p

关键 hint：p=0.5 时方差 $p(1-p) = 0.25$ 最大；p 越接近 0 或 1 方差越小。

代码骨架：

```python
import numpy as np

n = 10_000
n_repeat = 1000
ps = [0.01, 0.05, 0.1, 0.3, 0.5]
rng = np.random.default_rng(seed=20240717)

for p in ps:
    samples = rng.binomial(n=1, p=p, size=(n_repeat, n))
    p_hats = samples.mean(axis=1)
    emp_std = p_hats.std(ddof=1)
    theory_std = np.sqrt(p * (1 - p) / n)
    print(f"p={p:.2f}  std empirical={emp_std:.6f}  std theory={theory_std:.6f}")
```

结论：p=0.01 时标准差最小（小一个量级）；p=0.5 时最大。但**相对误差** $\\mathrm{CV} = \\mathrm{std}/p$ 反而是 p 越小越大，这影响小事件概率估计需要更多样本数。

## Q3 · 用种子的好姿势

代码骨架：

```python
import numpy as np
from numpy.random import SeedSequence, default_rng

# master 推两次
master = default_rng(seed=20240717)
A1 = master.integers(0, 100, size=10)
B1 = master.standard_normal(size=5)

# 重建
master2 = default_rng(seed=20240717)
A2 = master2.integers(0, 100, size=10)
B2 = master2.standard_normal(size=5)

assert np.allclose(A1, A2)
assert np.allclose(B1, B2)
print("A =", A1)
print("B =", B1)
print("OK: 同一种子重起后输出与首次一致")
```

**注**：用 `default_rng(seed=...)` 创建新实例即重置流；不能用 `np.random.seed(...)` 因为这操作的是单例 global state。

## 进阶 Q4 提示

解析：对 r 求概率 $P(r < 0.5) = \\int_0^{0.5} \\frac{2r}{R^2} dr = \\frac{0.25}{R^2}$；R=1 时 $P = 0.25$。

样本实现要点：要均匀采样圆盘上的点（不是均匀角度 + 均匀半径），否则得到的不是均匀圆盘采样。正确做法：

```python
# 在单位圆盘上均匀采样
sample_r = np.sqrt(rng.uniform(0, 1, size=N))  # 边缘 r 的 cdf: r² -> u
sample_theta = rng.uniform(0, 2 * np.pi, size=N)
# 计数 r < 0.5
frac = (sample_r < 0.5).mean()
print("frac:", frac, "theoretical 0.25")
```

## 实战 Q5 hint

`master.spawn(n)` 不是 numpy 的 API；正确写法是：

```python
from numpy.random import SeedSequence, default_rng
ss = SeedSequence(20240717)
children = ss.spawn(5)
generators = [default_rng(c) for c in children]
print("child entropy:", children[0].entropy, "... 5 个")
```

把每个 child 的 entropy 与 `load_state` 打印出来，便于读者用一句 `numpy.random.default_rng(entropy)` 重启。

报告骨架：

```markdown
## RNG 头部
Master seed = 20240717
5 个子进程派生自 SeedSequence.spawn(5)：

| run | child entropy |
|---|---|
| 1   | <填充>  |
| ... | ... |

## 结果

| run | mean (ms) | p50 (ms) | p99 (ms) |
|---|---|---|---|
| ... | ... | ... | ... |
```