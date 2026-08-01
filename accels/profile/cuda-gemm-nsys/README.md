# cuda-gemm-nsys

朴素 CUDA GEMM（`C = A * B`）+ NVTX，用于练习 / 验证 Nsight Systems（`nsys`）。

## 依赖

- CUDA Toolkit（`nvcc`）
- Nsight Systems（`nsys` / `nsys-ui`）

确保二者都在 PATH 中。

## 编译

### Linux（Makefile）

```bash
chmod +x build.sh profile.sh   # 首次
make                           # 或 ./build.sh
ARCH=sm_89 make                # 指定 GPU arch
```

### Windows

```bat
build.bat
build.bat sm_89
```

也可用 CMake：

```bash
cmake -B build -DCMAKE_CUDA_ARCHITECTURES=native
cmake --build build --config Release
```

## 运行

```bash
./gemm 1024 10          # Linux
gemm.exe 1024 10        # Windows
# 或
make run N=1024 ITERS=10
```

参数：`N`（方阵边长）、`iters`（计时迭代次数）。

## 用 nsys 采集

### Linux

```bash
./profile.sh 1024 10
# 或
make profile N=1024 ITERS=10
```

### Windows

```bat
profile.bat 1024 10
```

等价命令：

```bash
nsys profile -o gemm_report -f true --stats=true --trace=cuda,nvtx,osrt ./gemm 1024 10
```

用 UI 打开：

```bash
nsys-ui gemm_report.nsys-rep
```

时间线上应能看到 NVTX ranges：`H2D`、`warmup`、`gemm_iters` / `gemm_naive#*`、`D2H`。
