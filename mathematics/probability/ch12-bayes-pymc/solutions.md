# ch12 · 答案骨架

## Q1 hint
```python
from scipy.stats import beta
import numpy as np
a, b = 2, 5
# 顺序 1: (10, 3) then (5, 2)
a1, b1 = a + 3, b + 7
a2, b2 = a1 + 2, b1 + 3
# 顺序 2: (5, 2) then (10, 3)
a1r, b1r = a + 2, b + 3
a2r, b2r = a1r + 3, b1r + 7
# 一次 batch
a_o, b_o = a + 5, b + 10
print(a2, b2, a2r, b2r, a_o, b_o)
# 应全为 (7, 15)
```

## Q2 hint
```python
import numpy as np
sigma2, mu0, tau02 = 4, 0, 9
n, x_bar = 20, 1.5
# Posterior: N((tau02^-1 * mu0 + n/sigma2 * x_bar) / (tau02^-1 + n/sigma2), 1/(tau02^-1 + n/sigma2))
precision_post = 1/tau02 + n/sigma2
mean_post = (mu0/tau02 + n*x_bar/sigma2) / precision_post
var_post = 1 / precision_post
print(mean_post, var_post)  # 接近 1.32, 0.18
```

## Q4 hint
```python
import pymc as pm
import numpy as np
rng = np.random.default_rng(seed=0)
n_ads = 10
impressions = rng.integers(500, 5000, size=n_ads)
true_p = rng.beta(2, 50, size=n_ads)
clicks = rng.binomial(impressions, true_p)

with pm.Model() as m:
    alpha = pm.HalfNormal("alpha", 10)
    beta_p = pm.HalfNormal("beta_p", 10)
    p = pm.Beta("p", alpha=alpha, beta=beta_p, shape=n_ads)
    k = pm.Binomial("k", n=impressions, p=p, observed=clicks)
    trace = pm.sample(1000, tune=1000, chains=2, random_seed=0, progressbar=False)
import arviz as az
print(az.summary(trace, var_names=["alpha", "beta_p"]))
```

## Q5 hint
```python
from dataclasses import dataclass
import numpy as np
from scipy.stats import beta as beta_dist

@dataclass
class BayesianClickEngine:
    alpha: float = 1.0
    beta: float = 1.0

    def update(self, k, n):
        self.alpha += k
        self.beta += (n - k)

    def expected_p(self):
        return self.alpha / (self.alpha + self.beta)

    def credible_interval(self, level=0.95):
        lo = (1-level)/2; hi = 1-lo
        return beta_dist.ppf([lo, hi], self.alpha, self.beta)

    def prob_better_than(self, other, samples=20000, rng=None):
        rng = np.random.default_rng() if rng is None else rng
        a = rng.beta(self.alpha, self.beta, size=samples)
        b = rng.beta(other.alpha, other.beta, size=samples)
        return (a > b).mean()

e1 = BayesianClickEngine(); e1.update(50, 1000)
e2 = BayesianClickEngine(); e2.update(70, 1000)
print("CIs:", e1.credible_interval(), e2.credible_interval())
print("P(e2 > e1):", e2.prob_better_than(e1))
```