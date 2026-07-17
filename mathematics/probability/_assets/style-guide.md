# 符号与代码约定

## 数学符号统一表

| 符号 | 含义 | sympy/numpy 对应 |
|---|---|---|
| `X ~ F` | `X` 服从分布 `F` | `scipy.stats.<dist>` 实例 |
| `X ~ Bern(p)` | 伯努利分布 | `scipy.stats.bernoulli(p)` |
| `P(A)` | 事件 A 发生概率 | 标量 |
| `P(A \| B)` | 给定 B 时 A 的条件概率 | 标量 |
| `E[X]` | 期望 | `sympy.stats.E(X)` |
| `Var[X]` | 方差 | `sympy.stats.variance(X)` |
| `O_p(·)` | 概率阶 | 不常用代码化，仅在公式中 |
| `KL(p ‖ q)` | KL 散度 | `scipy.special.rel_entr` 或闭式解 |
| `N(μ, σ²)` | 正态分布 | `scipy.stats.norm(loc=μ, scale=σ)` |
| `Beta(α, β)` | Beta 分布 | `scipy.stats.beta(α, β)` |
| `q_θ(z \| x)` | 编码器分布（变分推断） | `torch.distributions` 实例 |
| `H[p]` | 香农熵 | `-Σ p*log p` |
| `I(X; Y)` | 互信息 | 数值估计 |

## 术语对照

- MLE / 最大似然估计 = Maximum Likelihood Estimation
- MAP / 最大后验估计 = Maximum A Posteriori
- CI / 置信区间 = Confidence Interval
- CrI / 可信区间 = Credible Interval（贝叶斯）
- HMC / 哈密顿蒙特卡洛 = Hamiltonian Monte Carlo
- MCMC / 马尔可夫链蒙特卡洛 = Markov Chain Monte Carlo
- ELBO / 证据下界 = Evidence Lower Bound
- VI / 变分推断 = Variational Inference
- KL 散度 / 相对熵 = Kullback-Leibler Divergence
- RNG / 随机数生成器 = Random Number Generator
- ODE / 常微分方程 = Ordinary Differential Equation

## 代码约定

- **Python ≥ 3.10**；字符串双引号；行宽 100。
- 导入排序：标准库 → 第三方 → 本地（`mathematics/...`）；分组之间空行。
- **显式种子**：所有 RNG 用 `numpy.random.default_rng(seed=...)`；不要混用全局 `numpy.random.seed`。
- **matplotlib**：统一 `fig, ax = plt.subplots(figsize=..., dpi=...)`；标题与轴标签含单位；颜色优先考虑色盲友好（与默认 tab10 即可）。
- **sympy**：标记性推导展示时显式 `.simplify()` / `.doit()`。
- **scipy.stats**：分布用 `dist.rvs(size=..., random_state=rng)` 而非 `np.random.*` 直接抽。
- **torch**：CPU 默认；`torch.device("cpu")`；所有 cell 在 CPU 上能在 600s 内跑完 1 epoch。
- **变量命名**：小写下划线；分布参数 `p_bern` / `mu_q` / `sigma_q`；估计器带 `hat`（`mu_hat`）。
- **公式输出**：单 cell 中尽量只保留输出 1 张图，避免被 `repr` 文字淹没。
- **跨 cell 引用**：变量在前序 cell 定义；不要在 cell 中重新导入以避免冗余；出现重要状态在 markdown cell 复述。

## 笔记本结构（notebook.ipynb）

固定按 10 段骨架展开（详见 [`docs/specs/`](../../docs/superpowers/specs/) 与每章 README）：

1. Why this chapter（动机 + 3 个学后能解决的任务）
2. 直觉引入（图/类比先于符号）
3. 定义与公理（LaTeX + sympy）
4. 符号推导（sympy）
5. 数值验证（numpy/scipy.stats）
6. 可视化（matplotlib/networkx）
7. 工程案例 + 完整可跑代码
8. pitfalls（列表）
9. 课后题指引（链到 exercises.md）
10. 参考课程位置（Stat 110 §、Murphy §、MacKay §、Bertsekas §）

## 公式渲染

- markdown cell 用 LaTeX：`$P(A \mid B) = \frac{P(B \mid A)P(A)}{P(B)}$`
- 代码注释中避免 LaTeX；改用朴素 ascii：`P(A|B) = P(B|A) P(A) / P(B)`
- sympy 表达式不要求与 LaTeX 公式 byte 一致；只要数学等价。