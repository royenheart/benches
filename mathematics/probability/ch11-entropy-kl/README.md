# ch11 · 熵、KL 散度、互信息、交叉熵

> 把"信息量"放进概率论; 给出 ML 中 cross-entropy、KL、ELBO 等损失的信息论合理解释。

## 学习目标

- 计算 Shannon 熵 H[X] 与互信息 I[X;Y]
- 推 KL 不对称 / 非负 / 链式法则
- 解释为什么分类用 cross-entropy (= H(p) + KL(p||q))
- 用 numpy 实现离散 KL 与 MI 估计
- 把信息论核心训练 loss 与 ML 实战关联 (CE, ELBO)

## 场景
1. **分类损失**: cross-entropy 出自 KL(p_data||q_model)
2. **特征选择**: 互信息筛选与目标函数相关的 feature
3. **变分推断**: ELBO = -KL - NLL, 这是 ch14 VAE 的"信息论解读"
4. **机密共享 / 编码理论**: rate-distortion 的核心

## 参考
- MacKay *Information Theory, Inference, and Learning Algorithms* Ch.2-4
- Cover & Thomas *Elements of Information Theory* Ch.2-7
- Murphy §2.3 信息部分