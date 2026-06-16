/*

给你一个整数数组 nums ，判断是否存在三元组 [nums[i], nums[j], nums[k]] 满足 i !=
j、i != k 且 j != k ，同时还满足 nums[i] + nums[j] + nums[k] == 0
。请你返回所有和为 0 且不重复的三元组。

注意：答案中不可以包含重复的三元组。

示例 1：

输入：nums = [-1,0,1,2,-1,-4]
输出：[[-1,-1,2],[-1,0,1]]
解释：
nums[0] + nums[1] + nums[2] = (-1) + 0 + 1 = 0 。
nums[1] + nums[2] + nums[4] = 0 + 1 + (-1) = 0 。
nums[0] + nums[3] + nums[4] = (-1) + 2 + (-1) = 0 。
不同的三元组是 [-1,0,1] 和 [-1,-1,2] 。
注意，输出的顺序和三元组的顺序并不重要。
示例 2：

输入：nums = [0,1,1]
输出：[]
解释：唯一可能的三元组和不为 0 。
示例 3：

输入：nums = [0,0,0]
输出：[[0,0,0]]
解释：唯一可能的三元组和为 0 。

提示：

3 <= nums.length <= 3000
-105 <= nums[i] <= 105

*/

#include <bench/competitive/problem.hpp>

#include <algorithm>
#include <array>
#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

struct ArrayHash {
    size_t operator()(const array<int, 3>& arr) const {
        size_t h = 0;
        for (int x : arr) {
            h = h * 131 + x;
        }
        return h;
    }
};

class Solution {
  public:
    vector<vector<int>> threeSum(vector<int>& nums) {
        auto nums_len = nums.size();
        unordered_map<int, vector<size_t>> indexes;
        unordered_set<array<int, 3>, ArrayHash> results_tmp;
        for (size_t index = 0; index < nums_len; index++) {
            int num = nums[index];
            if (indexes.count(num) > 0) {
                indexes[num].push_back(index);
            } else {
                indexes[num] = vector({index});
            }
        }

        for (size_t i = 0; i < nums_len - 1; i++) {
            for (size_t j = i + 1; j < nums_len; j++) {
                auto a = nums[i];
                auto b = nums[j];
                auto c = -a - b;
                if (indexes.count(c) > 0) {
                    auto& idxes = indexes[c];
                    bool is_not_in =
                        any_of(idxes.begin(), idxes.end(),
                               [&](size_t x) { return x != i && x != j; });
                    if (is_not_in) {
                        array<int, 3> array3 = {a, b, c};
                        sort(array3.begin(), array3.end());
                        results_tmp.insert(array3);
                    }
                }
            }
        }

        vector<vector<int>> results;
        for (auto key : results_tmp) {
            results.push_back(vector({key[0], key[1], key[2]}));
        }

        return results;
    }
};

vector<vector<int>> sample1() {
    Solution sol;
    auto q1 = vector({0, 0, 0});
    return sol.threeSum(q1);
}

vector<vector<int>> sample2() {
    Solution sol;
    auto q2 = vector({-1, 0, 1, 2, -1, -4});
    return sol.threeSum(q2);
}

int answer() {
    cout << sample1() << endl;
    cout << sample2() << endl;
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)
