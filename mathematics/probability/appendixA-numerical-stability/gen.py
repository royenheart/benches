"""appendixA · 数值稳定性手册. Build via nb_build."""

TITLE = "appendixA · 数值稳定性手册"

PROBES = []


def _md(t):
    PROBES.append({"kind": "markdown", "source": t})


def _code(t):
    PROBES.append({"kind": "code", "source": t})


_md("""# appendixA · 数值稳定性手册

## Why this appendix
工程上每天会遇到的"突然 NaN"、"KL 跑飞"、"softmax 溢出"绝大部分源于数值不稳, 而不是算法理解错. 把这套 cheat-sheet 直接放在仓库最顶层是为了 — 写到 log p / p(θ|y) 的代码时, 你一眼就知道用 scipy.special.logsumexp 而非 np.log(np.sum(np.exp(...))).

## 学完后能解决

- 用 log-sum-exp 替换朴素 log(sum(exp))
- log-domain KL stable 估计
- Bernoulli logp 在 p 接近 0 或 1 时避免 -inf / 不爆
- fp16 / bf16 混合精度训练的overflow 量级与对策
""")

_md("""## 2. 坑 1: log(sum(exp)) 溢出""")
_code(
    """import numpy as np
from scipy.special import logsumexp

x = np.array([1000.0, 1001.0, 1002.0])
# 朴素: e^1000 -> overflow (inf)
try:
    p_naive = np.exp(x) / np.exp(x).sum()
    print("naive:", p_naive)  # 通常 nan
except Exception as exc:
    print("naive raised", exc.__class__.__name__)

# log-sum-exp trick:
lse = logsumexp(x)
p_stable = np.exp(x - lse)
print("stable softmax:", p_stable)
print("sum check:", p_stable.sum())
"""
)

_md("""## 3. 公式

### log-sum-exp
$$\\mathrm{LSE}(x_1, ..., x_n) = \\log\\sum_i e^{x_i} = a + \\log\\sum_i e^{x_i - a}$$
where $a = \\max_i x_i$, 总是 $x_{max} \\le \\mathrm{LSE} \\le x_{max} + \\log n$.

### softmax stable
$$\\sigma_i = \\frac{e^{x_i}}{\\sum_k e^{x_k}} = e^{x_i - \\mathrm{LSE}(x)}$$
""")

_md("""## 4. 坑 2: Bernoulli logp when p 接近 0 / 1""")
_code(
    """import numpy as np
# e.g. binary cross entropy
# naive: log p = np.log(p) → -inf when p=0
p_pred = np.array([0.0, 0.001, 0.999, 1.0])

# 用 clip
log_p_clipped = np.log(np.clip(p_pred, 1e-30, 1 - 1e-30))
print("clipped log p:", log_p_clipped)

# 更优: torch.distributions.Bernoulli 用 logits 上 BCEWithLogitsLoss; 自行展开:
logits = np.log(p_pred / (1 - p_pred) + 1e-30)  # 但 p=1 仍 +inf
print("logits:", logits)

# 解: 训练时让模型 logits, 用 F.binary_cross_entropy_with_logits(logits, target)
# TensorFlow/PyTorch 中 BCE-with-logits 走 (log-sum-exp 形) 稳定计算
"""
)

_md("""## 5. 坑 3: KL 在 log domain""")
_code(
    """import numpy as np
# KL(p||q) = Σ p_i log(p_i / q_i) → 当 q_i = 0 发散; 朴素 NaN

p = np.array([0.5, 0.5])
q = np.array([0.0, 1.0])  # q[0]=0 会在朴素 KL 给 inf

# Stable version via logp:
logp = np.log(p)
logq = np.log(np.clip(q, 1e-30, None))  # log(0) -> -large; clip to prevent
kl_stable = np.sum(p * (logp - logq))
print("KL stable:", kl_stable)  # large finite number
print("If q can be 0 you actually have infinite KL — 这是代号 that模fit not matched!")
"""
)

_md("""## 6. 坑 4: 训练 fp16/bf16 与 overflow""")
_code(
    """import numpy as np
# fp16 maximum ~ 65504, overflow when e^x > 65504 -> x > 11.09
# fp16 minimum sub-normal ~6e-8; underflow for any x < -log(2^16) ≈ -27
# fp32: max ~3.4e38 -> x > ~88 
print("fp16 max value before exp overflow:", 11.09)
print("fp32 max value before exp overflow:", 88.0)

# Loss scaling technique (DeepSpeed, Apex): 复制 loss 上放大因子 S; backward 时再除 S
# 在 quantization 时取 S = max(logits magnitude) — 减少梯度 underflow
S = 1024
loss = np.array([1e-8])
loss_scaled = loss * S
print(f"loss before {loss.item()}, after scaling {loss_scaled.item()}")
# 注意 backward 阶段仍需 /S 以恢复
"""
)

_md("""## 7. 坑 5: log-sum-exp for gradients (softmax backward)""")
_code(
    """import torch
import torch.nn.functional as F

# Stable cross-entropy via logits - PyTorch has the implementation
logits = torch.tensor([1000.0, 1001.0, 1002.0])
target = torch.tensor(1, dtype=torch.long)
# 用 F.cross_entropy - 已经走 stable log category
loss = F.cross_entropy(logits.unsqueeze(0), target.unsqueeze(0))
print(f"stable CE loss = {loss.item():.4f}")

# 不稳定的手写:
try:
    log_p_wrong = torch.log_softmax(logits, dim=-1)[target]
    print(f"manual log_softmax = {log_p_wrong.item():.4f} - 也能稳因 PyTorch 的 log_softmax 已 实现 LSE trick")
except Exception as exc:
    print("err:", exc)
"""
)

_md("""## 8. pitfalls
- Do not compute `p / q` directly; logp - logq 是稳姿态
- p close to 0/1 用 logits 表示
- 用 fp16 训练时必须 loss scaling; 否则 underflow 抹掉小梯度
- KL 在两种支集不一致时是为确无穷 - 在评估中要 clip q ≈ 0
- LSE 不要凑多项; `scipy.special.logsumexp` 接受 axis 与 keepdims
- 当做高维 product 时 (n>1e6), log_sum_exp 累积 也可能丢精度; 用 Kahan 求和

## 9. 课后 → exercises.md

## 10. 参考
- scipy.special.logsumexp 文档
- https://blog.fugue.io/2018-12-15-numerical-stability.html
- Murphy §11.1""")