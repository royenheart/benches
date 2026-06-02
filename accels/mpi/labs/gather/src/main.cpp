#include <cstdio>
#include <cstdlib>
#include <mpi.h>
#include <stress.hpp>

int main(int argc, char* argv[]) {
    int procs, id;
    int m, n, k;
    if (argc <= 3) {
        std::cout << "usage: ./<program> <m> <n> <k>" << std::endl;
    }
    m = atoi(argv[1]);
    n = atoi(argv[2]);
    k = atoi(argv[3]);
    double *r = NULL;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &id);
    MPI_Comm_size(MPI_COMM_WORLD, &procs);

    if (id == 0) {
        r = (double*)malloc(m * n * procs * sizeof(double));
    }

    double *c = matrix_cal(m, n, k);
    printf("I'am %d: \n", id);
    print_matrix(c, m, n);

    MPI_Barrier(MPI_COMM_WORLD);
    // 多到一，每个进程向接收进程发送数据，接收数据得到的数据按进程顺序号排序
    MPI_Gather(c, m * n, MPI_DOUBLE, r, m * n, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    if (id == 0) {
        printf("Final:\n");
        print_matrix(r, m, n * procs);
    }

    MPI_Finalize();
    return 0;
}