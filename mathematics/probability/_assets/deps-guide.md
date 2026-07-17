# 依赖与启动

## 一行启动交互环境

```bash
uv run --extra probability jupyter lab
```

`uv` 会按需自动 sync probability extra（首次可能耗时数分钟；离线时设 `BENCHES_PROXY`）。

## 验证单章 notebook 一键跑通

```bash
uv run --extra probability jupyter nbconvert \
    --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=600 \
    mathematics/probability/chXX-.../notebook.ipynb
```

期望退出码 0；如有 cell 报错，修该章 `gen.py` 后重生：

```bash
uv run --extra dev python -m tools.math.nb_build \
    mathematics/probability/chXX-.../gen.py \
    mathematics/probability/chXX-.../notebook.ipynb
```

## 常见问题

### PyMC / numpyro 安装缓慢

首次 `uv sync --extra probability` 会把 PyMC / numpyro / jax 一套依赖装入。如果只跑 ch00-ch11 + appendixA，不需要这些；改用 `uv run --extra dev --with numpy --with scipy --with sympy --with matplotlib --with networkx jupyter lab` 即可。

### torchvision 不可用

ch14 的 VAE demo 用 torchvision.datasets.MNIST。若安装或下载失败，gen.py 会自动 fallback 到 numpy 合成数据（28×28 灰度，"7 vs 非 7"二分类）。看 notebook 第 7 段的 `try/except ImportError` 分支。

### torch 只能用 CPU

仓库默认无 CUDA；本课程所有 cell 在 `torch.device("cpu")` 下能在 600s 内跑完。若你有 CUDA 想加速，把 `device = "cpu"` 改为 `device = "cuda" if torch.cuda.is_available() else "cpu"`，注意重训结果在 CPU 重现时 seed 行为可能不同。

### memory 引用跨章节

ch14 之后会引用 ch12 的 PyMC 实体；目前没走出阶段 A，所以暂未发生。后续章节建议在 `gen.py` 中显式 import，不在 notebook 内部跨章引用。

### nbconvert 报 NotebookValidationError：'name' 是 required property

这是 kernelspec 缺 `name` 字段。`tools/math/nb_build.py` 已经设 `name: "python3"`；如果你手动改 notebook，记得该字段不能删。

### `restart & run all` 卡在某个 cell

把该章 top cell 的 `tmout = 600` 改大；或把 PyTorch 训练 epoch 数减半。`gen.py` 中 epoch 数已经选到能在 CPU 5分钟内完成的水平。