#include <bench/competitive/problem.hpp>

#include <algorithm>
#include <iostream>
#include <vector>

using Div3977Value = unsigned long long;

inline int factor3_count(Div3977Value value) {
    int count = 0;
    while (value % 3 == 0) {
        value /= 3;
        count++;
    }
    return count;
}

int answer() {
    int n;
    std::cin >> n;

    std::vector<Div3977Value> values(n);
    for (auto& value : values) {
        std::cin >> value;
    }

    std::sort(values.begin(), values.end(),
              [](Div3977Value left, Div3977Value right) {
                  const int left_factor3 = factor3_count(left);
                  const int right_factor3 = factor3_count(right);
                  if (left_factor3 != right_factor3) {
                      return left_factor3 > right_factor3;
                  }
                  return left < right;
              });

    for (auto value : values) {
        std::cout << value << " ";
    }

    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)

BENCH_IO_TEST("sample 1",
              R"(6
4 8 6 3 12 9)",
              "9 3 6 12 4 8 ", 0, answer)

BENCH_IO_TEST("sample 2",
              R"(4
42 28 84 126)",
              "126 42 84 28 ", 0, answer)

BENCH_IO_TEST("sample 3",
              R"(2
1000000000000000000 3000000000000000000)",
              "3000000000000000000 1000000000000000000 ", 0, answer)

BENCH_PERF_TEST("sample 1", answer,
                R"(6
4 8 6 3 12 9)",
                1)
