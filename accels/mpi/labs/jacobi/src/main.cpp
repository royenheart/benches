#include <cstdio>
#include <mpi.h>
#include <stress.hpp>

int main(int argc, char* argv[]) {
    int procs, id;
    int n, iter;
    if (argc <= 2) {
        std::cout << "usage: ./<program> <n> <iter>" << std::endl;
    }
    n = atoi(argv[1]);
    iter = atoi(argv[2]);
    double *A = NULL;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &id);
    MPI_Comm_size(MPI_COMM_WORLD, &procs);

    if (id == 0) {
        r = (double*)malloc(m * n * procs * sizeof(double));
    }
}