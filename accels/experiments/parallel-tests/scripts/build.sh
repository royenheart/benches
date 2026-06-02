#!/bin/bash

intel() {
	mkdir -p tests/bin/intel
	module purge
	module load compiler/2025.1.0 mpi/2021.15 mkl/2025.1
	# use Intel DPC/C++ Compiler, use Intel OpenMP lib
	icpx src/matrix_cal_openmp.cpp -g3 -O2 -qopenmp -I./inc -o tests/bin/intel/matrix_cal_openmp
	icpx src/load_imbalance_test.cpp -g3 -O2 -qopenmp -DINTEL -qmkl -o tests/bin/intel/load_imbalance_test
	mpiicpx src/matrix_cal_mpi_openmp.cpp -g3 -O2 -qopenmp -I./inc -o tests/bin/intel/matrix_cal_mpi_openmp
	icpx src/datagen.cpp -g3 -O2 -I./inc -o tests/bin/intel/datagen
}

arm() {
	mkdir -p tests/bin/arm
    module purge
    module load bisheng/4.2.0.1 kml/2.5.0 openmpi/3.1.6-default
    export OMPI_CC=clang
    export OMPI_CXX=clang++
    export OMPI_FC=flang
    # use Arm 
    clang++ src/matrix_cal_openmp.cpp -g3 -O2 -fopenmp -I./inc -o tests/bin/arm/matrix_cal_openmp
    # Why choose blas single-thread with locking, See: http://www.openmathlib.org/OpenBLAS/docs/faq/#how-can-i-use-openblas-in-multi-threaded-applications
	clang++ src/load_imbalance_test.cpp -g3 -O2 -fopenmp -DARM -I/usr/local/kml/include -L/usr/local/kml/lib/neon/kblas/locking -lkblas -o tests/bin/arm/load_imbalance_test
	mpic++ src/matrix_cal_mpi_openmp.cpp -g3 -O2 -fopenmp -I./inc -o tests/bin/arm/matrix_cal_mpi_openmp
	clang++ src/datagen.cpp -g3 -O2 -I./inc -o tests/bin/arm/datagen
}

# 使用 getopt 处理参数
OPTS=$(getopt -o a: --long arch: -n 'script.sh' -- "$@")

if [ $? -ne 0 ]; then
    echo "参数解析错误" >&2
    exit 1
fi

eval set -- "$OPTS"

# 默认架构
ARCH="intel"

while true; do
    case "$1" in
        -a|--arch)
            ARCH="$2"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "内部错误!" >&2
            exit 1
            ;;
    esac
done

# 根据参数执行相应函数
if [ "$ARCH" = "intel" ]; then
    intel
elif [ "$ARCH" = "arm" ]; then
    arm
else
    echo "未知架构: $ARCH" >&2
    echo "用法: $0 -a|--arch [intel|arm]" >&2
    exit 1
fi