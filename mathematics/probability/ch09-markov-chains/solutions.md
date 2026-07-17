# ch09 · 答案骨架

## Q1 hint
```python
import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(seed=0)
P = np.array([[0.9, 0.1], [0.1, 0.9]])
N_sim = 5000; N_steps = 200
states = np.zeros(N_sim, dtype=int)
rec = np.zeros(N_steps)
for t in range(N_steps):
    states = np.array([rng.choice(2, p=P[s]) for s in states])
    rec[t] = (states == 0).mean()
xs = np.arange(N_steps)
analytic = 0.5 * (1 + 0.8 ** xs)
plt.plot(xs, rec, label="MC")
plt.plot(xs, analytic, "--", label="analytic")
plt.legend(); plt.show()
# mix time |0.8^t| < 0.01 → t > log(0.01)/log(0.8) ≈ 44
```

## Q3 hint
```python
import numpy as np
pi = np.array([0.2, 0.5, 0.3])
P = np.zeros((3,3))
P[0,1] = 0.4; P[1,0] = pi[0]*P[0,1]/pi[1]
P[0,2] = 0.1; P[2,0] = pi[0]*P[0,2]/pi[2]
# row sums normalize:
for i in range(3):
    P[i,i] = 1 - P[i].sum()
# 保证 P[1,2], P[2,1] 满足 detailed balance
P[1,2] = 1 - P[1,0] - P[1,1]
P[2,1] = pi[1]*P[1,2]/pi[2]
# 重新均衡
print(P); print(P @ pi - pi)
```

## Q5 hint (Metropolis)
```python
import numpy as np
p = np.array([0.1, 0.2, 0.4, 0.3])
rng = np.random.default_rng(seed=0)
x = 0; samples = []
for _ in range(100_000):
    y = rng.integers(0, 4)
    if rng.uniform() < min(1, p[y]/p[x]):
        x = y
    samples.append(x)
hist = np.bincount(samples, minlength=4) / len(samples)
print(hist, p)
```