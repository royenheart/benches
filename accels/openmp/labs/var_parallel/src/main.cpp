#include <cstdio>
#include <omp.h>

int i = 0;
#pragma omp threadprivate(i)

int main(int argc, char* argv[]) {
    #pragma omp parallel 
    {
        int id = omp_get_thread_num();
        for (int k = 0; k < 4; k = k + 1) {
            i++;
            printf("%d: %d\n", id, i);
        }
    }

    printf("%d\n", i);

    #pragma omp parallel
    {
        int id = omp_get_thread_num();
        for (int k = 0; k < 4; k++) {
            i += 2;
            printf("%d: %d\n", id, i);
        }
    }

    printf("%d\n", i);
}