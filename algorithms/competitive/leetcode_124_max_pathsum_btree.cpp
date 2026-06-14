/**

二叉树中的 路径
被定义为一条节点序列，序列中每对相邻节点之间都存在一条边。同一个节点在一条路径序列中
至多出现一次 。该路径 至少包含一个 节点，且不一定经过根节点。

路径和 是路径中各节点值的总和。

给你一个二叉树的根节点 root ，返回其 最大路径和 。

示例 1：

输入：root = [1,2,3]
输出：6
解释：最优路径是 2 -> 1 -> 3 ，路径和为 2 + 1 + 3 = 6
示例 2：

输入：root = [-10,9,20,null,null,15,7]
输出：42
解释：最优路径是 15 -> 20 -> 7 ，路径和为 15 + 20 + 7 = 42

提示：

树中节点数目范围是 [1, 3 * 104]
-1000 <= Node.val <= 1000

*/

#include "bench/competitive/binary_tree.hpp"
#include <bench/competitive/problem.hpp>

#include <algorithm>
#include <climits>

using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* left, TreeNode* right)
        : val(x), left(left), right(right) {}
};

/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left),
 * right(right) {}
 * };
 */
class Solution {
  public:
    // return root's max
    int node_max(TreeNode* root) {
        if (root == nullptr) {
            return 0;
        }

        auto left_max = node_max(root->left);
        auto right_max = node_max(root->right);
        auto undominated_max =
            max({root->val + right_max, root->val, root->val + left_max,
                 root->val + left_max + right_max});
        auto dominated_max =
            max({root->val + right_max, root->val, root->val + left_max});

        // 这题主要是不是所有路径都能拆成全局子问题，部分是已经到达局部最优
        // 表示如果有不受支配（已经走完）的大于仍需受支配继续判断的，先判断最大
        if (undominated_max >= dominated_max) {
            // 这条路径走完了，不能被更上一层支配（无法归纳，不是上一级的子问题），因此只能先判断记录。
            global_max = max(global_max, undominated_max);
        }

        return dominated_max;
    }

    int maxPathSum(TreeNode* root) {
        if (root == nullptr) {
            return 0;
        }

        global_max = max(global_max, node_max(root));
        return global_max;
    }

  private:
    int global_max = INT_MIN;
};

int sample1() {
    auto tree = bench::competitive::make_binary_tree<TreeNode>({1, 2, 3});

    Solution sol;
    return sol.maxPathSum(tree.root());
}

int sample2() {
    using OptionalInt =
        bench::competitive::BinaryTreeFixture<TreeNode>::optional_value_type;

    auto tree = bench::competitive::make_binary_tree<TreeNode>(
        std::initializer_list<OptionalInt>{
            OptionalInt{-10}, OptionalInt{9}, OptionalInt{20}, OptionalInt{},
            OptionalInt{}, OptionalInt{15}, OptionalInt{7}});

    Solution sol;
    return sol.maxPathSum(tree.root());
}

int sample3() {
    auto tree = bench::competitive::make_binary_tree<TreeNode>({-3});

    Solution sol;
    return sol.maxPathSum(tree.root());
}

int answer() {
    cout << sample1() << "\n";
    cout << sample2() << "\n";
    cout << sample3() << "\n";
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)

BENCH_VALUE_TEST("sample 1", sample1(), 6)
BENCH_VALUE_TEST("sample 2", sample2(), 42)
BENCH_VALUE_TEST("sample 3", sample3(), -3)
