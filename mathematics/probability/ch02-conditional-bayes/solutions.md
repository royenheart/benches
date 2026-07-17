# ch02 · 课后题答案

## Q1 · Monty Hall n 扇门

把 3 扇推广：你初初始选中概率为 $1/n$。主持人被迫剩下 $n-2$ 扇上所有的 Goat 都打开 → 把"非玩家初始选到车的概率" $\\frac{n-1}{n}$ 全部集中到剩下那 1 扇门。

**换门胜率** $= \\frac{n-1}{n}$；$n=3$ 即得 $2/3$；$n=100$ 即得 $99/100$。

代码骨架：
```python
import numpy as np

def monty_hall_n(n, N=200_000):
    rng = np.random.default_rng(seed=20240717)
    cars = rng.integers(0, n, size=N)
    initial = rng.integers(0, n, size=N)
    switch_wins = (cars != initial).mean()  # 主持人严格只开羊门，剩下一扇必是"非初始 == 车"的承载
    return switch_wins

for n in [3, 4, 10, 100]:
    print(f"n={n}  switch_wins={monty_hall_n(n):.4f}  theory={(n-1)/n:.4f}")
```

## Q2 · 顺序无关

代码骨架：
```python
import numpy as np
from scipy.stats import beta

alpha_prior, beta_prior = 2.0, 5.0

# 方式 A：一次性
alpha_A = alpha_prior + 7
beta_A = beta_prior + 13  # n = 20, k = 7

# 方式 B：分两批
alpha_mid = alpha_prior + 2
beta_mid = beta_prior + 6
alpha_B = alpha_mid + 5
beta_B = beta_mid + 7

print(f"A: Beta({alpha_A}, {beta_A})  B: Beta({alpha_B}, {beta_B})")
print("两参数相等:", alpha_A == alpha_B and beta_A == beta_B)  # 应 True
```

够矣。

## Q3 · 二次检查后 PPV

设第一次 positive 后，$P(D|+_1) = p_1$。第二次检查独立 conditional on D：
$$P(+_2|+_1, D) = 0.99,\\quad P(+_2|+_1, \\bar D) = 0.05$$

然而**第一次后 $P(D|+_1)$** 已经从 1/1000 增长了一阶。代公式即可：
```python
p_D_prior = 0.001
sens, fpr = 0.99, 0.05
# 第一次
p_pos1_given_D = sens * p_D_prior + fpr * (1 - p_D_prior)
p_D_after_1 = sens * p_D_prior / p_pos1_given_D
# 第二次（用 p_D_after_1 作先验）
p_pos2_given_old_prior = sens * p_D_after_1 + fpr * (1 - p_D_after_1)
p_D_after_2 = sens * p_D_after_1 / p_pos2_given_old_prior
print(f"P(D|+_1)    = {p_D_after_1:.4f}")
print(f"P(D|+_1,+_2)= {p_D_after_2:.4f}")
```

期望输出：$P(D|+_1) \\approx 1.94\\%$，$P(D|+_1,+_2) \\approx 27.97\\%$ —— 跳着一个加量是来自基础率被 duplicate-data 强行向上推。

## Q4 hint

经典反例之一：丢两次"不知是否均匀"的硬币。A、B 是两次投掊结果，C = "硬币本身"。条件 C 已知是公平硬币 → A、B 独立；但 C 未知时 A、B 不独立（A 出职示争到硬币本身类型）。代码不要求；写一段文字+一句 sympy probability expression 即可。

## Q5 hint

引擎骨架：
```python
from dataclasses import dataclass
import numpy as np
from scipy.stats import beta as beta_dist

@dataclass
class ABEngine:
    alpha_a: float = 1.0
    beta_a: float = 1.0
    alpha_b: float = 1.0
    beta_b: float = 1.0

    def update(self, is_b: bool, n_obs: int, k_obs: int):
        if is_b:
            self.alpha_b += k_obs
            self.beta_b += (n_obs - k_obs)
        else:
            self.alpha_a += k_obs
            self.beta_a += (n_obs - k_obs)

    def expected_ctr_a(self): return self.alpha_a / (self.alpha_a + self.beta_a)
    def expected_ctr_b(self): return self.alpha_b / (self.alpha_b + self.beta_b)

    def should_stop(self, N_samples=100000):
        rng = np.random.default_rng(seed=0)  # 测试中可参数化
        pa = rng.beta(self.alpha_a, self.beta_a, size=N_samples)
        pb = rng.beta(self.alpha_b, self.beta_b, size=N_samples)
        p_b_worse = (pb < pa).mean()
        return p_b_worse < 0.05, p_b_worse

    def credible_interval_a_95(self):
        return beta_dist.ppf([0.025, 0.975], self.alpha_a, self.beta_a)

    def credible_interval_b_95(self):
        return beta_dist.ppf([0.025, 0.975], self.alpha_b, self.beta_b)
```

仿真用：仿真 truth CTR_a=0.4, CTR_b=0.45，按时间序列 feed 直到 should_stop 为 True；记录迭代数与时刻的 CIs。