# ch17 · RLHF / 偏好模型的概率机制

> Bradley-Terry、Plackett-Luce、PPO 中的概率比与 clip; DPO 的 `log p(y_w) − log p(y_l)` 推导。

## 学习目标

- 写 Bradley-Terry 与 Plackett-Luce 偏好模型
- 推 PPO 目标 `clip(r_t, 1-ε, 1+ε)·A_t` 与原 policy 梯度升降关系
- 推 DPO 的 closed-form 优化目标与隐含 reward
- 在 toy 数据上跑 REINFORCE-with-clip (mini PPO)
- 解释 reference model 的作用与 KL 罚项的工程含义

## 场景
1. **RLHF on LLM**: pairwise preference 训 reward model, 再用 PPO 微调
2. **DPO**: 直接最大 preference probability, 跳过 RL 步骤
3. **KL regularization**: 避免 policy 跑离 reference model

## 参考
- Christiano et al. 2017 *Deep RL from Human Preferences*
- Schulman et al. 2017 *Proximal Policy Optimization*
- Rafailov et al. 2023 *Direct Preference Optimization*