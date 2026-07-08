#include <cstdio>
#include <omp.h>

void func1(int id, int l, int r) {
    printf("task %d-%d, by thread %d\n", l, r, id);
}

int main(int argc, char* argv[]) {
    // #pragma omp task 
    // {
    //     omp_set_num_threads(4);
    //     #pragma omp parallel for
    //     for (int i = 0; i < 10; i++) {
    //         int id = omp_get_thread_num();
    //         printf("task1 loop by %d\n", id);
    //     }
    // }
    // #pragma omp task
    // {
    //     #pragma omp parallel for
    //     for (int i = 0; i < 10; i++) {
    //         int id = omp_get_thread_num();
    //         printf("task2 loop by %d\n", id);
    //     }
    // }
    // #pragma omp task
    // {
    //     #pragma omp parallel for
    //     for (int i = 0; i < 10; i++) {
    //         int id = omp_get_thread_num();
    //         printf("task3 loop by %d\n", id);
    //     }
    // }
    // #pragma omp task
    // {
    //     #pragma omp parallel for
    //     for (int i = 0; i < 10; i++) {
    //         int id = omp_get_thread_num();
    //         printf("task4 loop by %d\n", id);
    //     }
    // }
    // #pragma omp task
    // {
    //     #pragma omp parallel for
    //     for (int i = 0; i < 10; i++) {
    //         int id = omp_get_thread_num();
    //         printf("task5 loop by %d\n", id);
    //     }
    // }
    // #pragma omp task
    // {
    //     #pragma omp parallel for
    //     for (int i = 0; i < 10; i++) {
    //         int id = omp_get_thread_num();
    //         printf("task6 loop by %d\n", id);
    //     }
    // }
    // #pragma omp task
    // {
    //     #pragma omp parallel for
    //     for (int i = 0; i < 10; i++) {
    //         int id = omp_get_thread_num();
    //         printf("task7 loop by %d\n", id);
    //     }
    // }
    // #pragma omp task
    // {
    //     #pragma omp parallel for
    //     for (int i = 0; i < 10; i++) {
    //         int id = omp_get_thread_num();
    //         printf("task8 loop by %d\n", id);
    //     }
    // }
    #pragma omp parallel num_threads(4)
    {
        // single，最先进入的线程执行其中语句，默认隐式同步
        // 隐式同步可用于线程任务的发放（只有任务全部发布成功后才能继续执行）
        // + nowait clause 取消隐式同步，使得任务（task）不需要全部发布成功也能执行
        #pragma omp single nowait
        {
            int id = omp_get_thread_num();
            printf("Iam thread %d, doing task generate work!\n", id);
            for (int i = 0; i < 100; i+=10) {
                int k = i;
                // #pragma omp task is OpenMP 3.0+; MSVC /openmp (2.0) lacks it,
                // so guard it and run the body serially there.
#if defined(_OPENMP) && _OPENMP >= 200805
                #pragma omp task private(k) 
#endif
                {
                    int id = omp_get_thread_num();
                    func1(id, k, k + 10);
                }
            }
        }
        int id = omp_get_thread_num();
        printf("Thread %d finished work in parallel code area!\n", id);
    }
#if defined(_OPENMP) && _OPENMP >= 200805
    #pragma omp task
#endif
    {
        int id = omp_get_thread_num();
        printf("Thread %d get the task outside the parallel code!\n", id);
    }
    // 同步，只有当任务池中全部任务执行完毕后才能继续执行
#if defined(_OPENMP) && _OPENMP >= 200805
    #pragma omp taskwait
#endif
    printf("All tasks done!\n");
}