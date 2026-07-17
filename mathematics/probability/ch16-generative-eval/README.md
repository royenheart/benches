# ch16 · 生成模型评估与采样几何

> 似然、FID/IS、流形假设、Mode collapse; 把 ch14 ELBO 接到扩散模型评估的工程坑。

## 学习目标

- 区分 likelihood、IS、FID 三套生成模型评估指标
- 给"扩散模型评估的'易作弊'原因"
- 写一段 numpy 实现简易 FID 估计
- 解释流形假设与 mode collapse 的几何关系
- 给 IS 容易被 mode collapse 误喝的论证

## 场景
1. **VAE vs Diffusion vs GAN**: 三套生成模型的评估风格天然不同
2. **FID 计算**: latent feature 在 Inception-v3 上 (简化用 PCA 替代)
3. **采样几何**: 谈 mode collapse = "高质量 sample 但 cover 错了占总体分布"

## 参考
- Heusel et al. 2017 *GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash Equilibrium* (FID 起点)
- Salimans et al. 2016 *Improved Techniques for Training GANs* (IS)
- Murphy §20.6