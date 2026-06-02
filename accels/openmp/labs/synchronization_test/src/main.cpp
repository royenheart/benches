#include <omp.h>
#include <iostream>
#include <cstdio>

#define MAX_NUM_THREADS 100

int main(int argc, char* argv[]) {
    int arr[MAX_NUM_THREADS][8] = {0};
    int res = 0;
    #pragma omp parallel
    {
        int id = omp_get_thread_num();
        int ids = omp_get_num_threads();
        int pos = (id == ids - 1)?0:id + 1;
        arr[id][0] = id + 1;
        // 使用屏障同步
        #pragma omp barrier
        printf("From thread %d: %d\n", id, arr[pos][0]);
        // 使用 Critical 实现互斥（接下来的代码段实现互斥机制）
        // 以下输出如果不进行互斥，输出将不会按照应该的样子进行
        #pragma omp critical
        {
            std::cout << "check if critical protects this sentence output right" << std::endl;
        }
        // 使用原子操作更新数据（需要硬件支持，可简化 Critical 互斥）
        // 支持的形式如下：
        // x binop= expr
        // x++
        // ++x
        // x--
        // --x
        // x 为标量类型的左值，操作符为未被重载的内置操作数
        #pragma omp atomic
        res += arr[pos][0];
    }
}