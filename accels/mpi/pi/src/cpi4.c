#include <stdio.h>
#include <math.h>
#include <mpi.h>

#define ll unsigned long long

int main(int argc, char** argv[]) {
	ll n;
	int id, numprocs;
	double pi = 0.0;

	MPI_Init(&argc, argv);
	MPI_Comm_size(MPI_COMM_WORLD, &numprocs);
	MPI_Comm_rank(MPI_COMM_WORLD, &id);

	n = 10000;

	MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);
	
	double sum = 0.0;
	for (ll k = id; k < n; k += numprocs) {
		// long double tn = 1.0;
		// if (k < 1024) {
			// tn = pow(3.0, (long double)k);
		// } else {
			// long double a = 3.0;
			// while (k) {
				// (k & 1)?tn*=a:0;
				// k >>= 1;
				// a*=a;
			// }
		// }
		sum += ((k % 2 == 0)?1.0:-1.0) / (pow(3.0, (double)k) * (2*k + 1));
	}
	
	MPI_Barrier(MPI_COMM_WORLD);
	MPI_Reduce(&sum, &pi, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);
	
	// 收集到0号进程
	if (id == 0) {
		pi *= 2.0 * sqrtl(3.0);
		printf("id: %d, pi: %.15lf\n", id, pi);
		FILE *fp = fopen("output.txt", "w");
		fprintf(fp, "%.15lf", pi);
		fclose(fp);
	}
	
	MPI_Finalize();
	return 0;
}