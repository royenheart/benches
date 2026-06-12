#include <bench/competitive/problem.hpp>

#include <iostream>

struct dot {
    int a;
    int b;
    int g;
    int k;
};

dot maps[10000];

int answer() {
    int n;
    int x, y;
    int i = 0;
    std::cin >> n;
    for (; i < n; i++) {
        dot d;
        // 左下角，X 轴方向长度，Y 轴方向长度
        std::cin >> d.a >> d.b >> d.g >> d.k;
        maps[i] = d;
    }
    std::cin >> x >> y;
    for (i = n - 1; i >= 0; i--) {
        auto d = maps[i];
        auto xl = x - d.a;
        auto yl = y - d.b;
        if (d.g == 0 || d.k == 0)
            continue;
        if (xl >= 0 && xl <= d.g && yl >= 0 && yl <= d.k) {
            std::cout << i + 1;
            return 0;
        }
    }
    std::cout << -1;
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)

BENCH_IO_TEST("sample 1",
              R"(3
1 0 2 3
0 2 3 3
2 1 3 3
2 2)",
              "3", 0, answer)

BENCH_IO_TEST("sample 2",
              R"(3
1 0 2 3
0 2 3 3
2 1 3 3
4 5)",
              "-1", 0, answer)

BENCH_PERF_TEST("sample 1", answer,
                R"(3
1 0 2 3
0 2 3 3
2 1 3 3
2 2)",
                1)
