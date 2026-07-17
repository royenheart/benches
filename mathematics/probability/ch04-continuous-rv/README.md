# ch04 · 连续型随机变量

> 把离散概率推到连续：从 PMF 换 PDF；理解均匀/指数/正态/Gamma/Weibull 的适用场景与寿命建模。

## 学习目标

- 区分 PDF、CDF、分位数
- 写出指数分布的**无记忆性**与由此推出的 M/M/1 排队基础
- 解释 Gamma 分布族如何统一指数与卡方
- 给 Weibull 当作寿命 / 可靠性模型的选择理由
- 用 SciPy 拟合正态到样本数据并测拟合

## 三个能立刻解决的场景

1. **SLO 窗口**：API P99 与 SLI 的"延迟寿命"模型选择
2. **服务时长**：M/M/1 → 指数无记忆性 是为什么排队论成立
3. **可靠性寿命**：硬盘 MTBF 与 Weibull 形状参数的关系

## 参考

- Stat 110 §5.1-5.3 + §8.1-8.2
- Bertsekas §3.1-3.2 + §6.1
- Murphy §2.5-2.6

## 文件

| 文件 | 作用 |
|---|---|
| [`notebook.ipynb`](notebook.ipynb) | 主讲 |
| [gen.py](gen.py) | 源 |
| [exercises.md](exercises.md) | 5 题 |
| [solutions.md](solutions.md) | 基础题 |