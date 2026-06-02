#!/bin/bash

function compile() {
    # g++ -O0 -g -ggdb -Wall -DDebug -std=c++17 omp_cmul.cpp rhs.cpp -fopenmp -lm -o omp_cmul
    g++ -O3 -Wall -Wno-pragmas -std=c++17 -fopenmp -lm -o ./out/omp_cmul omp_cmul.cpp rhs.cpp
    g++ -O3 -Wall -Wno-pragmas -std=c++17 -lm -o ./out/gen_matrix gen_matrix.cpp rhs.cpp 
}

function test_right() {
    if [[ ! -e ./rights/right.$1.$2.$3.dat ]]; then
        ./out/gen_matrix $1 $2 $3
        mv right.dat ./rights/right.$1.$2.$3.dat
    fi
    echo "SEQ DONE! NOW TEST PARALLEL"
    for (( i=1;i<30;i=i+1 )); do
        ./out/omp_cmul $1 $2 $3
        rm -f ./outputs/output.$1.$2.$3.dat
        mv output.dat ./outputs/output.$1.$2.$3.dat
        cmp ./outputs/output.$1.$2.$3.dat ./rights/right.$1.$2.$3.dat
        if [[ $? == 1 ]]; then
            echo "ERROR: N1:$1 N2:$2 N3:$3"
            return
        else
            echo "DONE: N1:$1 N2:$2 N3:$3"
        fi
    done
}

function test_runtime() {
    export OMP_NUM_THREADS=8
    export OMP_PROC_BIND=true
    export OMP_PLACES=cores

    printf "RUNTIME: N1: 10, N2: 10, N3: 10\n"
    perf stat -a -d -d -d ./omp_cmul 10 10 10 |& grep -E "misses|stalled-cycles|seconds"
    mv output.dat ./outputs/output.RUNTIME.10.10.10.dat
    sync; sync;

    printf "RUNTIME: N1: 10240, N2: 10, N3: 10\n" 
    perf stat -a -d -d -d ./omp_cmul 10240 10 10 |& grep -E "misses|stalled-cycles|seconds"
    mv output.dat ./outputs/output.RUNTIME.10240.10.10.dat
    sync; sync;

    printf "RUNTIME: N1: 10, N2: 10240, N3: 10\n"
    perf stat -a -d -d -d ./omp_cmul 10 10240 10 |& grep -E "misses|stalled-cycles|seconds"
    mv output.dat ./outputs/output.RUNTIME.10.10240.10.dat
    sync; sync;

    printf "RUNTIME: N1: 10, N2: 100, N3: 10240\n"
    perf stat -a -d -d -d ./omp_cmul 10 100 10240 |& grep -E "misses|stalled-cycles|seconds"
    mv output.dat ./outputs/output.RUNTIME.10.100.10240.dat
    sync; sync;

    printf "RUNTIME: N1: 1024, N2: 64, N3: 1024\n" 
    perf stat -a -d -d -d ./omp_cmul 1024 64 1024 |& grep -E "misses|stalled-cycles|seconds"
    mv output.dat ./outputs/output.RUNTIME.1024.64.1024.dat
    sync; sync;
}

function test_magic_parts() {
    export OMP_NUM_THREADS=8
    export OMP_PROC_BIND=true
    export OMP_PLACES=cores
    for (( i=2;i<128;i=i*2 )); do
        g++ -O3 -Wall -Wno-pragmas -std=c++17 -fopenmp -lm -DDebug -DMAGIC_NUM_PARTS=$i -o ./out/omp_cmul omp_cmul.cpp rhs.cpp
        printf "DEBUG-PARTS: %d, TEST 1024 10240 1024;\n" $i
        perf stat -a -d -d -d ./out/omp_cmul 1024 10240 1024
    done
    rm -f ./output.dat
}

# compile
# test_right $@
test_magic_parts
# test_runtime