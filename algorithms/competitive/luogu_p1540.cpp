#include <bench/competitive/problem.hpp>

#include <iostream>
#include <queue>

bool set[1001] = {false};
std::queue<int> mem;

int answer() {
    int m, n;
    int count = 0;
    std::cin >> m >> n;
    for (int i = 0; i < n; i++) {
        int w;
        std::cin >> w;
        if (set[w] == false) {
            count++;
            set[w] = true;
            mem.push(w);
            if (static_cast<int>(mem.size()) > m) {
                set[mem.front()] = false;
                mem.pop();
            }
        }
    }
    std::cout << count;
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)

BENCH_IO_TEST("sample 1",
              R"(3 7
1 2 1 5 4 4 1)",
              "5", 0, answer)

BENCH_PERF_TEST("sample 1", answer,
                R"(3 7
1 2 1 5 4 4 1)",
                1)
