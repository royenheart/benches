#include <complex>
#include <fstream>
#include <string>
#include <vector>
#include <stdlib.h>
#include <time.h>
#include <assert.h>
#include <cstring>
#include <iostream>
#include <unistd.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <iosfwd>


#include <cufft.h>
#include <cuda_runtime.h>

#include "common.h"

extern void my_fft(int c, int r, std::complex<double> *in, std::complex<double> *out);

inline void cuAssert(cudaError_t status, const char *file, int line) {
    if (status != cudaSuccess)
        std::cerr<<"cuda assert: "<<cudaGetErrorString(status)<<", file: "<<file<<", line: "<<line<<std::endl;
}
#define cuErrCheck(res)                                 \
    {                                                   \
        cuAssert((res), __FILE__, __LINE__);            \
    }

void init_edge(std::vector<int> &edge) {
    for(int ii = 0; ii < edge.size(); ii++) {
        if (edge[ii] % 2 == 0) {
            edge[ii] += 1;
        }
    } 
}

void start_case(int c, int r, int num, std::complex<double> **in, std::complex<double>**out, const std::string filename) {
    std::cout << "filename = " << filename << std::endl;

    int n = c * c * c;
    //mmap to read data
    int fd = open(filename.c_str(), O_RDONLY);
    if (fd == -1) {
        std::cerr<<"open file error"<<std::endl;
        exit(1);
    }
    struct stat sb;
    if (fstat(fd, &sb) == -1) {
        std::cerr<<"fstat error"<<std::endl;
        exit(1);
    }
    if (!S_ISREG(sb.st_mode)) {
        std::cerr<<"not a regular file"<<std::endl;
        exit(1);
    }
    *in = (std::complex<double> *)mmap(NULL, n * sizeof(std::complex<double>), PROT_READ, MAP_PRIVATE, fd, 0);
    if (*in == MAP_FAILED) {
        std::cerr<<"mmap error"<<std::endl;
        exit(1);
    }
    close(fd);

    // mmap to output/c_c_r_r_num.dat
    std::string out_filename = "output/c_" + std::to_string(c) + "_r_" + std::to_string(r) + "_" + std::to_string(num) + ".dat";
    int out_fd = open(out_filename.c_str(), O_RDWR | O_CREAT, 0666);
    if (out_fd == -1) {
        std::cerr<<"open file error"<<std::endl;
        exit(1);
    }
    if (ftruncate(out_fd, n * sizeof(std::complex<double>)) == -1) {
        std::cerr<<"ftruncate error"<<std::endl;
        exit(1);
    }
    *out = (std::complex<double> *)mmap(NULL, n * sizeof(std::complex<double>), PROT_READ | PROT_WRITE, MAP_SHARED, out_fd, 0);
    if (*out == MAP_FAILED) {
        std::cerr<<"mmap error"<<std::endl;
        exit(1);
    }
    close(out_fd);
}

void warmup_cufft(int c) {
    cufftHandle plan;
    cufftPlan3d(&plan, c, c, c, CUFFT_Z2Z);
    cufftDestroy(plan);
}

void end_case(int c, std::complex<double> **in, std::complex<double> **out) {
    int n = c * c * c;
    munmap(*in, n * sizeof(std::complex<double>));
    munmap(*out, n * sizeof(std::complex<double>));
}

int main(int argc, char** argv)
{
    const int repeat_time = 10;

    std::complex<double> *in_data;
    std::complex<double> *out_data;
    std::complex<double> *in_data_d;
    std::complex<double> *out_data_d;

    std::vector<double> time_vec;

    // read c, r from command line
    int c = atoi(argv[1]);
    int r = atoi(argv[2]);
    int num_cases = atoi(argv[3]);

    int n = c * c * c;

    for(int num = 0; num < repeat_time; num++){

        std::string filename = "data/c_" + std::to_string(c) + "_r_" + std::to_string(r) + "_" + std::to_string(num) + ".dat";

        start_case(c, r, num, &in_data, &out_data, filename);
        cudaMalloc((void **)&in_data_d, sizeof(std::complex<double>) * n);
        cudaMalloc((void **)&out_data_d, sizeof(std::complex<double>) * n);
        cudaMemcpy(in_data_d, in_data, sizeof(std::complex<double>) * n, cudaMemcpyHostToDevice);

        float time_elapsed = 0.0;
        float sum_time = 0.0;
        cudaEvent_t start,stop;
        cudaEventCreate(&start);
        cudaEventCreate(&stop);
        warmup_cufft(c);
        cudaEventRecord(start);
        
        std::cout << 1 << std::endl;
        my_fft(c, r, in_data_d, out_data_d);
        cudaDeviceSynchronize();
        cuErrCheck(cudaGetLastError());

        std::cout << 2 << std::endl;

        cudaEventRecord(stop);
        cudaEventSynchronize(stop);
        cudaEventElapsedTime(&time_elapsed,start,stop);
        sum_time += time_elapsed;
        
        std::cout << 1 << std::endl;

        cudaMemcpy(out_data, out_data_d,
                sizeof(std::complex<double>) * c * c * c, cudaMemcpyDeviceToHost);
        cudaFree(out_data_d);
        cudaFree(in_data_d);
        time_vec.push_back(time_elapsed);
        end_case(c, &in_data, &out_data);

    }
    #ifdef DEBUG
    std::cout << "time = " << sum_time << " ms" << std::endl;
    #endif
    // save the time
    std::string filename = "time/" + std::to_string(c) + "_" + std::to_string(r) + ".txt";
    std::ofstream outfile;
    outfile.open(filename);
    for(int ii = 0; ii < time_vec.size(); ii++) {
        outfile << time_vec[ii] << std::endl;
    }
    outfile.close();
    return 0;
}

