# ch15 · 概率图模型 + 强化学习中的策略梯度

> 把章节 11-14 的概率关系浓缩到图模型领域; 并将“重新参数化技巧”与“score function”视为对偶梯度估计器带入强化学习中。

## 学习目标

- 写出贝叶斯网络 (Bayesian Network) 与马尔可夫随机场 (Markov Random Field) 的差异
- 根据图写出联合因子分解 (chain rule + 图条件独立性)
- 推导 REINFORCE 策略梯度 `∇J(θ) = E[∇w log π_θ(a|s) · Q(s,a)]`
- 对比 REINFORCE (score-function) 与 VAE reparam (pathwise) 的方差与适用性
- 使用 PyTorch 在 CartPole 类 toy MDP 上进行 REINFORCE 训练

## 场景
1. **PGM 描述**: 将 POMDP 状态空间 / 隐变量生成模型写成图, 获取推理路线
2. **REINFORCE 离散动作**: LLM 对答复采样 → reward → log p 梯度
3. **Actor-Critic**: score-based + bootstrap value (本章节给基础 REINFORCE)

## 参考
- Koller & Friedman *Probabilistic Graphical Models* Ch.2-4
- Sutton & Barto *RL* 2nd ed. Ch.13 (Policy Gradient)
- Murphy §19.5