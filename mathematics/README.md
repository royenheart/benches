# Mathematics 专题

`mathematics/` 收录与数学主题相关的循序渐进的可执行学习材料，把"看到任务想到建模"作为目标。

## 已有专题

| 专题 | 入口 | 状态 |
|---|---|---|
| 概率论 | [`probability/README.md`](probability/README.md) | 阶段 A：ch00、ch02、ch14 已交付；其余 16 章分阶段产出 |

## 约定

- 每章独立可读、可跑：`uv run --extra probability jupyter lab` 进入交互；`uv run --extra probability jupyter nbconvert --to notebook --execute mathematics/probability/chXX-.../notebook.ipynb` 验证。
- 每章统一 4 文件：`README.md` 速读、`notebook.ipynb` 主授课、`exercises.md` 三级题、`solutions.md` 关键题提示。
- 章节内容经辅助脚本 `tools/math/nb_build.py` 生成，源在每章 `gen.py`；写 `python -m tools.math.nb_build <gen.py> <notebook.ipynb>` 一键重生。
- 符号与代码约定见 [`probability/_assets/style-guide.md`](probability/_assets/style-guide.md)。