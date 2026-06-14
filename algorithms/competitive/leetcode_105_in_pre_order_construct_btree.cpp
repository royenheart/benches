/**

给定两个整数数组 preorder 和 inorder ，其中 preorder 是二叉树的先序遍历，
inorder 是同一棵树的中序遍历，请构造二叉树并返回其根节点。

示例 1:

输入: preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]
输出: [3,9,20,null,null,15,7]
示例 2:

输入: preorder = [-1], inorder = [-1]
输出: [-1]

提示:

1 <= preorder.length <= 3000
inorder.length == preorder.length
-3000 <= preorder[i], inorder[i] <= 3000
preorder 和 inorder 均 无重复 元素
inorder 均出现在 preorder
preorder 保证 为二叉树的前序遍历序列
inorder 保证 为二叉树的中序遍历序列

*/

#include "bench/competitive/binary_tree.hpp"
#include <bench/competitive/problem.hpp>

#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

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
    TreeNode* b(int i, int j) {
        if (preorder_index >= preorder.size()) {
            return nullptr;
        }
        auto val = preorder[preorder_index];
        auto* head = new TreeNode(val);
        if (i == j) {
            return head;
        }
        int mid_index = inorder_map[val];
        // 先左子节点
        if (mid_index - 1 >= i) {
            // cout << "gh" << mid_index << "," << i << endl;
            preorder_index++;
            head->left = b(i, mid_index - 1);
        }
        // 再右子节点
        if (j >= mid_index + 1) {
            preorder_index++;
            head->right = b(mid_index + 1, j);
        }
        return head;
    }

    TreeNode* buildTree(vector<int>& preorder, vector<int>& inorder) {
        this->inorder = inorder;
        this->preorder = preorder;
        // inordered hash: value -> index
        // 无重复元素
        int size = inorder.size();
        for (int i = 0; i < size; i++) {
            inorder_map[inorder[i]] = i;
        }
        return b(0, size - 1);
    }

  private:
    vector<int> preorder;
    vector<int> inorder;
    unordered_map<int, int> inorder_map;
    int preorder_index = 0;
};

vector<string> sample1() {
    vector<int> preorder{1, 2};
    vector<int> inorder{1, 2};

    Solution sol;
    TreeNode* root = sol.buildTree(preorder, inorder);

    cout << bench::competitive::binary_tree_pretty(root, preorder.size())
         << endl;

    return bench::competitive::binary_tree_to_level_strings(root,
                                                            preorder.size());
}

vector<string> sample2() {
    vector<int> preorder{3, 1, 2, 4};
    vector<int> inorder{1, 2, 3, 4};

    Solution sol;
    TreeNode* root = sol.buildTree(preorder, inorder);

    cout << bench::competitive::binary_tree_pretty(root, preorder.size())
         << endl;

    return bench::competitive::binary_tree_to_level_strings(root,
                                                            preorder.size());
}

int answer() {
    cout << sample1() << "\n";
    cout << sample2() << "\n";
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)
