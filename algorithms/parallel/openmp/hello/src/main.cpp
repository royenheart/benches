#include <iostream>
#include <omp.h>
#include <cstdio>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "输入一个参数表示线程数" << std::endl;
        return EXIT_FAILURE;
    }

    int thread_count = std::atoi(argv[1]);

    int i, j;
    #pragma omp parallel num_threads(thread_count) private(i, j)
    {
        int me = omp_get_thread_num();
        int all = omp_get_num_threads();

        printf("%d from %d\n", me, all);
        for (i = 0; i < 2; i++) {
            printf("%d got i: %d\n", me, i);
            #pragma omp for
            for (j = 1; j < 11; j++) {
                printf("%d got j: %d\n", me, j);
            }
        }
    }
}