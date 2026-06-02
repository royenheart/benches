#include <fstream>
#include <iostream>
#include <iomanip>
#include <omp.h>
#include "rhs.h"

using namespace std;

int main(int argc, char* argv[]) {
    int N = atoi(argv[1]);
    double out = 0.0;
    double halfN = 1.0 / (2.0 * N);
    #pragma omp parallel for simd reduction(+ : out)
    for (int i = 0; i < N; i++) {
        double a = (double)i / (double)N + halfN;
        double b = 0.0;
        rhs(a, b);
        out = out + b;
    }
    out = 1.0 / N * out;
    ofstream output;
    output.open("output.dat");
    output << setprecision(12) << out << endl;
    output.close();
}