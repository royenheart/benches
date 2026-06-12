#include <bench/competitive/problem.hpp>

#include <iostream>
#include <sstream>
#include <string>

int answer() {
    int n;
    std::cin >> n;
    std::string out;
    for (int i = n; i >= 0; i--) {
        int a;
        std::cin >> a;
        if (a != 0) {
            if (a > 0) {
                out.push_back('+');
            } else {
                out.push_back('-');
            }
            if (i != 0) {
                if (abs(a) != 1) {
                    out.append(std::to_string(abs(a)));
                }
                out.append("x");
                if (i != 1) {
                    out.push_back('^');
                    out.append(std::to_string(i));
                }
            } else {
                out.append(std::to_string(abs(a)));
            }
        }
    }
    if (out.length() > 0 && out[0] == '+') {
        out = out.substr(1);
    }
    std::cout << out;
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)

BENCH_IO_TEST("sample 1",
              R"(5 
100 -1 1 -3 0 10)",
              "100x^5-x^4+x^3-3x^2+10", 0, answer)

BENCH_IO_TEST("sample 2",
              R"(3 
-50 0 0 1 )",
              "-50x^3+1", 0, answer)

BENCH_IO_TEST("sample 3",
              R"(0 
1)",
              "1", 0, answer)

BENCH_IO_TEST("sample 4",
              R"(0 
0)",
              "", 0, answer)

BENCH_IO_TEST("sample 5",
              R"(1 
1 -10)",
              "x-10", 0, answer)

BENCH_PERF_TEST("sample 1", answer,
                R"(5 
100 -1 1 -3 0 10)",
                1)
