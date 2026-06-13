/**

给你一个整数数组 nums，有一个大小为 k
的滑动窗口从数组的最左侧移动到数组的最右侧。你只可以看到在滑动窗口内的 k
个数字。滑动窗口每次只向右移动一位。

返回 滑动窗口中的最大值。

示例 1：

输入：nums = [1,3,-1,-3,5,3,6,7], k = 3
输出：[3,3,5,5,6,7]
解释：
滑动窗口的位置                最大值
---------------               -----
[1  3  -1] -3  5  3  6  7       3
 1 [3  -1  -3] 5  3  6  7       3
 1  3 [-1  -3  5] 3  6  7       5
 1  3  -1 [-3  5  3] 6  7       5
 1  3  -1  -3 [5  3  6] 7       6
 1  3  -1  -3  5 [3  6  7]      7
示例 2：

输入：nums = [1], k = 1
输出：[1]


提示：

1 <= nums.length <= 105
-104 <= nums[i] <= 104
1 <= k <= nums.length

*/

#include <bench/competitive/problem.hpp>

#include <deque>
#include <tuple>
#include <vector>

using namespace std;

class Solution {
  public:
    vector<int> maxSlidingWindow(vector<int>& nums, int k) {
        // value, index
        deque<tuple<int, int>> max_candidates;
        vector<int> results;

        // 1. init candidates
        for (int i = 0; i < k; i++) {
            auto num = nums[i];
            while (!max_candidates.empty() &&
                   num >= get<0>(max_candidates.back())) {
                max_candidates.pop_back();
            }
            max_candidates.emplace_back(num, i);
        }
        results.push_back(get<0>(max_candidates.front()));

        // 2. slide window
        for (int i = k; i < nums.size(); i++) {
            // 2.1 pop frontend if index
            if (get<1>(max_candidates.front()) <= (i - k)) {
                max_candidates.pop_front();
            }

            // 2.2 push next candidate
            auto num = nums[i];
            while (!max_candidates.empty() &&
                   num >= get<0>(max_candidates.back())) {
                max_candidates.pop_back();
            }
            max_candidates.emplace_back(num, i);

            // 2.3 append result
            results.push_back(get<0>(max_candidates.front()));
        }

        return results;
    }
};

vector<int> sample1() {
    Solution sol;
    auto q = vector({1, 3, -1, -3, 5, 3, 6, 7});
    return sol.maxSlidingWindow(q, 3);
}

vector<int> sample2() {
    Solution sol;
    auto q = vector({1});
    return sol.maxSlidingWindow(q, 1);
}

int answer() {
    cout << sample1() << "\n";
    cout << sample2() << "\n";
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)

BENCH_VALUE_TEST("sample 1", sample1(), (vector<int>({3, 3, 5, 5, 6, 7})))
BENCH_VALUE_TEST("sample 2", sample2(), (vector<int>({1})))
