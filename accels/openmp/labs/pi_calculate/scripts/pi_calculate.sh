#!/bin/bash

mpiCC -fopenmp -Wignored-pragmas -o pi_calculate/seq -Dseq pi_calculate.cpp
mpiCC -fopenmp -Wignored-pragmas -o pi_calculate/slp_omp -Dslp_omp pi_calculate.cpp
mpiCC -fopenmp -Wignored-pragmas -o pi_calculate/slp_omp_v1 -Dslp_omp_v1 pi_calculate.cpp
mpiCC -fopenmp -Wignored-pragmas -o pi_calculate/slp_omp_v2 -Dslp_omp_v2 pi_calculate.cpp
mpiCC -fopenmp -Wignored-pragmas -o pi_calculate/slp_omp_synchronization -Dslp_omp_synchronization pi_calculate.cpp
mpiCC -fopenmp -Wignored-pragmas -o pi_calculate/worksharing_for -Dworksharing_for ./pi_calculate.cpp 
mpiCC -fopenmp -Wignored-pragmas -o pi_calculate/reduction_test -Dreduction_test ./pi_calculate.cpp 
mpiCC -fopenmp -fopenmp-extensions -Wignored-pragmas -o pi_calculate/reduction_plus_simd -Dreduction_plus_simd ./pi_calculate.cpp 

function test_right() {
    export OMP_PROC_BIND=true
    export OMP_PLACES=cores
    export OMP_NUM_THREADS=4

    files=$(ls pi_calculate)

    for file in ${files[@]}; do
        echo "~~~~~test ${file}~~~~~"
        time pi_calculate/${file}
        echo "~~~~~test ${file}~~~~~"
    done
}


# ------测试亲和度绑定对于可拓展性的影响------
# 测试结果：
# ~slp_omp - 测试未加亲和度绑定的可拓展性~
# 1: 0m0.289s, 2: 0m0.159s, 3: 0m0.114s, 4: 0m0.090s, 5: 0m0.073s, 6: 0m0.061s, 7: 0m0.068s, 8: 0m0.071s, 
# ~slp_omp - 测试未加亲和度绑定的可拓展性~
# ~slp_omp - 测试亲和度绑定后的可拓展性~
# 1: 0m0.283s, 2: 0m0.154s, 3: 0m0.107s, 4: 0m0.090s, 5: 0m0.075s, 6: 0m0.062s, 7: 0m0.061s, 8: 0m0.049s, 
# ~slp_omp - 测试亲和度绑定后的可拓展性~
# 测试结论：
# 加入亲和度绑定后，可拓展性有所提高
# ------测试亲和度绑定对于可拓展性的影响------

function affinity_with_scalability() {
    echo "~slp_omp - 测试未加亲和度绑定的可拓展性~"
    export OMP_PROC_BIND=false
    for (( i=1;i<=8;i=i+1 )); do
        export OMP_NUM_THREADS=$i
        usertime=$({ time pi_calculate/slp_omp; } 2>&1 | awk '/real/{print $2}')
        printf "%d: %s, " $i ${usertime}
    done
    printf "\n~slp_omp - 测试未加亲和度绑定的可拓展性~"

    printf "\n~slp_omp - 测试亲和度绑定后的可拓展性~\n"
    export OMP_PROC_BIND=true
    export OMP_PLACES=cores
    for (( i=1;i<=8;i=i+1 )); do
        export OMP_NUM_THREADS=$i
        usertime=$({ time pi_calculate/slp_omp; } 2>&1 | awk '/real/{print $2}')
        printf "%d: %s, " $i ${usertime}
    done
    printf "\n~slp_omp - 测试亲和度绑定后的可拓展性~\n"
}

# ------测试 False Sharing 对于可拓展性的影响------
# 测试结果：
# ~slp_omp_v1 vs. slp_omp_v2 - 测试 False Sharing 对可拓展性的影响~
# slp_omp_v1 - 1: 0m0.282s, 2: 0m0.388s, 3: 0m0.488s, 4: 0m0.392s, 5: 0m0.340s, 6: 0m0.306s, 7: 0m0.393s, 8: 0m0.373s, 
# slp_omp_v2 - 1: 0m0.294s, 2: 0m0.157s, 3: 0m0.113s, 4: 0m0.088s, 5: 0m0.086s, 6: 0m0.069s, 7: 0m0.060s, 8: 0m0.071s, 
# ~slp_omp_v1 vs. slp_omp_v2 - 测试 False Sharing 对可拓展性的影响~
# 测试结论：
# 缓存要熟记于心，对于缓存的读写若进行不当会严重影响性能
# ------测试 False Sharing 对于可拓展性的影响------

