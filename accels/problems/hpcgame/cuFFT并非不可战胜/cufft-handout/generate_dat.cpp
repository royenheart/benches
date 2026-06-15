#include <complex>
#include <ios>
#include <string>
#include <vector>
#include <stdlib.h>
#include <time.h>
#include <assert.h>
#include <cstring>
#include <iostream>
#include <unistd.h>
#include <fstream>
#include <complex>
#include <random>
#include <chrono>

std::complex<double> randn() {
    std::random_device rd;
    std::mt19937 mt(rd());
    std::normal_distribution<double> dist(0, 1);
    return std::complex<double> {dist(mt), dist(mt)};
}

void init_edge(std::vector<int> &edge) {
    for(int ii = 0; ii < edge.size(); ii++) {
        if (edge[ii] % 2 == 0) {
            edge[ii] += 1;
        }
    } 
}

void gen_data(int c, int r, std::complex<double> **in) {
    int n = c * c * c;

    *in = (std::complex<double> *)malloc(sizeof(std::complex<double>) * n);

    // There will be a better way to init data, but I am lazy
    for (int ii = 0; ii < c; ii++) {
        int idx_ii = ii * c * c;
        for (int jj = 0; jj < c; jj++) {
            int idx_jj = idx_ii + jj * c;
            for (int kk = 0; kk < c; kk++) {
                int dis_2 = (ii - c/2) * (ii - c/2) +
                            (jj - c/2) * (jj - c/2) +
                            (kk - c/2) * (kk - c/2);
                if (dis_2 > r * r) {
                    (*in)[idx_jj + kk] = std::complex<double> (0, 0);
                }
                else {
                    (*in)[idx_jj + kk] = randn();
                }
            }
        }
    }
}

int main()
{
	std::vector<int> edge_config = {32, 32, 64, 64, 128, 128, 256, 256, 512, 512};
	std::vector<int> radius_config = {8, 6, 16, 12, 32, 24, 64, 48, 96, 128};
    const int repeat_time = 10;

    assert(edge_config.size() == radius_config.size());

    std::complex<double> *in_data;

    init_edge(edge_config);
    int num_cases = edge_config.size();

    for (int ii = 0; ii < num_cases; ii++) {
        int c = edge_config[ii];
		int n = c * c * c;
        for (int num = 0; num < repeat_time; num ++) {
            gen_data(c, radius_config[ii], &in_data);
            std::cout << "Case " << ii << " " << num << std::endl;
            std::cout << "Edge: " << c << std::endl;
            std::cout << "Radius: " << radius_config[ii] << std::endl;

            std::ofstream fout;
            std::string filename = "c_" + std::to_string(c) + "_r_" + std::to_string(radius_config[ii]) + "_" + std::to_string(num) + ".dat";
            // open binary file for output
            fout.open(filename, std::ios_base::out | std::ios_base::binary);
            // write data to binary file
            fout.write((char *)in_data, sizeof(std::complex<double>) * n);
            // close file
            fout.close();
            free(in_data);
        }
    }

}
