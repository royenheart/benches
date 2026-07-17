# 概率论专题

循循序晋渐进、章节独立、每章可跑、对接工业 AI 的概率论教程。

## 学习路径

- **快速入门（约 2-3 小时）**：ch00 → ch02 → ch08 第 1-3 段
- **基础课程（约 25 小时）**：Phase 0 → 1 → 2 → 3 + 附录 A
- **贝叶斯 + AI 应用（约 20 小时）**：Phase 4 全部 + 附录 B
- **完整路径**：约 50-60 小时；详细进度见 [`SUMMARY.md`](SUMMARY.md)。

## Phase 0 · 启程

| 章节 | 标题 | 状态 |
|---|---|---|
| [ch00 · 概率是什么 + 工作流落地](ch00-prob-intuition/) | 起点篇 | ✅ |
| [ch01 · 样本空间、事件、概率公理 + 排列组合](ch01-sample-space-axioms/) | ⬜ | ⬜ |

## Phase 1 · 基础公理与一维世界

| 章节 | 标题 | 状态 |
|---|---|---|
| [ch02 · 条件概率、贝叶斯定理、独立性](ch02-conditional-bayes/) | ✅ | ✅ |
| ch03 · 离散型随机变量 | ⬜ | ⬜ |
| ch04 · 连续型随机变量 | ⬜ | ⬜ |

## Phase 2 · 多维、极限与估计

| 章节 | 标题 | 状态 |
|---|---|---|
| ch05 · 联合分布、协方差、相关 vs 因果 | ⬜ | ⬜ |
| ch06 · 矩母函数、大数律、中心极限定理 | ⬜ | ⬜ |
| ch07 · 次序统计量、分位数、Bootstrap | ⬜ | ⬜ |
| ch08 · 参数估计：矩法、MLE、Fisher 信息 | ⬜ | ⬜ |

## Phase 3 · 随机过程与信息论碎片

| 章节 | 标题 | 状态 |
|---|---|---|
| ch09 · 马尔可夫链 | ⬜ | ⬜ |
| ch10 · 泊松过程与排队论速写 | ⬜ | ⬜ |
| ch11 · 熵、KL 散度、互信息、交叉熵 | ⬜ | ⬜ |

## Phase 4 · 贝叶斯与现代 AI 应用

| 章节 | 标题 | 状态 |
|---|---|---|
| ch12 · 贝叶斯推断基础 | ⬜ | ⬜ |
| ch13 · 蒙特卡洛族 | ⬜ | ⬜ |
| [ch14 · 变分推断、重参数化、ELBO 推导](ch14-variational-VAE/) | ✅ | ✅ |
| ch15 · PGM + 强化学习策略梯度 | ⬜ | ⬜ |
| ch16 · 生成模型评估与采样几何 | ⬜ | ⬜ |
| ch17 · RLHF / 偏好模型概率机制 | ⬜ | ⬜ |

## 附录

| 章节 | 标题 | 状态 |
|---|---|---|
| appendixA · 数值稳定性手册 | ⬜ | ⬜ |
| appendixB · 工程速查表 | ⬜ | ⬜ |

## 资源

- [符号与代码约定](_assets/style-guide.md)
- [依赖与启动](_assets/deps-guide.md)
- [完成进度](SUMMARY.md)

## 参考课程与教材

- Harvard Stat 110 (Blitzstein & Hwang, *Introduction to Probability*)
- MIT 6.041 / 6.265 (Bertsekas, *Probabilistic Systems Analysis*)
- MacKay, *Information Theory, Inference, and Learning Algorithms*
- Murphy, *Probabilistic Machine Learning* Vol. 1
- Kingma & Welling, *Auto-Encoding Variational Bayes* (2014)