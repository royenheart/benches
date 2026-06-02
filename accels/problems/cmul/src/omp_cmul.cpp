#include <iostream>
#include <fstream>
#include <iomanip>
#include <omp.h>
#include <cstdlib>
#include <cstring>
#include "rhs.h"

using namespace std;

#define MAGIC_NUM_PARTS 384
#define MAGIC_NUM_MID 16384

double *out = NULL;
int threads_num = 0;
uint part = 0;
bool is_small_use_parallel = true;

double* dataPara(uint il, uint ir, uint jl, uint jr, uint kl, uint kr) {
    // 元素个数
    uint iw = ir - il + 1;
    uint jw = jr - jl + 1;
    uint kw = kr - kl + 1;
    double *tmp = (double*)calloc(sizeof(double), iw * jw);

    if (iw*jw <= part) {
        // 取数据必须对应最开始的矩阵（matA，matB）
        #pragma omp parallel for schedule(dynamic, 512) proc_bind(close) if(is_small_use_parallel)
        for (uint i = il; i < ir + 1; ++i) {
            for (uint j = jl; j < jr + 1; ++j) {
                double ko = 0.0;
                for (uint k = kl; k < kr + 1; ++k) {
                    double a, b;
                    matA(i, k, a);
                    matB(k, j, b);
                    ko = a * b + ko;
                }
                tmp[(i-il) * jw + (j-jl)] += ko;
            }
        }
    } else {
        uint midil = il + (iw+1)/2-1;
        uint midir = midil + 1;
        uint midjl = jl + (jw+1)/2-1;
        uint midjr = midjl + 1;
        uint midkl = kl + (kw+1)/2-1;
        uint midkr = midkl + 1;
        double *p0 = NULL, *p1 = NULL, *p2 = NULL, *p3 = NULL;
        double *p4 = NULL, *p5 = NULL, *p6 = NULL, *p7 = NULL;
        // #pragma omp task shared(p0)
        // {
        //     p0 = dataPara(il, midil, jl, midjl, kl, midkl);
        // }
        // #pragma omp task shared(p1)
        // {
        //     p1 = dataPara(il, midil, jl, midjl, midkr, kr); 
        // }
        // #pragma omp task shared(p2)
        // {
        //     p2 = dataPara(il, midil, midjr, jr, kl, midkl); 
        // } 
        // #pragma omp task shared(p3)
        // {
        //     p3 = dataPara(il, midil, midjr, jr, midkr, kr);
        // }
        // #pragma omp task shared(p4)
        // {
        //     p4 = dataPara(midir, ir, jl, midjl, kl, midkl); 
        // }
        // #pragma omp task shared(p5)
        // {
        //     p5 = dataPara(midir, ir, jl, midjl, midkr, kr); 
        // }
        // #pragma omp task shared(p6)
        // {
        //     p6 = dataPara(midir, ir, midjr, jr, kl, midkl); 
        // }
        // #pragma omp task shared(p7)
        // {
        //     p7 = dataPara(midir, ir, midjr, jr, midkr, kr);
        // }
        
        // #pragma omp task shared(p0, p1)
        // {
        //     p0 = dataPara(il, midil, jl, midjl, kl, midkl);
        //     p1 = dataPara(il, midil, jl, midjl, midkr, kr); 
        // }
        // #pragma omp task shared(p2, p3)
        // {
        //     p2 = dataPara(il, midil, midjr, jr, kl, midkl); 
        //     p3 = dataPara(il, midil, midjr, jr, midkr, kr);
        // }
        // #pragma omp task shared(p4, p5)
        // {
        //     p4 = dataPara(midir, ir, jl, midjl, kl, midkl); 
        //     p5 = dataPara(midir, ir, jl, midjl, midkr, kr); 
        // }
        // #pragma omp task shared(p6, p7)
        // {
        //     p6 = dataPara(midir, ir, midjr, jr, kl, midkl); 
        //     p7 = dataPara(midir, ir, midjr, jr, midkr, kr);
        // }

        #pragma omp task shared(p0, p1, p2, p3)
        {
            p0 = dataPara(il, midil, jl, midjl, kl, midkl);
            p1 = dataPara(il, midil, jl, midjl, midkr, kr); 
            p2 = dataPara(il, midil, midjr, jr, kl, midkl); 
            p3 = dataPara(il, midil, midjr, jr, midkr, kr);
        }
        #pragma omp task shared(p4, p5, p6, p7)
        {
            p4 = dataPara(midir, ir, jl, midjl, kl, midkl); 
            p5 = dataPara(midir, ir, jl, midjl, midkr, kr); 
            p6 = dataPara(midir, ir, midjr, jr, kl, midkl); 
            p7 = dataPara(midir, ir, midjr, jr, midkr, kr);
        }
        #pragma omp taskwait
        // Cpp = P0 + P1
        // Cpq = P2 + P3
        // Cqp = P4 + P5
        // Cqq = P6 + P7
        uint tt1 = midil - il + 1;
        uint tt2 = midjl - jl + 1;
        uint tt3 = midjr - jl;
        uint tt4 = midir - il;
        uint tt5 = jr - midjr + 1;
        #pragma omp parallel for
        for (uint i = 0; i < tt1; i++) {
            for (uint j = 0; j < tt2; j++) {
                tmp[i * jw + j] = p0[i * tt2 + j] + p1[i * tt2 + j];
            }
            for (uint j = tt3; j < jw; j++) {
                tmp[i * jw + j] = p2[i * tt5 + j - tt3] + p3[i * tt5 + j - tt3];
            }
        }
        #pragma omp parallel for
        for (uint i = tt4; i < iw; i++) {
            for (uint j = 0; j < tt2; j++) {
                tmp[i * jw + j] = p4[(i - tt4) * tt2 + j] + p5[(i - tt4) * tt2 + j];
            }
            for (uint j = tt3; j < jw; j++) {
                tmp[i * jw + j] = p6[(i - tt4) * tt5 + j - tt3] + p7[(i - tt4) * tt5 + j - tt3];
            }
        }
        free(p0); free(p1); free(p2); free(p3); free(p4); free(p5); free(p6); free(p7);
    }
    return tmp;
}

