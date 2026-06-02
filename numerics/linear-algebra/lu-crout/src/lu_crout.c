/**
 * @file lu_crout.cpp
 * @author royenheart@outlook.com
 * @brief use crout algorithm to solve LU Decomposition
 * @version 0.1
 * @date 2023-12-09
 *
 * @copyright Copyright (c) 2023
 *
 */

/*
使用 Crout 算法
LU 分解变体，将方阵分解为下三角矩阵 L 和上三角矩阵 U 的乘积，U 的对角线元素均为
1

伪代码：

function Crout(A)
    Input: A - n x n matrix
    Output: L, U - LU decomposition of A

    n = number of rows/columns of A
    Initialize L as n x n zero matrix
    // 初始化 L 为 0 矩阵
    Initialize U as n x n identity matrix
    // 初始化 U 为单元矩阵

    for i = 1 to n
        for j = 1 to i
            L[i, j] = A[i, j] - sum(L[i, k] * U[k, j] for k = 1 to j - 1)
        end for
        for j = i + 1 to n
            U[i, j] = (A[i, j] - sum(L[i, k] * U[k, j] for k = 1 to i - 1)) /
L[i, i] end for end for

    return L, U
end function

*/

#include "lu_crout.h"
#include "mat_struct.h"
#include "stdio.h"
#include "stdlib.h"

void lu_crout(MAT A, MAT L, MAT U, size_t n) {
    for (size_t i = 0; i < n; i++) {
        size_t j, k;
        for (j = 0; j < i + 1; j++) {
            MAT_ELEM s = 0;
            for (k = 0; k < j; k++) {
                s += L[i * n + k] * U[k * n + j];
            }
            L[i * n + j] = A[i * n + j] - s;
        }
        for (j = i + 1; j < n; j++) {
            MAT_ELEM s = 0;
            for (k = 0; k < j; k++) {
                s += L[i * n + k] * U[k * n + j];
            }
            U[i * n + j] = (A[i * n + j] - s) / L[i * n + i];
        }
    }
}