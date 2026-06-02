#include <omp.h>
#include <cstdio>

int main(int argc, char *argv[]) {
    int numT;
    int numP;
    int numPlace;
    int is_proc_bind = omp_get_proc_bind();
    if (is_proc_bind == omp_proc_bind_true) {
        printf("proc bind on!\n");
    } else {
        printf("proc bind off!\n");
    }
    #pragma omp parallel shared(numT, numP, numPlace) proc_bind(spread) num_threads(3)
    {
        #pragma omp master 
        {
            // 线程数
            numT = omp_get_num_threads();
            // 处理核心数量
            numP = omp_get_num_procs();
            // 线程设置分布的核数
            numPlace = omp_get_num_places(); 
        }
    }
    printf("num threads: %d, num procs: %d, num places: %d\n", numT, numP, numPlace);
}