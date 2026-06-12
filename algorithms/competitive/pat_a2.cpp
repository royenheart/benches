#include <bench/competitive/problem.hpp>

#include <iostream>
#include <queue>

int answer() {
    int l;
    std::cin >> l;

    int s1s = 0;
    int s2s = 0;
    bool first_output = true;
    std::queue<int> q;

    auto emit_line_prefix = [&first_output]() {
        if (!first_output) {
            std::cout << "\n";
        }
        first_output = false;
    };

    for (int i = 0; i < l; i++) {
        char o;
        std::cin >> o;
        if (o == 'O') {
            if (s2s == 0) {
                if (s1s == 0) {
                    emit_line_prefix();
                    std::cout << "ERROR";
                } else {
                    emit_line_prefix();
                    std::cout << q.front() << " " << s1s * 2 + 1;
                    s2s = s1s - 1;
                    s1s = 0;
                    q.pop();
                }
            } else {
                emit_line_prefix();
                std::cout << q.front() << " " << 1;
                s2s--;
                q.pop();
            }
        } else {
            unsigned int e;
            std::cin >> e;
            q.push(e);
            s1s++;
        }
    }

    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)

BENCH_IO_TEST("sample 1",
              R"(10
I 20
I 32
O
I 11
O
O
O
I 100
I 66
O)",
              R"(20 5
32 1
11 3
ERROR
100 5)",
              0, answer)

BENCH_PERF_TEST("sample 1", answer,
                R"(10
I 20
I 32
O
I 11
O
O
O
I 100
I 66
O)",
                1)
