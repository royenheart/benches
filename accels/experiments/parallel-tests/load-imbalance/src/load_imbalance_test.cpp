#include <iostream>
#include <vector>
#include <cstdlib>
#include <cmath>
#include <omp.h>
#include <ctime>
#include <iomanip>
#include <random>
#include <string>
#include <cstring>

#ifdef INTEL
#include <mkl.h>
#define math_malloc mkl_malloc
#define math_free mkl_free
#elif defined(ARM)
#include <kblas.h>
#include <memory>
#define math_malloc kml_malloc
#define math_free kml_free

void* kml_malloc(size_t size, int align) {
    // 直接 malloc 没有进行内存对齐
    // return malloc(size);
    // 使用 C++17 后的 memory 提供的 API 对齐
    return std::aligned_alloc(align, size);
}

void kml_free(void* ptr) {
    // free(ptr);
    std::free(ptr);
}
#endif

// 全局变量，用于存储预分配的矩阵
double **global_A = nullptr;
double **global_B = nullptr;
double **global_C = nullptr;
int global_max_matrix_size = 0;

// 初始化全局矩阵
void initialize_matrices(int num_threads, int max_workload) {
    // 计算最大矩阵尺寸
    global_max_matrix_size = static_cast<int>(std::sqrt(max_workload / 10)) + 50;
    if (global_max_matrix_size < 100) global_max_matrix_size = 100;
    
    std::cout << "- 预分配矩阵大小: " << global_max_matrix_size << "x" << global_max_matrix_size << std::endl;
    
    // 为每个线程分配矩阵
    global_A = new double*[num_threads];
    global_B = new double*[num_threads];
    global_C = new double*[num_threads];
    
    // 使用OpenMP并行初始化
    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        
        // 为每个线程分配矩阵内存
        global_A[tid] = (double *)math_malloc(global_max_matrix_size * global_max_matrix_size * sizeof(double), 64);
        global_B[tid] = (double *)math_malloc(global_max_matrix_size * global_max_matrix_size * sizeof(double), 64);
        global_C[tid] = (double *)math_malloc(global_max_matrix_size * global_max_matrix_size * sizeof(double), 64);
        
        // 初始化矩阵
        std::mt19937 gen(tid + 1);  // 线程专用随机数生成器
        std::uniform_real_distribution<> dis(0.0, 1.0);
        
        for (int i = 0; i < global_max_matrix_size * global_max_matrix_size; i++) {
            global_A[tid][i] = dis(gen);
            global_B[tid][i] = dis(gen);
            global_C[tid][i] = 0.0;
        }
    }
}

// 释放全局矩阵内存
void cleanup_matrices(int num_threads) {
    if (global_A != nullptr) {
        for (int i = 0; i < num_threads; i++) {
            if (global_A[i]) math_free(global_A[i]);
            if (global_B[i]) math_free(global_B[i]);
            if (global_C[i]) math_free(global_C[i]);
        }
        delete[] global_A;
        delete[] global_B;
        delete[] global_C;
        
        global_A = nullptr;
        global_B = nullptr;
        global_C = nullptr;
    }
}

// 修改后的计算负载函数，使用预分配矩阵
void compute_workload(long iterations) {
    int tid = omp_get_thread_num();
    
    // 根据迭代次数确定子矩阵大小
    int sub_matrix_size = static_cast<int>(std::sqrt(iterations / 10));
    if (sub_matrix_size < 10) sub_matrix_size = 10;
    if (sub_matrix_size > global_max_matrix_size) sub_matrix_size = global_max_matrix_size;
    
    // 随机选择子矩阵起始点
    int max_start = global_max_matrix_size - sub_matrix_size;
    int start_row = rand() % (max_start > 0 ? max_start : 1);
    int start_col = rand() % (max_start > 0 ? max_start : 1);
    
    // 矩阵乘法参数
    char transa = 'n';
    char transb = 'n';
    double alpha = 1.0;
    double beta = 0.0;
    
    // 为子矩阵准备指针
    double *A_sub = global_A[tid] + start_row * global_max_matrix_size + start_col;
    double *B_sub = global_B[tid] + start_row * global_max_matrix_size + start_col;
    double *C_sub = global_C[tid] + start_row * global_max_matrix_size + start_col;
    
    // 执行子矩阵乘法
    cblas_dgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans, 
                sub_matrix_size, sub_matrix_size, sub_matrix_size, 
                alpha, A_sub, global_max_matrix_size, 
                B_sub, global_max_matrix_size, 
                beta, C_sub, global_max_matrix_size);
}

