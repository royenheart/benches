# ch01 · 课后题答案

## Q1 hint

```python
import numpy as np
def birthday_p(n, days=365):
    nn = np.array([days - k for k in range(n)])
    dd = np.full(n, days)
    return 1 - np.prod(nn / dd)

rng = np.random.default_rng(seed=20240717)
def simulate(n, N=100000, rng_=None):
    if rng_ is None: rng_ = np.random.default_rng(seed=20240717)
    b = rng_.integers(0, 365, size=(N, n))
    s = np.sort(b, axis=1)
    return (s[:, 1:] == s[:, :-1]).any(axis=1).mean()

print(birthday_p(50), simulate(50))
# 期望 ≈ 0.97  /  0.97x
```

## Q2 hint

不同号码：$q = 1 - (1-p)^{1000}$；重复号码：$q' = 1 - (1-p)^{1000} \\cdot \\ldots$ 不对，重复意味着每次独立 → $q' = 1 - (1-p)^{1000}$ 等同（但若重复则候选个数 ≤ 1000 不同，q' 必然低于 q）。

更准确：$q' = 1 - (1-p)^{1000}$ (本应每次"独立"但同一票购多次实际中只算一张→ 见内隐 $q'$ 必有重复⇒：$q' \\le q$。可归纳当 =>
```
p = 1 / 13983816
print("独立1000种：" 1 - (1-p)**1000)
```

## Q3 hint

5 学生围坐无环：$5! = 120$；同性别女5 取 2 组：$\\binom{5}{2} = 10$；3 学生从 5 取 (顺序)：$A_5^3 = 60$。

## Q5 hint (代码骨架)

```python
import numpy as np
def predict_bits(b, p=0.5):
    return int(np.sqrt(2 * 2**b * np.log(1/(1-p))))

for b in [8, 16, 24]:
    print(b, "predict:", predict_bits(b))
    # MC:
    rng = np.random.default_rng(seed=20240717)
    N_trial = 50_000; T = 2**b
    seen_first = []
    for _ in range(200):
        seen = set(); cnt = 0
        while True:
            h = rng.integers(0, T); cnt += 1
            if h in seen: break
            seen.add(h)
        seen_first.append(cnt)
    print("  MC median:", int(np.median(seen_first)))
```