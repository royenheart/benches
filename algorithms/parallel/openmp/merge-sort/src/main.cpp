#include <omp.h>
#include <iostream>
#include <chrono>
#include <random>
#include <unistd.h>

#define SIZE 1000000
#define LOOP 10

/**
 * @brief 合并序列
 * 
 * @param l1 合并的序列的起始位置下标，也是第一个被合并序列的起始位置
 * @param r1 第二个被合并序列的起始位置下标
 * @param r2 第二个被合并序列的最后位置下标 + 1
 * @param data 原序列
 * @param temp 临时序列，用于存储合并后的结果，最后重新更新至原序列
 */
void merge(int l1, int r1, int r2, int64_t* data, int64_t* temp) {
    int top = l1, p = l1, q = r1;
    while (p < r1 || q < r2) {
        if (q >= r2 || (p < r1 && data[p] <= data[q])) {
            temp[top++] = data[p++];
        } else {
            temp[top++] = data[q++];
        }
    }
    for (top = l1; top < r2; top++) {
        data[top] = temp[top];
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "输入一个参数表示线程数" << std::endl;
        return EXIT_FAILURE;
    }

    int thread_count = std::atoi(argv[1]);
    if (thread_count < 2) {
        std::cout << "Must be at least 2 threads specified" << std::endl;
        return EXIT_FAILURE;
    }

    int64_t *numbers = (int64_t*)malloc(SIZE * sizeof(int64_t));
    int64_t *temp = (int64_t*)malloc(SIZE * sizeof(int64_t));

    // L2 Cache - 单个 CPU L2 缓存大小
    long l2 = sysconf(_SC_LEVEL2_CACHE_SIZE);
    long l1d = sysconf(_SC_LEVEL1_DCACHE_SIZE);
    long l1i = sysconf(_SC_LEVEL1_ICACHE_SIZE);
    long l3 = sysconf(_SC_LEVEL3_CACHE_SIZE);
    long chunk = l2 / sizeof(int64_t) / 128;

    std::cout << "L2 Cache Size " << l2 << "Bytes" << std::endl;
    std::cout << "Chunk Size " << chunk << std::endl;

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int64_t> dis(INT64_MIN, INT64_MAX);

    for (int u = 0; u < LOOP; u++) {
        // initialize the vectors
        int i, j;
        int64_t t;
        for (i = 0; i < SIZE; i++) {
            numbers[i] = dis(gen);
        }
        auto start = std::chrono::high_resolution_clock::now();

        // 各个线程负责一段进行运算，每次针对只有两个元素的序列进行排序
        // 每段计算规模类似，因此使用默认调度即可（负载可以均衡）
        #pragma omp parallel for num_threads(thread_count) private(i, t) shared(numbers)
        for (i = 0; i < SIZE / 2; i++) {
            if (numbers[i * 2] > numbers[i * 2 + 1]) {
                t = numbers[i * 2];
                numbers[i * 2] = numbers[i * 2 + 1];
                numbers[i * 2 + 1] = t;
            }
        }
        for (i = 2; i < SIZE; i *= 2) { // 自底向上合并各段，从长度2开始
            #pragma omp parallel for num_threads(thread_count) private(j) shared(i)
            for (j = 0; j < SIZE - i; j += i * 2) {
                merge(j, j + i, (j + i * 2 < SIZE)?j + i * 2:SIZE, numbers, temp);
            }
        }

        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        std::cout << "单次耗时: " << duration.count() / 1000000.0 << " 秒" << std::endl;
        // 打印前 50 个元素
        for (i = 0; i < 50; i++) {
            std::cout << numbers[i] << " ";
        }
        std::cout << std::endl;
        // 验证
        auto tmp = numbers[0];
        for (i = 1; i < SIZE; i++) {
            if (numbers[i] < tmp) {
                std::cout << "排序失败" << std::endl;
                std::cout << i-1 << ":" << tmp << " " << i << ":" << numbers[i] << std::endl;
                break;
            } else {
                tmp = numbers[i];
            }
        }
        if (i == SIZE) {
            std::cout << "排序成功" << std::endl;
        }
    }
}