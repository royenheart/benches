/**

给你一个整数数组 nums 和一个整数 k ，请你统计并返回 该数组中和为 k
的子数组的个数 。

子数组是数组中元素的连续非空序列。

示例 1：

输入：nums = [1,1,1], k = 2
输出：2
示例 2：

输入：nums = [1,2,3], k = 3
输出：2


提示：

1 <= nums.length <= 2 * 104
-1000 <= nums[i] <= 1000
-107 <= k <= 107

*/

#include <bench/competitive/problem.hpp>

#include <optional>
#include <unordered_map>
#include <vector>

using namespace std;

class Solution {
  public:
    int subarraySum(vector<int>& nums, int k) {
        int results = 0;
        size_t len = nums.size();
        vector<optional<int>> prefix_sums(len);
        prefix_sums[0] = nums[0];
        for (auto i = 0; i < len; i++) {
            if (prefix_sums[i] == k) {
                results++;
            }
            for (auto j = i + 1; j < len; j++) {
                if (prefix_sums[j] == nullopt) {
                    prefix_sums[j] = *prefix_sums[j - 1] + nums[j];
                }
                if ((*prefix_sums[j] - *prefix_sums[i]) == k) {
                    results++;
                }
            }
        }

        return results;
    }
};

// 既然都是 查找 前缀和，那直接建立 index -> 前缀和 映射即可，也就是 prefix(i) -
// prefix(j) == k ==> prefix(i) - k = prefix(j) as key;
// 同时需要从左往右便利同时建立，这样可以避免下标错位，即 j 当前已存在的 prefix
// 永远在 i 左侧， 从两次遍历 n^2 变为一次遍历 n
// * 要考虑 prefix(i) 正好为 k 的可能，由于 j 就只是从 index = 0 迭代的，要判断
// prefix(i) - k = 0 是否存在，初始就没判断不进行前缀和相减符合情况（即隐藏
// index -1）
class Solution_best {
  public:
    int subarraySum(vector<int>& nums, int k) {
        int results = 0;
        size_t len = nums.size();
        // prefix -> count
        unordered_map<int, int> prefix_sums;
        prefix_sums[0] = 1;
        int prefix_i = 0;
        for (auto i = 0; i < len; i++) {
            prefix_i += nums[i];
            if (prefix_sums.find(prefix_i - k) != prefix_sums.end()) {
                results += prefix_sums[prefix_i - k];
            }
            prefix_sums[prefix_i]++;
        }

        return results;
    }
};

int sample1() {
    Solution sol;
    auto q = vector({1, 1, 1});
    return sol.subarraySum(q, 2);
}

int sample2() {
    Solution sol;
    auto q = vector({1, 2, 3});
    return sol.subarraySum(q, 3);
}

int sample1_best() {
    Solution_best sol;
    auto q = vector({1, 1, 1});
    return sol.subarraySum(q, 2);
}

int sample2_best() {
    Solution_best sol;
    auto q = vector({1, 2, 3});
    return sol.subarraySum(q, 3);
}

int answer() {
    cout << sample1() << "\n";
    cout << sample2() << "\n";
    cout << sample1_best() << "\n";
    cout << sample2_best() << "\n";
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)

BENCH_VALUE_TEST("sample 1", sample1(), 2)
BENCH_VALUE_TEST("sample 2", sample2(), 2)

BENCH_VALUE_TEST("sample 1 best", sample1_best(), 2)
BENCH_VALUE_TEST("sample 2 best", sample2_best(), 2)

BENCH_PERF_TEST("sample 1", sample1, "", 100)
