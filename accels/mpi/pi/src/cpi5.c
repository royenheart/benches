#include <stdio.h>
#include <math.h>
#include <mpi.h>

// Gauss-Leren's German algorithm

#define ll unsigned long long

int main(int argc, char** argv[]) {
	ll n;
	int id, numprocs;
	double pi;

	MPI_Init(&argc, argv);
	MPI_Comm_size(MPI_COMM_WORLD, &numprocs);
	MPI_Comm_rank(MPI_COMM_WORLD, &id);

	n = 1000000000;

	MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);
	
	double sum = 0.0;
	for (ll k = id; k < n; k += numprocs) {
		 
	}
	
	MPI_Reduce(&sum, &pi, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

	pi *= 4.0;

	FILE *fp = fopen("output.txt", "w");
	fprintf(fp, "%.15lf", pi);
	fclose(fp);

	MPI_Finalize();
	return 0;
}
