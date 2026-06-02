#include <omp.h>
#include <cstdio>
#include <ctime>
#include <random>

#define N 100

int main(int argc, char* argv[]) {
    srand((unsigned)time(NULL));
    
    double arr[N];
    double out[N / 2];

    for (int i = 0; i < N; i++) {
        arr[i] = (double)(rand() % 100);
    }

    #pragma omp parallel
    {
        int ids = omp_get_num_threads();
        int id = omp_get_thread_num();
        int sec = N / ids;
        int start = id * sec;
        int end = (id == ids - 1)?N:start + sec;
        printf("Iam id: %d, resolve data from index %d to %d\n", id, start, end);
        for (int i = start; i < end; i += 2) {
            out[i / 2] = arr[i] + arr[i + 1];
        }
    }
    
    for (int i = 0; i < N / 2; i++) {
        if (out[i] != arr[2 * i] + arr[2 * i + 1]) {
            printf("Not right!\n");
            return EXIT_SUCCESS;
        }
    }
    printf("Right!\n");
    return EXIT_SUCCESS;
}