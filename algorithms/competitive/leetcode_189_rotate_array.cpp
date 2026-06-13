/**

给定一个整数数组 nums，将数组中的元素向右轮转 k 个位置，其中 k 是非负数。

示例 1:

输入: nums = [1,2,3,4,5,6,7], k = 3
输出: [5,6,7,1,2,3,4]
解释:
向右轮转 1 步: [7,1,2,3,4,5,6]
向右轮转 2 步: [6,7,1,2,3,4,5]
向右轮转 3 步: [5,6,7,1,2,3,4]
示例 2:

输入：nums = [-1,-100,3,99], k = 2
输出：[3,99,-1,-100]
解释:
向右轮转 1 步: [99,-1,-100,3]
向右轮转 2 步: [3,99,-1,-100]

提示：

1 <= nums.length <= 105
-231 <= nums[i] <= 231 - 1
0 <= k <= 105

*/

#include <bench/competitive/problem.hpp>

#include <vector>

using namespace std;

class Solution {
  public:
    void rotate(vector<int>& nums, int k) {
        auto len = nums.size();
        k = k % len;
        vector a(nums.begin() + len - k, nums.end());
        nums.insert(nums.begin(), a.begin(), a.end());
        nums.resize(len);
    }
};

vector<int> sample1() {
    Solution sol;
    auto q = vector({1, 2, 3, 4, 5, 6, 7});
    sol.rotate(q, 3);
    return q;
}

vector<int> sample2() {
    Solution sol;
    auto q = vector({-1, -100, 3, 99});
    sol.rotate(q, 2);
    return q;
}

vector<int> sample3() {
    Solution sol;
    auto q = vector({-1});
    sol.rotate(q, 2);
    return q;
}

vector<int> sample4() {
    Solution sol;
    auto q = vector({-1, 2});
    sol.rotate(q, 3);
    return q;
}

vector<int> sample5() {
    Solution sol;
    auto q = vector({1, 2, 3});
    sol.rotate(q, 1);
    return q;
}

int answer() {
    cout << sample1() << "\n";
    cout << sample2() << "\n";
    cout << sample3() << "\n";
    cout << sample4() << "\n";
    cout << sample5() << "\n";
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)
