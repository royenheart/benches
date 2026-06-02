#include <omp.h>
#include <cstdio>

// 主从模式测试

int main(int argc, char* argv[]) {
    int data, flag = 0;
    #pragma omp parallel
    {
        #pragma omp master
        {
            #pragma omp flush(flag, data)
            while (flag < 1)
            {
                #pragma omp flush(flag, data)
            }
            printf("flag=%d data=%d\n", flag, data);
            #pragma omp flush(flag, data)
            printf("flag=%d data=%d\n", flag, data);
        }
        data = 42;
        #pragma omp flush(flag, data)
        flag = 1;
        #pragma omp flush(flag)
    }
}