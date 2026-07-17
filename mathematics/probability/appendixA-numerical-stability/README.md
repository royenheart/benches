# appendixA · 数值稳定性手册

> 工程中常因 log p / log-sum-exp / 小概率浮点数爆 / KL 累积 NaN 等. 这一附录把这些坑集中起来给一段段"古法算式 → numpy API 等价 → 推荐姿势".

## 学习目标

- 写出 log-sum-exp 用于 mixed Gaussian / 加入 low-prob 防止 NaN overflow
- 写出 categorical log_safe = log(p) - log p_max
- 用 scipy.special.logsumexp 与 logaddexp 替换朴素累加 概率
- 处理 fp16 / bf16 训练中 overflow / underflow
- 写一段 KL 散度稳定估计借助 LOg-space

## 参考
- documentation `scipy.special.logsumexp`
- https://blog.fugue.io/2018-12-15-numerical-stability.html
- Murphy §11.1