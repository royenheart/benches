# ParallelTests

## 解决问题

矩阵乘法问题：

设矩阵 A：

$$
A = \left(
    \begin{array}{ccc}
        a_{11} & a_{12} & ... & a_{1n} \\
        a_{21} & a_{22} & ... & a_{2n} \\
        ... & ... & ... & ... \\
        a_{m1} & a_{m2} & ... & a_{mn} \\
    \end{array}
\right)
$$

设矩阵 B：

$$
B = \left(
    \begin{array}{ccc}
        b_{11} & b_{12} & ... & b_{1p} \\
        b_{21} & b_{22} & ... & b_{2p} \\
        ... & ... & ... & ... \\
        b_{n1} & b_{n2} & ... & b_{np} \\
    \end{array}
\right)
$$

A 矩阵是 $m * n$ 大小的矩阵，B 矩阵是 $n * p$ 大小的矩阵，两矩阵乘法结果是一个新矩阵 C，维度是 $m * p$，即 $m$ 行和 $p$ 列。

矩阵乘法数学公式表示为：

$$
C_{mp} = \sum_{n=1}^n A_{mn} \cdot B_{np} 
$$

## 使用方法

* 所有源代码均使用 `C++17` 标准编写，编译时请注意。 

> 提示：使用 `-std` 编译参数指定使用的 C/C++ 标准版本。

所有矩阵存放方式均为行优先，内部元素类型为 `double`，生成的数据集文件 `matrix-m-n-p.x.bin` 为二进制文件，包含：

1. 指定内部矩阵大小的 m, n, p 三个元素（`size_t` 类型）。
2. A 矩阵元素（`double` 类型）。
3. B 矩阵元素（`double` 类型）。
4. 串行算法计算得来的 A B 矩阵乘法的结果，用作正确答案便于后续进行验证，其元素个数为 $m * p$，类型为 `double`。

`inc` 目录存放了头文件，`src` 目录存放了源代码文件。进入 `src` 目录，首先编译 `datagen.cpp` 文件用于生成数据集，`datagen.cpp` 编译后使用方法为：

> ./datagen \<m\> \<n\> \<p\> [folder]

> m : A 矩阵行数。

> n : A 矩阵列数，B 矩阵行数。

> p : B 矩阵列数。

> folder: 可选，指定数据集生成的目录。未指定时默认生成至当前目录。默认生成一个数据集，包含 10 个指定矩阵规模的随机数据（即总共 10 组 A、B 矩阵），按照生成顺序反映在文件 `matrix-m-n-p.x.bin` 的 `x` 编号上。

计算程序使用方法：

> ./matrix_cal_xxx [folder]

> folder: 可选，指定使用数据集存放的目录。未指定时默认遍历当前目录下名称为 `matrix-m-n-p.x.bin` 的数据集。默认会将同一类（即判断 m，n，p 是否相同）的数据作为一个数据集集中测试，每次测试一个数据集后接到下一个。

## Test ENV

### Intel (Black Server)

| Software          | Version  |
| ----------------- | -------- |
| Intel oneAPI Base | 2025.1.0 |
| Intel oneAPI HPC  | 2025.1.0 |

## Exp1

调整 Spinlock time（block time）。以下设置在 Intel 编译器中应当生效，使用 Intel 编译器时，启用 MKL 库优化（一些特殊线程设置参数在 MKL 中）。

参考网址：

1. [Intel DPC/C++ Compiler OpenMP Env](https://www.intel.com/content/www/us/en/docs/dpcpp-cpp-compiler/developer-guide-reference/2023-2/supported-environment-variables.html)
2. [Intel MKL Threading Performance Suggestion](https://www.intel.com/content/www/us/en/docs/onemkl/developer-guide-linux/2024-0/improving-performance-with-threading.html)
3. [LLVM Compiler OpenMP Env](https://openmp.llvm.org/design/Runtimes.html)
4. [OpenMP 6.0 Standard](https://www.openmp.org/wp-content/uploads/OpenMP-API-Specification-6-0.pdf)

### OMP_WAIT_POLICY (Intel Compiler(libiomp), LLVM (libomp))

The OMP_WAIT_POLICY environment variable provides a hint to an OpenMP implementation about the desired behavior of waiting native threads by setting the wait-policy-var ICV. A compliant implementation may or may not abide by the setting of the environment variable. The value of this environment variable must be one of the following:

> active | passive

The active value specifies that waiting native threads should mostly be active, consuming processor cycles, while waiting. A compliant implementation may, for example, make waiting native threads spin. The passive value specifies that waiting native threads should mostly be passive, not consuming processor cycles, while waiting. For example, a compliant implementation may make waiting native threads yield the processor to other native threads or go to sleep. The details of the active and passive behaviors are implementation defined. The behavior of the program is implementation defined if the value of OMP_WAIT_POLICY is neither active nor passive.

当设置为 passive 时，修改 OpenMP kmp blocktime 为0，即禁用自旋等待时间。

### KMP_BLOCKTIME (Intel Compiler(libiomp), LLVM(libomp))

设置线程在执行完一个并行计算区域之后进入睡眠之前的等待时间，单位是毫秒，默认 200ms。

LLVM 21 目前支持设置到 us 微秒级别，比如：

1. export KML_BLOCKTIME=200ms
2. export KML_BLOCKTIME=20us

### KMP_AFFINITY (Intel Compiler(libiomp), LLVM(libomp))

启用运行时库来将线程绑定到物理处理单元上，优先级在 OMP_PROC_BIND 之上，有更细粒度的调整，Intel 对于开启了 Hyper Threading 的系统推荐为：

> KMP_AFFINITY=granularity=fine,compact,1,0

### KMP_SETTINGS (Intel Compiler(libiomp), LLVM(libomp))

启用（true）或禁用（false）程序执行过程中 OpenMP 运行时库环境变量的打印

### OMP_DISPLAY_ENV (LLVM(libomp))

启用（true）或禁用（false）程序执行过程中 OpenMP 运行时库环境变量的打印，也可以使用 verbose。

### MKL_DYNAMIC (Intel Compiler with MKL)

在没有使用 MKL 的加速时（矩阵计算 API），不需要设置

The MKL_DYNAMIC environment variable enables Intel® oneAPI Math Kernel Library (oneMKL) to dynamically change the number of threads. 允许 Intel MKL 动态调整线程数（不是 Intel tbb 线程库）。

### OMP_DYNAMIC (LLVM(libomp))

和 MKL_DYNAMIC 同理。

### GOMP_SPINCOUNT (GCC(libgomp))

GCC 中没有类似 KMP_BLOCKTIME 直接控制自旋锁等待时间的参数，此参数是类似的，但是控制自旋锁最大等待次数：

> Determines how long a threads waits actively with consuming CPU power before waiting passively without consuming CPU power. The value may be either INFINITE, INFINITY to always wait actively or an integer which gives the number of spins of the busy-wait loop. The integer may optionally be followed by the following suffixes acting as multiplication factors: k (kilo, thousand), M (mega, million), G (giga, billion), or T (tera, trillion). If undefined, 0 is used when OMP_WAIT_POLICY is PASSIVE, 300,000 is used when OMP_WAIT_POLICY is undefined and 30 billion is used when OMP_WAIT_POLICY is ACTIVE. If there are more OpenMP threads than available CPUs, 1000 and 100 spins are used for OMP_WAIT_POLICY being ACTIVE or undefined, respectively; unless the GOMP_SPINCOUNT is lower or OMP_WAIT_POLICY is PASSIVE.