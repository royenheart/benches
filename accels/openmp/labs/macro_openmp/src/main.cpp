#include <omp.h>
#include <iostream>

int main() {
    #ifdef _OPENMP
    std::cout << "_OPENMP: " << _OPENMP << std::endl;
    #else
    std::cout << "_OPENMP not defined" << std::endl;
    #endif
}