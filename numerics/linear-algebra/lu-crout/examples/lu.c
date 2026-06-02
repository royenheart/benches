#include "lu_crout.h"
#include "stdio.h"
#include "stdlib.h"
#include "string.h"

int main(int argc, char* argv[]) {
    size_t n = 3;
    double A[] = {2, 3, 1, 4, 7, 1, 6, 7, 3};
    MAT L = (MAT)malloc(n * n * sizeof(MAT_ELEM));
    MAT U = (MAT)malloc(n * n * sizeof(MAT_ELEM));
    memset(L, 0, 9);
    memset(U, 0, 9);
    for (int i = 0; i < n; i++) {
        U[i * n + i] = 1;
    }
    lu_crout(A, L, U, n);
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            printf("%lf ", L[i * n + j]);
        }
        printf("\n");
    }
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            printf("%lf ", U[i * n + j]);
        }
        printf("\n");
    }
}