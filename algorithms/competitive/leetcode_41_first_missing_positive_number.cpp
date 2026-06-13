/**

给你一个未排序的整数数组 nums ，请你找出其中没有出现的最小的正整数。

请你实现时间复杂度为 O(n) 并且只使用常数级别额外空间的解决方案。

示例 1：

输入：nums = [1,2,0]
输出：3
解释：范围 [1,2] 中的数字都在数组中。
示例 2：

输入：nums = [3,4,-1,1]
输出：2
解释：1 在数组中，但 2 没有。
示例 3：

输入：nums = [7,8,9,11,12]
输出：1
解释：最小的正数 1 没有出现。

提示：

1 <= nums.length <= 10^5
-2^31 <= nums[i] <= 2^31 - 1: int

*/

#include <algorithm>
#include <bench/competitive/problem.hpp>

#include <unordered_set>
#include <vector>

using namespace std;

class Solution {
  public:
    int firstMissingPositive(vector<int>& nums) {
        // 本质上就是在维护一个布尔集合
        unordered_set<int> sets;
        int x = 1;
        for (auto n : nums) {
            sets.insert(n);
            if (n == x) {
                do {
                    x++;
                } while (sets.find(x) != sets.end());
            }
        }
        return x;
    }
};

class Solution_best {
  public:
    int firstMissingPositive(vector<int>& nums) {
        // 这里相当于就是把布尔集合原地哈希到数组上，通过一系列的特征抽取决定可行
        int n = nums.size();
        int max = n + 1;

        for (int& num : nums) {
            if (num <= 0 || num > n) {
                num = max;
            }
        }

        for (int i = 0; i < n; i++) {
            auto x = abs(nums[i]);
            // 表示出现过
            if (x != max) {
                nums[x - 1] = -abs(nums[x - 1]);
            }
        }

        for (int i = 0; i < n; i++) {
            auto x = nums[i];
            if (x > 0) {
                return i + 1;
            }
        }

        return max;
    }
};

int sample1() {
    Solution sol;
    auto q = vector({1, 2, 0});
    return sol.firstMissingPositive(q);
}

int sample2() {
    Solution sol;
    auto q = vector({3, 4, -1, 1});
    return sol.firstMissingPositive(q);
}

int sample3() {
    Solution sol;
    auto q = vector({7, 8, 9, 12, 11});
    return sol.firstMissingPositive(q);
}

int sample1_best() {
    Solution_best sol;
    auto q = vector({1, 2, 0});
    return sol.firstMissingPositive(q);
}

int sample2_best() {
    Solution_best sol;
    auto q = vector({3, 4, -1, 1});
    return sol.firstMissingPositive(q);
}

int sample3_best() {
    Solution_best sol;
    auto q = vector({7, 8, 9, 12, 11});
    return sol.firstMissingPositive(q);
}

int answer() {
    cout << sample1() << "\n";
    cout << sample2() << "\n";
    cout << sample3() << "\n";

    cout << sample1_best() << "\n";
    cout << sample2_best() << "\n";
    cout << sample3_best() << "\n";
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)
