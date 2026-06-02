#include <iostream>
#include <mpi.h>
#include <cblas.h>
#include <stress.hpp>

int main(int argc, char* argv[]) {
    // MPI 通信-组通信
    // 1. 一到多（Broadcast，Scatter）
    // 2. 多到一（Reduce，Gather）
    // 3. 多到多（Allreduce，Allgather）
    // 4. 同步（Barrier）

    int procs, id;
    int m, n, k;
    if (argc <= 3) {
        std::cout << "usage: ./<program> <m> <n> <k>" << std::endl;
    }
    m = atoi(argv[1]);
    n = atoi(argv[2]);
    k = atoi(argv[3]);
    double ret[m][n];

	MPI_Init(&argc, &argv);
    // 获取全部进程数
	MPI_Comm_size(MPI_COMM_WORLD, &procs);
    // 获取当前进程 id
	MPI_Comm_rank(MPI_COMM_WORLD, &id);

    #ifdef Bcast
    int ss;

    if (id == 0) {
        std::cin >> ss;
    }

    // 一到多广播，将得到的信息传给其他进程
	MPI_Bcast(&ss, 1, MPI_INT, 0, MPI_COMM_WORLD);
    
    std::cout << id << " receive " << ss << std::endl;
    #endif

    double *c = NULL;
    c = matrix_cal(m, n, k);

    MPI_Barrier(MPI_COMM_WORLD);
    // 多到一收集
    // 由各个 sendbuf 送到 MPI_COMM_WORLD 通道的 0 号进程（root）的 recvbuf 中，并进行 MPI_SUM 操作
	MPI_Reduce(c, ret, m * n, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);
	MPI_Finalize();

    std::cout << id << ":" << std::endl;
    print_matrix(c, m, n);

	return 0;
}