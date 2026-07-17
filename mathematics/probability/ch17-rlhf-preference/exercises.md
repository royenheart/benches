# ch17 · 课后题

## Q1 · Bradley-Terry MLE
给定 5 个 pairwise preferences over 4 candidates: write BT negative log likelihood 用 PyTorch 求出 MLE reward vector. 验证排序.

## Q2 · Plackett-Luce for top-3
3 个 list-level ordering y1 > y2 > y3 over 4 candidates, 给 PL 的 log-likelihood; 用 numpy 或 PyTorch 抽样验证.

## Q3 · PPO clip ratio visualization
用 ε=0.1, 0.3, 0.5 算 PPO objective curve (与 ch17 §6 一致). 在 ε 越大时 — ratio 上限做多远? * 比照 ε 用途.

## Q4 · DPO closed form derivation
按 ch17 §3 推导 DPO 完整路径 (BT + KL-正则推导 + reward-π* 逆推式); 写一段文本答案.

## Q5 · Mini-PPO on GridWorld-1D
仿真 1-D simple MDP: state s∈{0..10}, action {-1, 0, +1}; reward=s 时间步后值. 实现 mini-PPO (clip+advantage) 在 1000 episodes 上跑, 观察 π 收敛到最优策略 (全部向 +1).