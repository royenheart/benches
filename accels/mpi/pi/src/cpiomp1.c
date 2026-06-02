#include <stdio.h>
#include <math.h>
#include <mpi.h>
#include <omp.h>

double f(double a);
double f(double a) {
	return (4.0 / (1.0 + a * a));
}

int main(int argc, char** argv[]) {
	unsigned long long n;
	int id, numprocs, i;
	double mypi, pi, h, sum, x;
	double start = 0.0, end;
	int namelen;
	char processor_name[MPI_MAX_PROCESSOR_NAME];
	MPI_Init(&argc, argv);
	MPI_Comm_size(MPI_COMM_WORLD, &numprocs);
	MPI_Comm_rank(MPI_COMM_WORLD, &id);
	MPI_Get_processor_name(processor_name, &namelen);

	n = 10000000000;

	MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);
	h = 1.0 / (double) n;
	
	#pragma omp parallel for simd reduction(+:sum) private(x)
	for (unsigned long long i = id + 1; i <= n; i+= numprocs) {
		x = h * ((double)i - 0.00001);
		sum += f(x);
	}
	mypi = h * sum;
	MPI_Reduce(&mypi, &pi, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

	MPI_Finalize();
	return 0;
}
