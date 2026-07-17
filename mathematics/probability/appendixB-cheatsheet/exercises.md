# appendixB · 课后题

## Q1 · 识别场景
每个场景找推荐分布族 + 估计器 + 采样器:
1. 在线广告点击率每周统计
2. 高 SNR Pixel 回归 (输出像素值)
3. 排队 API 的 P95 延迟 vs SLO

## Q2 · KL 选择对应
解释 "VAE / EM / Diffusion 三种生成模型里, 用 forward 或 reverse KL 的差别"。

## Q3 · 通用样板:
报 seed + 训练后 ML 模型时, 推荐一段文档化的"RNG header": 你写在 README 中 5 行。

## Q4 (进阶) · 跨越表的关系
从分类/回归 (ch08) → A/B 测试 (ch12) → LLM 对齐 (ch17): 解释 "likelihood 选择 + 报告"决策相似与不同的地方。

## Q5 (实战) · 一份 modern AI 项目 cheatsheet
给 medium-size ML team 用这份 course 写一份 1 页的 "概率建模 cheat sheet"，涵盖:
- 序贯 SEED header 模板
- 当 N<1000 时如何处理分布假设
- 报 credible interval / 的姿势