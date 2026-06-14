/**

给你链表的头节点 head ，每 k 个节点一组进行翻转，请你返回修改后的链表。

k 是一个正整数，它的值小于或等于链表的长度。如果节点总数不是 k
的整数倍，那么请将最后剩余的节点保持原有顺序。

你不能只是单纯的改变节点内部的值，而是需要实际进行节点交换。

示例 1：

输入：head = [1,2,3,4,5], k = 2
输出：[2,1,4,3,5]

示例 2：

输入：head = [1,2,3,4,5], k = 3
输出：[3,2,1,4,5]

提示：
链表中的节点数目为 n
1 <= k <= n <= 5000
0 <= Node.val <= 1000

进阶：你可以设计一个只用 O(1) 额外内存空间的算法解决此问题吗？

*/

#include <bench/competitive/problem.hpp>

#include <vector>

using namespace std;

struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};

/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */
class Solution {
  public:
    ListNode* reverseKGroup(ListNode* head, int k) {
        vector<ListNode*> stacks;
        auto prev_head = new ListNode(0, head);
        auto prev_list_end = prev_head;
        int last = k;
        while (head != nullptr) {
            if (last > 0) {
                stacks.push_back(head);
                head = head->next;
                last--;
            } else {
                auto next_list_head = stacks.back()->next;
                auto n = stacks.back();
                prev_list_end->next = n;
                while (stacks.size() > 1) {
                    stacks.pop_back();
                    n->next = stacks.back();
                    // cout << n->val << endl;
                    n = stacks.back();
                }
                n->next = next_list_head;
                prev_list_end = n;

                last = k;
                head = next_list_head;
                stacks.pop_back();
            }
        }

        if (stacks.size() > 0 && last == 0) {
            auto next_list_head = stacks.back()->next;
            auto n = stacks.back();
            prev_list_end->next = n;
            while (stacks.size() > 1) {
                stacks.pop_back();
                n->next = stacks.back();
                // cout << n->val << endl;
                n = stacks.back();
            }
            n->next = next_list_head;
            prev_list_end = n;

            last = k;
            head = next_list_head;
            stacks.pop_back();
        }

        return prev_head->next;
    }
};

vector<int> sample1() {
    auto list = bench::competitive::make_singly_list<ListNode>({1, 2, 3, 4, 5});

    Solution sol;
    ListNode* result = sol.reverseKGroup(list.head(), 2);

    return list.to_vector(result);
}

vector<int> sample2() {
    auto list = bench::competitive::make_singly_list<ListNode>({1, 2, 3, 4, 5});

    Solution sol;
    ListNode* result = sol.reverseKGroup(list.head(), 3);

    return list.to_vector(result);
}

vector<int> sample3() {
    auto list = bench::competitive::make_singly_list<ListNode>({1, 2});

    Solution sol;
    ListNode* result = sol.reverseKGroup(list.head(), 2);

    return list.to_vector(result);
}

int answer() {
    cout << sample1() << "\n";
    cout << sample2() << "\n";
    cout << sample3() << "\n";
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)
