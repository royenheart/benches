#include <iostream>
#include <cstdio>
#include <omp.h>

int main(int argc, char* argv[]) {
    #pragma omp parallel
    {
        int id = omp_get_thread_num();
        int processor = omp_get_place_num();
        printf("my id is %d, place in %d\n", id, processor);
        // std::cout << "my id is " << id << ", place in " << processor << std::endl;
    }
}