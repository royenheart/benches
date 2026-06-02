#include "rhs.h"
#include <fstream>
#include <iostream>
#include <iomanip>
#include <chrono>

double out[10000][10000];

using namespace std;

int main(int argc, char *argv[]) {
    uint N1 = atoi(argv[1]);
    uint N2 = atoi(argv[2]);
    uint N3 = atoi(argv[3]);

    // for (uint i = 0; i < N1; i++) {
    //     for (uint j = 0; j < N2; j++) {
    //         uint &ir = i;
    //         uint &jr = j;
    //         double t;
    //         double &tr = t;
    //         matA(ir, jr, tr);
    //         std::cout << tr << " ";
    //     }
    //     std::cout << std::endl;
    // }
    
    // for (uint i = 0; i < N2; i++) {
    //     for (uint j = 0; j < N3; j++) {
    //         uint &ir = i;
    //         uint &jr = j;
    //         double t;
    //         double &tr = t;
    //         matB(ir, jr, tr);
    //         std::cout << tr << " ";
    //     }
    //     std::cout << std::endl;
    // }

    for (uint i = 0; i < N1; i++) {
        for (uint j = 0; j < N3; j++) {
            for (uint k = 0; k < N2; k++) {
                double t1, t2;
                matA(i, k, t1);
                matB(k, j, t2);
                out[i][j] += t1 * t2;
            }
        }
    }

    ofstream output;
    output.open("right.dat");

    for (uint i = 0; i < N1; i++) {
        for (uint j = 0; j < N3; j++) {
            output << setprecision(12) << out[i][j] << endl;
        }
    }
    
    output.close();
}