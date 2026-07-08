#include <iostream>
#include <cstdio>
#include <omp.h>

int main(int argc, char* argv[]) {
    #pragma omp parallel
    {
        int id = omp_get_thread_num();
        // omp_get_place_num() is an OpenMP 4.0+ routine. MSVC /openmp only
        // implements OpenMP 2.0, so guard it and fall back to -1 there.
#if defined(_OPENMP) && _OPENMP >= 201307
        int processor = omp_get_place_num();
#else
        int processor = -1;
#endif
        printf("my id is %d, place in %d\n", id, processor);
        // std::cout << "my id is " << id << ", place in " << processor << std::endl;
    }
}