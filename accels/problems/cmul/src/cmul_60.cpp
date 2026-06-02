#include <iostream>
#include <fstream>
#include <iomanip>
#include <cstdio>
#include <omp.h>
#include "rhs.h"

// 60/90

using namespace std;

double *out = NULL;

int main(int argc, char* argv[]) {
    uint N1 = atoll(argv[1]);
    uint N2 = atoll(argv[2]);
    uint N3 = atoll(argv[3]);

    out = new double[N1 * N3];

    omp_set_num_threads(8);

    // dataPara(0, N1 - 1, 0, N3 - 1, 0, N2 - 1);
    #pragma omp parallel for num_threads(8) schedule(dynamic, 4096) proc_bind(close)
    for (uint t = 0; t < N1*N3; ++t) {
        uint i = t / N3;
        uint j = t % N3;
        double tk = 0.0;
        for (uint k = 0; k < N2; ++k) {
            double a, b;
            matA(i, k, a);
            matB(k, j, b);
            tk = a * b + tk;
        }
        // cal out(i,j)
        out[i * N3 + j] = tk;
    }

    #pragma omp taskwait

    ofstream output;
    output.open("output.dat");

    for (uint t = 0; t < N1*N3; ++t) {
        uint i = t / N3;
        uint j = t % N3;
        output << setprecision(12) << out[i * N3 + j] << endl;
    }
    
    output.close();
    delete []out;
}