int main(int argc, char *argv[]) {
    // 默认参数
    int num_threads = omp_get_max_threads();
    int num_tasks = 100;
    double imbalance_factor = 5.0;  // 负载不均衡因子
    int base_workload = 1000000;    // 基础工作负载
    int repeat_count = 5;           // 重复执行次数

    // 解析命令行参数
    if (argc > 1) num_threads = std::atoi(argv[1]);
    if (argc > 2) num_tasks = std::atoi(argv[2]);
    if (argc > 3) imbalance_factor = std::atof(argv[3]);
    if (argc > 4) base_workload = std::atoi(argv[4]);
    if (argc > 5) repeat_count = std::atoi(argv[5]);

    // 设置线程数
    omp_set_num_threads(num_threads);
    
    initialize_matrices(num_threads, base_workload * imbalance_factor);

    // 初始化随机数生成器
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(1.0, imbalance_factor);
    
    std::cout << "测试配置:" << std::endl;
    std::cout << "- 线程数: " << num_threads << std::endl;
    std::cout << "- 任务数: " << num_tasks << std::endl;
    std::cout << "- 不均衡因子: " << std::fixed << std::setprecision(2) << imbalance_factor << std::endl;
    std::cout << "- 基础负载: " << base_workload << std::endl;
    std::cout << "- 重复次数: " << repeat_count << std::endl;
    
    // 获取当前的 KMP_BLOCKTIME 值
    char* blocktime_env = std::getenv("KMP_BLOCKTIME");
    std::cout << "- KMP_BLOCKTIME: " << (blocktime_env ? blocktime_env : "未设置") << std::endl;
    
    double total_time = 0.0;
    double min_time = -1.0;
    double max_time = 0.0;
    
    for (int r = 0; r < repeat_count; r++) {
        double start_time = omp_get_wtime();
        
        // 创建任务负载数组
        std::vector<long> task_loads(num_tasks);
        long total_workload = 0;
        for (int i = 0; i < num_tasks; i++) {
            // 使用不均衡因子生成不同的任务负载
            double random_factor = dis(gen);
            task_loads[i] = static_cast<long>(base_workload * random_factor);
            total_workload += task_loads[i];
        }
        
        // 收集每个线程的工作时间和分配到的负载
        std::vector<double> thread_times(num_threads, 0.0);
        std::vector<long> thread_workloads(num_threads, 0);
        std::vector<int> task_counts(num_threads, 0);
        
        #pragma omp parallel
        {
            int tid = omp_get_thread_num();
            double thread_start = omp_get_wtime();
            
            // 取消隐式同步，避免时间计算的错误
            #pragma omp for schedule(dynamic, 1) nowait
            for (int i = 0; i < num_tasks; i++) {
                #pragma omp critical
                {
                    thread_workloads[tid] += task_loads[i];
                    task_counts[tid]++;
                }
                compute_workload(task_loads[i]);
            }
            
            #pragma omp critical
            {
                thread_times[tid] = omp_get_wtime() - thread_start;
            }
        }
        
        double end_time = omp_get_wtime();
        double elapsed = end_time - start_time;
        
        // 计算统计信息
        double avg_thread_time = 0.0;
        double min_thread_time = thread_times[0];
        double max_thread_time = thread_times[0];
        
        long min_workload = thread_workloads[0];
        long max_workload = thread_workloads[0];
        long total_accounted_workload = 0;
        int min_task_count = task_counts[0];
        int max_task_count = task_counts[0];
        
        for (int i = 0; i < num_threads; i++) {
            avg_thread_time += thread_times[i];
            if (thread_times[i] < min_thread_time) min_thread_time = thread_times[i];
            if (thread_times[i] > max_thread_time) max_thread_time = thread_times[i];
            
            total_accounted_workload += thread_workloads[i];
            if (thread_workloads[i] < min_workload) min_workload = thread_workloads[i];
            if (thread_workloads[i] > max_workload) max_workload = thread_workloads[i];
            
            if (task_counts[i] < min_task_count) min_task_count = task_counts[i];
            if (task_counts[i] > max_task_count) max_task_count = task_counts[i];
        }
        avg_thread_time /= num_threads;
        
        // 计算标准差
        double std_dev_time = 0.0;
        double std_dev_workload = 0.0;
        double avg_workload = static_cast<double>(total_accounted_workload) / num_threads;
        
        for (int i = 0; i < num_threads; i++) {
            std_dev_time += (thread_times[i] - avg_thread_time) * (thread_times[i] - avg_thread_time);
            std_dev_workload += (thread_workloads[i] - avg_workload) * (thread_workloads[i] - avg_workload);
        }
        std_dev_time = std::sqrt(std_dev_time / num_threads);
        std_dev_workload = std::sqrt(std_dev_workload / num_threads);
        
        // 计算负载不均衡指标
        double time_imbalance = max_thread_time / avg_thread_time;
        double workload_imbalance = static_cast<double>(max_workload) / avg_workload;
        
        // 输出统计结果
        std::cout << "\n运行 " << r+1 << "/" << repeat_count << ":" << std::endl;
        std::cout << "- 总执行时间: " << std::fixed << std::setprecision(4) << elapsed << " 秒" << std::endl;
        std::cout << "- 平均线程时间: " << avg_thread_time << " 秒" << std::endl;
        std::cout << "- 最短线程时间: " << min_thread_time << " 秒" << std::endl;
        std::cout << "- 最长线程时间: " << max_thread_time << " 秒" << std::endl;
        std::cout << "- 线程时间标准差: " << std_dev_time << std::endl;
        std::cout << "- 时间不均衡指标: " << time_imbalance << std::endl;
        
        std::cout << "\n- 任务总负载: " << total_workload << " 单位" << std::endl;
        std::cout << "- 平均线程负载: " << static_cast<long>(avg_workload) << " 单位" << std::endl;
        std::cout << "- 最小线程负载: " << min_workload << " 单位" << std::endl;
        std::cout << "- 最大线程负载: " << max_workload << " 单位" << std::endl;
        std::cout << "- 线程负载标准差: " << static_cast<long>(std_dev_workload) << " 单位" << std::endl;
        std::cout << "- 负载不均衡指标: " << workload_imbalance << std::endl;
        std::cout << "- 最少任务数: " << min_task_count << " 个" << std::endl;
        std::cout << "- 最多任务数: " << max_task_count << " 个" << std::endl;
        
        // 输出详细线程信息
        std::cout << "\n- 线程详细信息:" << std::endl;
        std::cout << "  " << std::setw(8) << "线程ID" << std::setw(15) << "执行时间(秒)" 
                  << std::setw(15) << "负载(单位)" << std::setw(10) << "任务数" 
                  << "  " << "负载可视化" << std::endl;
        
        for (int i = 0; i < num_threads; i++) {
            std::cout << "  " << std::setw(8) << i 
                      << std::setw(15) << std::fixed << std::setprecision(4) << thread_times[i] 
                      << std::setw(15) << thread_workloads[i] 
                      << std::setw(10) << task_counts[i] << "  ";
            
            // 简单的可视化
            int bars = static_cast<int>(thread_workloads[i] / static_cast<double>(max_workload) * 50);
            for (int j = 0; j < bars; j++) std::cout << " ";
            std::cout << std::endl;
        }
        
        // 更新总统计
        total_time += elapsed;
        if (min_time < 0 || elapsed < min_time) min_time = elapsed;
        if (elapsed > max_time) max_time = elapsed;
    }
    
    // 输出总结果
    std::cout << "\n总体结果 (" << repeat_count << " 次运行):" << std::endl;
    std::cout << "- 平均执行时间: " << std::fixed << std::setprecision(4) << total_time / repeat_count << " 秒" << std::endl;
    std::cout << "- 最快执行时间: " << min_time << " 秒" << std::endl;
    std::cout << "- 最慢执行时间: " << max_time << " 秒" << std::endl;
    
    cleanup_matrices(num_threads);

    return 0;
}