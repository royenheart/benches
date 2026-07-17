# 概率论专题 · 完成进度

> 阶段 A (ch00, ch02, ch14) 与阶段 B (其余 17 章 + 2 附录) 均已完成。
> 全部 20 个 notebook 经 `nbconvert --to notebook --execute --inplace` 验证通过 (0 cell errors)。

## 总进度

- 阶段 A：✅ ch00 + ch02 + ch14
- 阶段 B：✅ ch01 + ch03-ch17 (除 ch14 外) + appendixA + appendixB

## 详细进度

| 章节 | 标题 | 状态 | 预估时长 | 推荐学习路径位 |
|---|---|---|---|---|
| ch00 | 概率是什么 + 工作流落地 | ✅ | 90 min | 起点 |
| ch01 | 样本空间、事件、概率公理 + 排列组合 | ✅ | 120 min | Phase 1 第 1 章 |
| ch02 | 条件概率、贝叶斯定理、独立性 | ✅ | 120 min | Phase 1 第 2 章 |
| ch03 | 离散型随机变量 | ✅ | 120 min | Phase 1 第 3 章 |
| ch04 | 连续型随机变量 | ✅ | 120 min | Phase 1 第 4 章 |
| ch05 | 联合分布、协方差、相关 vs 因果 | ✅ | 90 min | Phase 2 第 1 章 |
| ch06 | 矩母函数、大数律、中心极限定理 | ✅ | 150 min | Phase 2 第 2 章 |
| ch07 | 次序统计量、分位数、Bootstrap | ✅ | 90 min | Phase 2 第 3 章 |
| ch08 | 参数估计：矩法、MLE、Fisher 信息 | ✅ | 150 min | Phase 2 第 4 章 |
| ch09 | 马尔可夫链：平稳分布、细致平衡、收敛 | ✅ | 150 min | Phase 3 第 1 章 |
| ch10 | 泊松过程与排队论速写 | ✅ | 90 min | Phase 3 第 2 章 |
| ch11 | 熵、KL 散度、互信息、交叉熵 | ✅ | 120 min | Phase 3 第 3 章 |
| ch12 | 贝叶斯推断基础：共轭先验、后验预测 | ✅ | 150 min | Phase 4 起点 |
| ch13 | 蒙特卡洛族（拒绝/重要性/MH/HMC/NUTS） | ✅ | 150 min | Phase 4 第 2 章 |
| ch14 | 变分推断、重参数化、ELBO 推导 | ✅ | 180 min | Phase 4 第 3 章 |
| ch15 | PGM + 强化学习策略梯度 REINFORCE | ✅ | 150 min | Phase 4 第 4 章 |
| ch16 | 生成模型评估与采样几何 | ✅ | 120 min | Phase 4 第 5 章 |
| ch17 | RLHF / 偏好模型概率机制 | ✅ | 120 min | Phase 4 第 6 章 |
| appendixA | 数值稳定性手册 | ✅ | 90 min | 跨章参考 |
| appendixB | 工程速查表 | ✅ | 60 min | 跨章参考 |

## 完整路径建议

- **快速入门 (2-3 小时)**: ch00 → ch02 → ch08 §1-3
- **基础课程 (约 25 小时)**: Phase 0 → 1 → 2 → 3 + appendixA
- **贝叶斯 + AI 应用 (约 20 小时)**: Phase 4 全部 + appendixB
- **完整路径 (约 50-60 小时)**: ch00 → ch17 + appendixA + appendixB

## 工具链

- Python ≥ 3.10
- numpy / scipy / sympy / matplotlib / networkx (主线)
- PyMC / numpyro / arviz (ch12-13 贝叶斯)
- torch / torchvision (ch14-17 AI 应用)
- 一行启动: `uv run --extra probability jupyter lab`
- 验证单章: `uv run --extra probability jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 mathematics/probability/chXX-.../notebook.ipynb`

## 重生 notebook

每章 notebook 由 `gen.py` 生成（不是手写 ipynb）。重生：

```bash
uv run --extra dev python -m tools.math.nb_build \
    mathematics/probability/chXX-.../gen.py \
    mathematics/probability/chXX-.../notebook.ipynb
```