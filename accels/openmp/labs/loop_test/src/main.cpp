#include <cstdio>
#include <omp.h>

#define MAX 100000000

void seq_v() {
    int i, j;
    static int A[MAX] = {0};
    j = 5;
    double t_start = omp_get_wtime();
    for (i = 0; i < MAX; i++) {
        j += 2;
        A[i] *= j / 2;
    }  
    double t_end = omp_get_wtime();
    printf("Calculate Time: %fs\n", (t_end - t_start));
}

void omp_v() {
    static int A[MAX] = {0};
    int i, j;
    j = 5;
    double t_start = omp_get_wtime();
    for (i = 0; i < MAX; i++) {
        j += 2;
        A[i] *= j / 2;
    }  
    double t_end = omp_get_wtime();
    printf("Calculate Time: %fs\n", (t_end - t_start));
}

int main(int argc, char* argv[]) {
    int i, j;
    static int A[MAX] = {0};
    j = 5;
    for (i = 0; i < MAX; i++) {
        j += 2;
        A[i] *= j / 2;
    }
}