# ch15 · 课后题

## Q1 · D-separation
给定 BN: A→B, A→C, B→D, C→D。问 B 与 C 给定 A 时是否独立? 给定 D 时是否独立? (即 v-structure collider)

## Q2 · REINFORCE 在 2-arm bandit
两臂 μ=[0.3, 0.7], noise=0.1。用 REINFORCE 学习 1000 步; 报 softmax 收敛轨迹与 arm-2 P(选) → 1 的速度。

## Q3 · REINFORCE vs random
计算 ch15 第 5 段的 sample mean 在第 100/500/2000 步; 换用纯随机抓取 baseline; 看提升多少。

## Q4 (进阶) · baseline 加速
重新训 REINFORCE 无 baseline vs EMA baseline; 给两条 reward 曲线叠加, 看哪个更快收敛到 0.8。

## Q5 (实战) · 用 multinomial 模拟 LLM REINFORCE
模拟 situation: 4 个 candidate response, logit feasible 来 reward 函数 [0.3, 0.5, 0.7, 0.9]。用 REINFORCE 训练 logits; 看哪个 candidate 概率被推得最高。给步骤 + 代码 + final probs。