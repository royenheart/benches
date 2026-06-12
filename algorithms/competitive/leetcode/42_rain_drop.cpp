#include <algorithm>
#include <iterator>
#include <vector>

#include <iostream>

using namespace std;

class Solution {
  public:
    int trap(vector<int>& height) {
        int results = 0;
        int partial_heights = 0;

        if (height.size() <= 2) {
            return 0;
        }

        auto begin =
            find_if(height.begin(), height.end(), [](int& x) { return x > 0; });
        if (begin == height.end()) {
            return 0;
        }

        auto rend = find_if(height.rbegin(), height.rend(),
                            [](int& x) { return x > 0; });
        // real end, 此时由于正向一定有 >0，那么反向也肯定是有的
        auto end = prev(rend.base());
        if (end == begin) {
            return 0;
        }
        auto i = begin;

        // 1. 找递增序列
        for (auto j = next(begin); j <= end; j++) {
            if (*j >= *i) {
                results += (*i * (distance(i, j) - 1)) - partial_heights;
                i = j;
                partial_heights = 0;
            } else {
                partial_heights += *j;
            }
        }

        // 2. 从递增序列末尾开始二分计算 max 进行类似操作
        if (i >= end) {
            return results;
        }
        while (next(i) < end) {
            partial_heights = 0;
            auto mid_max = max_element(next(i), next(end));
            // cout << *i << "," << *mid_max << "," << endl;
            for (auto j = next(i); j < mid_max; j++) {
                partial_heights += *j;
            }
            results +=
                (*mid_max * (distance(i, mid_max) - 1)) - partial_heights;
            i = mid_max;
        }

        return results;
    }
};

int main() {
    Solution sol;
    auto q1 = vector({0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1});
    auto a1 = sol.trap(q1);
    cout << a1 << endl;

    auto q2 = vector({4, 2, 0, 3, 2, 5});
    auto a2 = sol.trap(q2);
    cout << a2 << endl;

    auto q3 = vector({4, 2, 3});
    auto a3 = sol.trap(q3);
    cout << a3 << endl;
}
