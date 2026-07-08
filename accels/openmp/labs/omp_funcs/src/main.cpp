#include <omp.h>
#include <cstdio>

int main(int argc, char *argv[]) {
    int numT = 0;
    int numP = 0;
    int numPlace = 0;
    // omp_get_proc_bind(), omp_proc_bind_true, the proc_bind() clause and
    // omp_get_num_places() are OpenMP 4.0+ features. MSVC /openmp only
    // implements OpenMP 2.0, so guard them and use a 2.0 fallback there.
#if defined(_OPENMP) && _OPENMP >= 201307
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
#else
    printf("proc bind / places API requires OpenMP 4.0+ (MSVC /openmp is 2.0)\n");
    #pragma omp parallel shared(numT, numP) num_threads(3)
    {
        #pragma omp master
        {
            // 线程数
            numT = omp_get_num_threads();
            // 处理核心数量
            numP = omp_get_num_procs();
        }
    }
#endif
    printf("num threads: %d, num procs: %d, num places: %d\n", numT, numP, numPlace);
}