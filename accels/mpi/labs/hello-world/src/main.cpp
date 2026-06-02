#include <iostream>
#include <cstdio>
#include <mpi.h>

#define ll unsigned long long

int main(int argc, char** argv[]) {
	int id, numprocs;

	MPI_Init(&argc, argv);
	MPI_Comm_size(MPI_COMM_WORLD, &numprocs);
	MPI_Comm_rank(MPI_COMM_WORLD, &id);

	printf("Hello from %d in %d\n", id, numprocs);

	MPI_Barrier(MPI_COMM_WORLD);
	MPI_Finalize();

	return 0;
}