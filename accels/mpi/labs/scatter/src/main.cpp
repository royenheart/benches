#include <iostream>
#include <mpi.h>
#include <vector>
#include <cstdio>
#include <cstdlib>

#define N 10

int main(int argc, char* argv[]) {
    int procs, id;

    if (argc != 2) {
        printf("usage: ./<program> <recv_n>\n");
        exit(EXIT_FAILURE);
    }
    int recv_n = atoi(argv[1]);

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &procs);
    MPI_Comm_rank(MPI_COMM_WORLD, &id);

    if (procs < 2) {
        printf("Please use at least 2 procs\n");
        MPI_Abort(MPI_COMM_WORLD, MPI_ERR_NO_MEM);
    }
    
    int *send = (int*)malloc(N * procs * sizeof(int));
    int *recv = (int*)malloc(N * sizeof(int));
    // memset(recv, 0, N * sizeof(int));

    if (id == 0) {
        for (int i = 0; i < procs * N; i++) {
            send[i] = i * 2;
        }
    }

    // 向各个进程发送数组内的部分数据
    MPI_Scatter(send, N, MPI_INT, recv, N, MPI_INT, 0, MPI_COMM_WORLD);

    printf("I'am %d\n", id);
    for (int i = 0; i < N; i++) {
        printf("%d reveive recv[%d]=%d\n", id, i, recv[i]);
    }

    MPI_Finalize();
}