function false_sharing_to_scalability() {
    echo "~slp_omp_v1 vs. slp_omp_v2 - 测试 False Sharing 对可拓展性的影响~"
    # 关闭亲和度绑定，以测试缓存对于性能的影响
    export OMP_PROC_BIND=false
    printf "slp_omp_v1 - "
    for (( i=1;i<=8;i=i+1 )); do
        export OMP_NUM_THREADS=$i
        usertime=$({ time pi_calculate/slp_omp_v1; } 2>&1 | awk '/real/{print $2}')
        printf "%d: %s, " $i ${usertime}
    done
    printf "\nslp_omp_v2 - "
    for (( i=1;i<=8;i=i+1 )); do
        export OMP_NUM_THREADS=$i
        usertime=$({ time pi_calculate/slp_omp_v2; } 2>&1 | awk '/real/{print $2}')
        printf "%d: %s, " $i ${usertime}
    done
    printf "\n~slp_omp_v1 vs. slp_omp_v2 - 测试 False Sharing 对可拓展性的影响~\n"
}

# ------测试使用高级互斥同步抽象语句避免 False Sharing 对于可拓展性的影响------
# 测试结果：
# ~slp_omp_v2 vs. slp_omp_synchronization - 测试使用高级互斥同步抽象语句避免 False Sharing 对于可拓展性的影响~
# slp_omp_v2 - 1: 0m0.292s, 2: 0m0.152s, 3: 0m0.112s, 4: 0m0.089s, 5: 0m0.078s, 6: 0m0.095s, 7: 0m0.061s, 8: 0m0.072s, 
# slp_omp_synchronization - 1: 0m0.304s, 2: 0m0.155s, 3: 0m0.116s, 4: 0m0.086s, 5: 0m0.109s, 6: 0m0.084s, 7: 0m0.078s, 8: 0m0.068s, 
# ~slp_omp_v2 vs. slp_omp_synchronization - 测试使用高级互斥同步抽象语句避免 False Sharing 对于可拓展性的影响~
# 测试结论：
# 使用高级互斥同步抽象有利于简化代码，提升一定性能，减少不同平台的影响
# ------测试使用高级互斥同步抽象语句避免 False Sharing 对于可拓展性的影响------

function synchronization_false_sharing_to_scalability() {
    echo "~slp_omp_v2 vs. slp_omp_synchronization - 测试使用高级互斥同步抽象语句避免 False Sharing 对于可拓展性的影响~"
    # 关闭亲和度绑定，以测试缓存对于性能的影响
    export OMP_PROC_BIND=false
    printf "slp_omp_v2 - "
    for (( i=1;i<=8;i=i+1 )); do
        export OMP_NUM_THREADS=$i
        usertime=$({ time pi_calculate/slp_omp_v2; } 2>&1 | awk '/real/{print $2}')
        printf "%d: %s, " $i ${usertime}
    done
    printf "\nslp_omp_synchronization - "
    for (( i=1;i<=8;i=i+1 )); do
        export OMP_NUM_THREADS=$i
        usertime=$({ time pi_calculate/slp_omp_synchronization; } 2>&1 | awk '/real/{print $2}')
        printf "%d: %s, " $i ${usertime}
    done
    printf "\n~slp_omp_v2 vs. slp_omp_synchronization - 测试使用高级互斥同步抽象语句避免 False Sharing 对于可拓展性的影响~\n"
}

# ------测试 worksharing for------
# 测试结果：
# ~ 测试 worksharing for ~
# worksharing_for: 1: 0m0.290s, 2: 0m0.153s, 3: 0m0.121s, 4: 0m0.088s, 5: 0m0.078s, 6: 0m0.066s, 7: 0m0.057s, 8: 0m0.055s, 
# slp_omp_synchronization: 1: 0m0.294s, 2: 0m0.147s, 3: 0m0.107s, 4: 0m0.084s, 5: 0m0.072s, 6: 0m0.072s, 7: 0m0.060s, 8: 0m0.050s, 
# ~ 测试 worksharing for ~
# 测试结论：
# 
# ------测试 worksharing for------

