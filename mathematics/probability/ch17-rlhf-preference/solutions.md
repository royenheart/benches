# ch17 · 答案骨架

## Q1 hint
```python
import torch
import torch.nn.functional as F
torch.manual_seed(0)
rewards = torch.zeros(4, requires_grad=True)
prefs = [(1, 2), (0, 3), (1, 3), (2, 0), (3, 1)]
opt = torch.optim.Adam([rewards], lr=0.1)
for _ in range(500):
    loss = 0.0
    for w, l in prefs:
        loss = loss - F.logsigmoid(rewards[w] - rewards[l])
    loss = loss / len(prefs)
    opt.zero_grad(); loss.backward(); opt.step()
print("MLE rewards:", rewards.detach().numpy())
print("Order:", rewards.detach().argsort(descending=True).numpy() if hasattr(rewards.detach(), 'argsort') else sorted(range(4), key=lambda i: -rewards.detach().numpy()[i]))
```

## Q2 hint
```python
import numpy as np
from math import log, exp
candidates = ['a', 'b', 'c', 'd']
rewards = {'a':1.0, 'b':0.5, 'c':0.2, 'd':0.1}
sortings = [('a', 'b', 'c'), ('b', 'c', 'd'), ('a', 'd', 'c')]
for s in sortings:
    log_lik = 0
    avail = list(s) + ['d'] if 'd' not in s else list(s) + ['a']
    for i, y in enumerate(s):
        denom = sum(exp(rewards[k]) for k in s[i:])
        log_lik += rewards[y] - np.log(denom)
    print(f"{s}: log-lik = {log_lik:.4f}")
```

## Q3 hint
修改 ch17 §6 gen.py 的 eps_clip 为 [0.1, 0.3, 0.5]; 看每条带状 colors 看曲线平坦度。

## Q4 hint (见 ch17 §3 的 latex 推导链)
完整推导文字骨架:
1. BT: $P(y_w > y_l) = σ(r_w - r_l)$
2. KL-正则 RL: $\max_π E_{y~π}[r(x,y)] - β D_{KL}(π(·|x) || π_ref(·|x))$
3. 拉格朗日得到 $π^*(y|x) = π_ref(y|x) exp(r/β) / Z(x)$
4. 反推: $r(x,y) = β log \frac{π^*(y|x)}{π_ref(y|x)} + β log Z(x)$
5. 代入 BT: $r_w - r_l = β (log\frac{π^*(y_w|x)}{π_ref(y_w|x)} - log\frac{π^*(y_l|x)}{π_ref(y_l|x)})$ (Z 抵消)
6. 得 $L^{DPO} = -logσ(r_w - r_l) = -log σ(β log_w/pref_w - β log_l/pref_l)$

## Q5 hint (代码骨架)
```python
import numpy as np
import torch
import torch.nn.functional as F
torch.manual_seed(0)
S = 10
policy = torch.zeros(S, 3, requires_grad=True)  # right, stay, left (o-hot)
opt = torch.optim.Adam([policy], lr=0.01)
eps = 0.2
for ep in range(500):
    s = 0; advs = []
    old_logits = policy.detach()
    for t in range(20):
        logits = F.softmax(policy[s], 0)
        a = torch.multinomial(logits, 1)
        adv = s - 5  # advantage = state minus mean
        new_prob = F.softmax(policy[s], 0)[a]
        old_prob = F.softmax(old_logits[s], 0)[a]
        r_t = (new_prob / old_prob).item()
        r_clipped = max(min(r_t, 1+eps), 1-eps)
        loss = -torch.log(new_prob) * adv * r_clipped
        opt.zero_grad(); loss.backward(); opt.step()
        s = max(0, min(S-1, s + (int(a) - 1)))
```