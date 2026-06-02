#include <omp.h>
#include <cstdio>
#include <immintrin.h>

#define STEPS 100000000
#define PI 3.1415926535897
#define MAX_NUM_THREADS 100
#define NUM_THREADS 4

int main(int argc, char* argv[]) {
    #ifdef seq
    {
        int i;
        double x, pi, sum = 0.0;
        double step = 1.0 / (double)STEPS;
        double t_start = omp_get_wtime();
        for (i = 0; i < STEPS; i++) {
            x = (i + 0.5) * step;
            sum = sum + 4.0 / (1.0 + x * x);
        }
        double t_end = omp_get_wtime();
        pi = step * sum;
        printf("Calculate Time: %fs\n", (t_end - t_start));
        printf("The result is %.26f\n", pi);
        printf("The mistake is: %.26f\n", abs(pi - PI));
    }
    #endif
    // 使用 SPMD 算法策略
    // 类似 CUDA 核函数，线程组的概念，idx * ids + id....
    // 线程号 + 线程（循环分布）
    #ifdef slp_omp
    {
        double pi, sum = 0.0;
        double t_start = omp_get_wtime();
        double step = 1.0 / (double)STEPS;
        double arr_sum[MAX_NUM_THREADS] = {0};
        #pragma omp parallel
        {
            int i;
            double x = 0.0;
            int id = omp_get_thread_num();
            int ids = omp_get_num_threads();
            double t_sum = 0.0;
            for (i = id; i < STEPS; i += ids) {
                x = (i + 0.5) * step;
                t_sum += 4.0 / (1.0 + x * x);
            }
            arr_sum[id] = t_sum;
        }
        double t_end = omp_get_wtime();
        for (int i = 0; i < MAX_NUM_THREADS; i++) {
            sum += arr_sum[i];
        }
        pi = step * sum;
        printf("Calculate Time: %fs\n", (t_end - t_start));
        printf("The result is %.26f\n", pi);
        printf("The mistake is: %.26f\n", abs(pi - PI));
    }
    #endif
    // 不好的 SPMD 算法策略写法
    // 此写法拓展性并不算太好，所有线程都访问 arr_sum ，会导致“虚假共享”（False Sharing）
    // 出现在数组元素缓存在同一 Cache Line 时，由于线程既读又写，写过程会导致缓存（Cache）需要进行更新防止脏数据（避免数据竞争）
    // 此时很容易导致缓存的 Slosh back and forth 的一种来回摆动的状态
    #ifdef slp_omp_v1
    {
        double pi, sum = 0.0;
        double t_start = omp_get_wtime();
        double step = 1.0 / (double)STEPS;
        double arr_sum[MAX_NUM_THREADS] = {0};
        #pragma omp parallel
        {
            int i;
            double x = 0.0;
            int id = omp_get_thread_num();
            int ids = omp_get_num_threads();
            double t_sum = 0.0;
            for (i = id; i < STEPS; i += ids) {
                x = (i + 0.5) * step;
                arr_sum[id] += 4.0 / (1.0 + x * x);
            }
        }
        double t_end = omp_get_wtime();
        for (int i = 0; i < MAX_NUM_THREADS; i++) {
            sum += arr_sum[i];
        }
        pi = step * sum;
        printf("Calculate Time: %fs\n", (t_end - t_start));
        printf("The result is %.26f\n", pi);
        printf("The mistake is: %.26f\n", abs(pi - PI));
    }
    #endif
    // 修正后的 SPMD 算法策略，（在 v1 基础上，解决方法较为丑陋）
    // 添加一维，使得每次载入一个 L1D Cache Line 大小的书记，避免多个线程同时访问同一个 Cache Line
    // getconf 查询计算机硬件信息
    // getconf -a | grep CACHE
    #ifdef slp_omp_v2
    {
        double pi, sum = 0.0;
        double t_start = omp_get_wtime();
        double step = 1.0 / (double)STEPS;
        double arr_sum[MAX_NUM_THREADS][8] = {0};
        #pragma omp parallel
        {
            int i;
            double x = 0.0;
            int id = omp_get_thread_num();
            int ids = omp_get_num_threads();
            for (i = id; i < STEPS; i += ids) {
                x = (i + 0.5) * step;
                arr_sum[id][0] += 4.0 / (1.0 + x * x);
            }
        }
        double t_end = omp_get_wtime();
        for (int i = 0; i < MAX_NUM_THREADS; i++) {
            sum += arr_sum[i][0];
        }
        pi = step * sum;
        printf("Calculate Time: %fs\n", (t_end - t_start));
        printf("The result is %.26f\n", pi);
        printf("The mistake is: %.26f\n", abs(pi - PI));
    }
    #endif
    #ifdef slp_omp_synchronization
    {
        double pi, sum = 0.0;
        double t_start = omp_get_wtime();
        double step = 1.0 / (double)STEPS;
        #pragma omp parallel
        {
            int i;
            double x = 0.0;
            int id = omp_get_thread_num();
            int ids = omp_get_num_threads();
            double t_sum = 0.0;
            for (i = id; i < STEPS; i += ids) {
                x = (i + 0.5) * step;
                t_sum += 4.0 / (1.0 + x * x);
            }
            #pragma omp atomic 
            sum += t_sum;
        }
        double t_end = omp_get_wtime();
        pi = step * sum;
        printf("Calculate Time: %fs\n", (t_end - t_start));
        printf("The result is %.26f\n", pi);
        printf("The mistake is: %.26f\n", abs(pi - PI));
    }
    #endif
    #ifdef worksharing_for
    {
        double pi, sum = 0.0;
        double t_start = omp_get_wtime();
        double step = 1.0 / (double)STEPS;
        double x = 0.0;
        double t_sum = 0.0;
        #pragma omp parallel firstprivate(x, t_sum)
        {
            #pragma omp for
            {
                for (int i = 0; i < STEPS; i++) {
                    x = (i + 0.5) * step;
                    t_sum += 4.0 / (1.0 + x * x);
                }
            }
            #pragma omp atomic
            sum += t_sum;
        }
        double t_end = omp_get_wtime();
        pi = step * sum;
        printf("Calculate Time: %fs\n", (t_end - t_start));
        printf("The result is %.26f\n", pi);
        printf("The mistake is: %.26f\n", abs(pi - PI));
    }
    #endif
    #ifdef reduction_test
    {
        double pi;
        double t_sum = 0.0;
        double step = 1.0 / (double)STEPS;
        double x = 0.0;
        double t_start = omp_get_wtime();
        #pragma omp parallel for reduction(+ : t_sum) firstprivate(x)
        {
            for (int i = 0; i < STEPS; i++) {
                x = (i + 0.5) * step;
                t_sum += 4.0 / (1.0 + x * x);
            }
        }
        double t_end = omp_get_wtime();
        pi = step * t_sum;
        printf("Calculate Time: %fs\n", (t_end - t_start));
        printf("The result is %.26f\n", pi);
        printf("The mistake is: %.26f\n", abs(pi - PI));
    }
    #endif
    #ifdef reduction_plus_simd
    {
        double pi;
        double t_sum = 0.0;
        double step = 1.0 / (double)STEPS;
        double x = 0.0;
        double t_start = omp_get_wtime();
        #pragma omp parallel for simd reduction(+ : t_sum) firstprivate(x)
        {
            for (int i = 0; i < STEPS; i++) {
                x = (i + 0.5) * step;
                t_sum += 4.0 / (1.0 + x * x);
            }
        }
        double t_end = omp_get_wtime();
        pi = step * t_sum;
        printf("Calculate Time: %fs\n", (t_end - t_start));
        printf("The result is %.26f\n", pi);
        printf("The mistake is: %.26f\n", abs(pi - PI));
    }
    #endif
}