# ch15 · 答案骨架

## Q1 hint
A→B, A→C, B→D, C→D 即 "diamond". B⊥C | A (A 是 root, 去掉 A 后 B, C 仍独立); B 不⊥C | D (D 是 collider on path B-D-C).

## Q2 hint
```python
import numpy as np
import torch
import torch.nn.functional as F
torch.manual_seed(0)
K = 2; true_mu = torch.tensor([0.3, 0.7])
logits = torch.zeros(K, requires_grad=True)
opt = torch.optim.Adam([logits], lr=0.05)
rng = np.random.default_rng(seed=0)
probs_record = []
for step in range(1000):
    probs = F.softmax(logits, 0)
    a = torch.multinomial(probs, 1)
    r = float(true_mu[a]) + rng.normal(0, 0.1)
    log_prob = F.log_softmax(logits, 0)[a]
    loss = -(r * log_prob)
    opt.zero_grad(); loss.backward(); opt.step()
    probs_record.append(F.softmax(logits, 0).detach().numpy())
import numpy as np
probs_record = np.array(probs_record)
print(f"step 100 arm-2 prob = {probs_record[100, 1]:.3f}")
print(f"step 1000 arm-2 prob = {probs_record[-1, 1]:.3f}")
```

## Q3 hint 略 (与 ch15 第 5 段类似).

## Q5 hint
```python
import torch
import torch.nn.functional as F
logits = torch.zeros(4, requires_grad=True)
opt = torch.optim.Adam([logits], lr=0.1)
true_rewards = torch.tensor([0.3, 0.5, 0.7, 0.9])
for _ in range(1000):
    probs = F.softmax(logits, 0)
    a = torch.multinomial(probs, 1)
    r = true_rewards[a]
    loss = -(r * F.log_softmax(logits, 0)[a])
    opt.zero_grad(); loss.backward(); opt.step()
print("final probs:", F.softmax(logits, 0))
```