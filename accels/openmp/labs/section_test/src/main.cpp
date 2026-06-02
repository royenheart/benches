#include <cstdio>
#include <iostream>
#include <omp.h>

int main(int argc, char* argv[]) {
    int i = 0;
    int num = 0;
    #pragma omp parallel
    {
        #pragma omp master
        {
            printf("master, insert a name!\n");
            std::cin >> num;
        }
        #pragma omp sections
        {
            #pragma omp section 
            {
                int id = omp_get_thread_num();
                printf("sec1 %d, i: %d\n", id, i);
            }
            #pragma omp section 
            {
                int id = omp_get_thread_num();
                printf("sec2 %d, i: %d\n", id, i);
            }
            #pragma omp section 
            {
                int id = omp_get_thread_num();
                printf("sec3 %d, i: %d\n", id, i);
            }
            #pragma omp section 
            {
                int id = omp_get_thread_num();
                printf("sec4 %d, i: %d\n", id, i);
            }
        }
    }
}