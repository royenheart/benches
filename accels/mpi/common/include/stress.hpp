#pragma once

#include <cblas.h>
#include <stdlib.h>

/**
 * @brief 生成随机矩阵
 * 
 * @param m 矩阵宽
 * @param n 矩阵高
 * @return double* 矩阵
 */
double* gen_random_matrix(int m, int n);

/**
 * @brief 调用 openblas 进行矩阵分解计算
 * 
 * @return double* 结果矩阵
 */
double* matrix_cal(int m, int n, int k);

/**
 * @brief 打印矩阵
 * 
 * @param c 矩阵
 * @param m 矩阵宽
 * @param n 矩阵高
 */
void print_matrix(double *c, int m, int n);

double* matrix_cal(int m, int n, int k) {
    double *A = gen_random_matrix(m, k), *B = gen_random_matrix(k, n), *C = (double*)malloc(m * n * sizeof(double));

    cblas_dgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans, m, n, k, 1.0, A, k, B, n, 0.0, C, n);

    free(A); 
    free(B);

    return C;
}

void print_matrix(double *c, int m, int n) {
    for (int i = 0; i < m; i++) {
        std::cout << "[";
        for (int j = 0; j < n; j++) {
            std::cout << c[i * n + j] << ",";
        }
        std::cout << "]" << std::endl;
    }
}

double* gen_random_matrix(int m, int n) {
    double *r = NULL; 
    for (int i = 0; i < m * n; i++) {
        r[i] = (double) rand() / (double) RAND_MAX;
    }
    return r;
}

