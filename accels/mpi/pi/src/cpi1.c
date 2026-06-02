#include <stdio.h>
#include <math.h>
#include <mpi.h>

// pi = 4 ∫^2_0 sqrt(1-x^2) dx ~= 4h ∑^{N-1}_0 sqrt(1-x_i^2) x_i=(i+1/2)h,h=1/N

#define ll unsigned long long

int main(int argc, char** argv[]) {
	ll n;
	int id, numprocs;
	double pi;

	MPI_Init(&argc, argv);
	MPI_Comm_size(MPI_COMM_WORLD, &numprocs);
	MPI_Comm_rank(MPI_COMM_WORLD, &id);

	n = 10000000;

	MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);
	
	double mypi, h, sum, x;
	h = 1.0 / (double)n;
	for (ll i = id + 1; i <= n; i+= numprocs) {
		x = h * ((double)i - 0.000001);
		sum += (4.0 / (1.0 + x * x));
	}
	mypi = h * sum;
	
	MPI_Reduce(&mypi, &pi, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

	FILE *fp = fopen("output.txt", "w");
	fprintf(fp, "%.15lf", pi);
	fclose(fp);

	MPI_Finalize();
	return 0;
}