function test_worksharing_for() {
    echo "~ 测试 worksharing for ~"
    export OMP_PROC_BIND=true
    export OMP_PLACES=cores
    printf "worksharing_for: "
    for (( i=1;i<=8;i=i+1 )); do
        export OMP_NUM_THREADS=$i
        usertime=$({ time pi_calculate/worksharing_for; } 2>&1 | awk '/real/{print $2}')
        printf "%d: %s, " $i ${usertime}
    done
    printf "\nslp_omp_synchronization: "
    for (( i=1;i<=8;i=i+1 )); do
        export OMP_NUM_THREADS=$i
        usertime=$({ time pi_calculate/slp_omp_synchronization; } 2>&1 | awk '/real/{print $2}')
        printf "%d: %s, " $i ${usertime}
    done
    printf "\n~ 测试 worksharing for ~\n"
}

# ------测试 reduction------
# 测试结果：
# ~ 测试 reduction ~
# reduction_test: 1: 0m0.282s, 2: 0m0.162s, 3: 0m0.113s, 4: 0m0.086s, 5: 0m0.079s, 6: 0m0.064s, 7: 0m0.058s, 8: 0m0.051s, 
# slp_omp_synchronization: 1: 0m0.274s, 2: 0m0.156s, 3: 0m0.107s, 4: 0m0.088s, 5: 0m0.073s, 6: 0m0.062s, 7: 0m0.059s, 8: 0m0.050s, 
# ~ 测试 reduction ~
# 测试结论：
# 
# ------测试 reduction------

function test_reduction() {
    echo "~ 测试 reduction ~"
    export OMP_PROC_BIND=true
    export OMP_PLACES=cores
    printf "reduction_test: "
    for (( i=1;i<=8;i=i+1 )); do
        export OMP_NUM_THREADS=$i
        usertime=$({ time pi_calculate/reduction_test; } 2>&1 | awk '/real/{print $2}')
        printf "%d: %s, " $i ${usertime}
    done
    printf "\nslp_omp_synchronization: "
    for (( i=1;i<=8;i=i+1 )); do
        export OMP_NUM_THREADS=$i
        usertime=$({ time pi_calculate/slp_omp_synchronization; } 2>&1 | awk '/real/{print $2}')
        printf "%d: %s, " $i ${usertime}
    done
    printf "\n~ 测试 reduction ~\n"
}

# ------对比 reduction/simd/seq------
# 测试结果：
# ~ 对比 reduction/simd/seq ~
# seq: 1: 0m0.278s, 2: 0m0.281s, 3: 0m0.279s, 4: 0m0.275s, 5: 0m0.272s, 6: 0m0.278s, 7: 0m0.282s, 8: 0m0.274s, 
# only reduction: 1: 0m0.285s, 2: 0m0.158s, 3: 0m0.109s, 4: 0m0.085s, 5: 0m0.078s, 6: 0m0.064s, 7: 0m0.057s, 8: 0m0.049s, 
# reduction with simd: 1: 0m0.280s, 2: 0m0.153s, 3: 0m0.110s, 4: 0m0.092s, 5: 0m0.071s, 6: 0m0.060s, 7: 0m0.064s, 8: 0m0.055s, 
# ~ 对比 reduction/simd/seq ~
# 测试结论：
# 
# ------对比 reduction/simd/seq------

function reduction_simd_seq() {
    echo "~ 对比 reduction/simd/seq ~"
    export OMP_PROC_BIND=true
    export OMP_PLACES=cores
    printf "seq: "
    for (( i=1;i<=8;i=i+1 )); do
        export OMP_NUM_THREADS=$i
        usertime=$({ time pi_calculate/seq; } 2>&1 | awk '/real/{print $2}')
        printf "%d: %s, " $i ${usertime}
    done
    printf "\nonly reduction: "
    for (( i=1;i<=8;i=i+1 )); do
        export OMP_NUM_THREADS=$i
        usertime=$({ time pi_calculate/reduction_test; } 2>&1 | awk '/real/{print $2}')
        printf "%d: %s, " $i ${usertime}
    done
    printf "\nreduction with simd: "
    for (( i=1;i<=8;i=i+1 )); do
        export OMP_NUM_THREADS=$i
        usertime=$({ time pi_calculate/reduction_plus_simd; } 2>&1 | awk '/real/{print $2}')
        printf "%d: %s, " $i ${usertime}
    done
    printf "\n~ 对比 reduction/simd/seq ~\n"
}

# test_right
affinity_with_scalability
false_sharing_to_scalability
synchronization_false_sharing_to_scalability
test_worksharing_for
test_reduction
reduction_simd_seq