# ch13 · 蒙特卡洛族: 拒绝采样、重要性采样、MCMC、HMC

> 把 ch12 共轭能力扩展到任意目标分布; 工程实际贝叶斯离不开 MC 采样。

## 学习目标

- 写拒绝采样算法与接收率
- 写重要性采样给期望估计 (含权重自归一)
- 推 MH 接受率表达式 + 仿真 Beta-Binomial 例
- 解释 HMC 的物理直觉与梯度作用
- 用 numpyro 一键采 VAE 后验 — 与 ch12 PyMC 对比

## 场景
1. **任意分布后验采样**: PyMC / numpyro 的费用工程: 模型 logp 可算但归一化常数不可算
2. **离线置信估计**: importance sampling 重加权历史数据
3. **变分推断之外的备选方案**: 与 ch14 的 VI 不同, MCMC 在极限是 exact

## 参考
- MacKay Ch.29-30
- Murphy §19.2-19.4
- Hoffman & Gelman 2014 *NUTS*