int main(int argc, char* argv[]) {
    uint N1 = atoll(argv[1]);
    uint N2 = atoll(argv[2]);
    uint N3 = atoll(argv[3]);

    // out = new double[N1 * N3];

    omp_set_num_threads(8);

    #pragma omp parallel shared(threads_num)
    {
        #pragma omp single
        {
            threads_num = omp_get_num_threads();
        }
    }
    is_small_use_parallel = (N1 * N3) < MAGIC_NUM_MID; 
    part = (is_small_use_parallel)?N1 * N3:N1 * N3 / MAGIC_NUM_PARTS;

    #ifdef Debug
    printf("Is small use parallel: %s, part: %u, magic_mid: %d, magic_parts: %d", 
            (is_small_use_parallel)?"yes":"no", part, MAGIC_NUM_MID, MAGIC_NUM_PARTS);
    #endif

    double *out = dataPara(0, N1 - 1, 0, N3 - 1, 0, N2 - 1);
    // #pragma omp parallel for num_threads(8) schedule(dynamic, 4096) proc_bind(close)
    // for (uint t = 0; t < N1*N3; ++t) {
    //     uint i = t / N3;
    //     uint j = t % N3;
    //     double tk = 0.0;
    //     for (uint k = 0; k < N2; ++k) {
    //         double a, b;
    //         matA(i, k, a);
    //         matB(k, j, b);
    //         tk = a * b + tk;
    //     }
    //     // cal out(i,j)
    //     out[i * N3 + j] = tk;
    // }

    // #pragma omp parallel
    // {
    //     #pragma omp single nowait
    //     {
    //         uint lw = N1 * N3;
    //         uint l = 0;
    //         while (lw > 0)
    //         {
    //             #pragma omp task firstprivate(N3, N2, l)
    //             {
    //                 for (uint t = l; t < l + 1024; ++t) {
    //                     uint i = t / N3;
    //                     uint j = t % N3;
    //                     double tk = 0;
    //                     #pragma omp parallel for num_threads(8) schedule(dynamic,2048) reduction(+ : tk) firstprivate(i, j)
    //                     for (uint k = 0; k < N2; ++k) {
    //                         double a, b;
    //                         matA(i, k, a);
    //                         matB(k, j, b);
    //                         tk = a * b + tk;
    //                     }
    //                     out[i * N3 + j] = tk;
    //                 }
    //             }
    //             // lw -= 1024;
    //             if (lw < 1024) { 
    //                 break; 
    //             } else {
    //                 lw = lw - 1024;
    //             }
    //             l += 1024;
    //         }
    //     }
    // }

    #pragma omp taskwait

    ofstream output;
    output.open("output.dat");

    for (uint t = 0; t < N1*N3; ++t) {
        uint i = t / N3;
        uint j = t % N3;
        output << setprecision(12) << out[i * N3 + j] << endl;
    }
    
    output.close();
    // delete []out;
    free(out);
}