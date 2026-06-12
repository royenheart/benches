#include <bench/competitive/problem.hpp>

#include <algorithm>
#include <iostream>
#include <vector>

std::vector<int> seq;

int answer() {
    int n, k;
    std::cin >> n >> k;
    seq.clear();
    for (int i = 0; i < n; i++) {
        int tmp;
        std::cin >> tmp;
        seq.push_back(tmp);
    }
    std::sort(seq.begin(), seq.end());

    if (k >= n) {
        std::cout << seq[n - 1];
        return 0;
    }

    int l = (k == 0) ? 1 : seq[k - 1];
    int r = seq[k];

    if (l < r) {
        std::cout << l;
    } else {
        std::cout << -1;
    }

    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)

BENCH_IO_TEST("sample 1",
              R"(7 4
3 7 5 1 10 3 20)",
              "5", 0, answer)

BENCH_IO_TEST("sample 2",
              R"(7 2
3 7 5 1 10 3 20)",
              "-1", 0, answer)

BENCH_IO_TEST("sample 3",
              R"(1 0
1)",
              "-1", 0, answer)

BENCH_IO_TEST("sample 4",
              R"(1 0
2)",
              "1", 0, answer)

BENCH_IO_TEST("sample 5",
              R"(2 3
1 2)",
              "2", 0, answer)

BENCH_PERF_TEST("sample 1", answer,
                R"(7 4
3 7 5 1 10 3 20)",
                1)
