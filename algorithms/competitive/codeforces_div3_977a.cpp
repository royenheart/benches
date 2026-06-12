#include <bench/competitive/problem.hpp>

#include <iostream>

int answer() {
    size_t n, k;
    std::cin >> n >> k;
    for (size_t i = 0; i < k; i++) {
        int l = n % 10;
        if (l == 0) {
            n /= 10;
        } else {
            n--;
        }
    }
    std::cout << n;
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)

BENCH_IO_TEST("sample 1", R"(512 4)", "50", 0, answer)
BENCH_IO_TEST("sample 2", R"(1000000000 9)", "1", 0, answer)
BENCH_PERF_TEST("sample 1", answer, R"(512 4)", 1)
