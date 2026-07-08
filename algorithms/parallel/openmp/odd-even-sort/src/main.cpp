#include <omp.h>
#include <iostream>
#include <chrono>
#include <random>
#include <cstdlib>

// Query the L2 cache size in a portable way. sysconf(_SC_LEVEL2_CACHE_SIZE) is
// a Linux/glibc extension and <unistd.h> does not exist on MSVC, so use
// GetLogicalProcessorInformation there and fall back to 256 KiB if unknown.
#if defined(_WIN32)
#include <windows.h>
static long get_l2_cache_size() {
    DWORD len = 0;
    GetLogicalProcessorInformation(nullptr, &len);
    if (len == 0) {
        return 256 * 1024;
    }
    SYSTEM_LOGICAL_PROCESSOR_INFORMATION* buf =
        static_cast<SYSTEM_LOGICAL_PROCESSOR_INFORMATION*>(malloc(len));
    if (buf == nullptr || !GetLogicalProcessorInformation(buf, &len)) {
        free(buf);
        return 256 * 1024;
    }
    long size = 0;
    DWORD count = len / sizeof(SYSTEM_LOGICAL_PROCESSOR_INFORMATION);
    for (DWORD i = 0; i < count; i++) {
        if (buf[i].Relationship == RelationCache && buf[i].Cache.Level == 2) {
            size = static_cast<long>(buf[i].Cache.Size);
            break;
        }
    }
    free(buf);
    return size > 0 ? size : 256 * 1024;
}
#else
#include <unistd.h>
static long get_l2_cache_size() {
    long size = sysconf(_SC_LEVEL2_CACHE_SIZE);
    return size > 0 ? size : 256 * 1024;
}
#endif

#define SIZE 200000
#define LOOP 1

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

    // L2 Cache - 单个 CPU L2 缓存大小
    long l2 = get_l2_cache_size();
    long chunk = l2 / sizeof(int64_t) / 128;

    std::cout << "L2 Cache Size " << l2 << "Bytes" << std::endl;
    std::cout << "Chunk Size " << chunk << std::endl;

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int64_t> dis(-SIZE*2, SIZE*2);

    int phase, i;
    int64_t tmp;

    for (int u = 0; u < LOOP; u++) {
        // initialize the vectors
        for (int i = 0; i < SIZE; i++) {
            numbers[i] = dis(gen);
        }
        auto start = std::chrono::high_resolution_clock::now();
        #pragma omp parallel num_threads(thread_count) shared(numbers, chunk) private(phase, i, tmp)
        {
            for (phase = 0; phase < SIZE; phase++) {
                if (phase % 2 == 0) {
                    #pragma omp for schedule(static, chunk)
                    for (i = 1; i < SIZE; i += 2) {
                        if (numbers[i - 1] > numbers[i]) {
                            tmp = numbers[i - 1];
                            numbers[i - 1] = numbers[i];
                            numbers[i] = tmp;
                        }
                    }
                } else {
                    #pragma omp for schedule(static, chunk)
                    for (i = 1; i < SIZE - 1; i += 2) {
                        if (numbers[i] > numbers[i + 1]) {
                            tmp = numbers[i + 1];
                            numbers[i + 1] = numbers[i];
                            numbers[i] = tmp;
                        }
                    }
                }
            }
        }
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        std::cout << "单次耗时: " << duration.count() / 1000000.0 << " 秒" << std::endl;
        // 打印前 50 个元素
        for (int i = 0; i < 50; i++) {
            std::cout << numbers[i] << " ";
        }
        std::cout << std::endl;
        // 验证
        auto tmp = numbers[0];
        int i;
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