/**

给你一个链表，两两交换其中相邻的节点，并返回交换后链表的头节点。你必须在不修改节点内部的值的情况下完成本题（即，只能进行节点交换）。

示例 1：

输入：head = [1,2,3,4]
输出：[2,1,4,3]
示例 2：

输入：head = []
输出：[]
示例 3：

输入：head = [1]
输出：[1]

提示：

链表中节点的数目在范围 [0, 100] 内
0 <= Node.val <= 100

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
    ListNode* swapPairs(ListNode* head) {
        if (head == nullptr || head->next == nullptr) {
            return head;
        }

        ListNode dummy(0, head);
        ListNode* prev_head = &dummy;
        while (head != nullptr && head->next != nullptr) {
            // swap, 此时该区间头节点为 sec
            ListNode* sec = head->next;
            head->next = sec->next;
            sec->next = head;

            prev_head->next = sec;
            prev_head = head;
            head = head->next;
        }

        return dummy.next;
    }
};

vector<int> sample1() {
    auto list = bench::competitive::make_singly_list<ListNode>({1, 2, 3, 4});

    Solution sol;
    ListNode* result = sol.swapPairs(list.head());

    return list.to_vector(result);
}

vector<int> sample2() {
    auto list = bench::competitive::make_singly_list<ListNode>({});

    Solution sol;
    ListNode* result = sol.swapPairs(list.head());

    return list.to_vector(result);
}

vector<int> sample3() {
    auto list = bench::competitive::make_singly_list<ListNode>({1});

    Solution sol;
    ListNode* result = sol.swapPairs(list.head());

    return list.to_vector(result);
}

vector<int> sample4() {
    auto list = bench::competitive::make_singly_list<ListNode>({1, 2, 3});

    Solution sol;
    ListNode* result = sol.swapPairs(list.head());

    return list.to_vector(result);
}

int answer() {
    cout << sample1() << "\n";
    cout << sample2() << "\n";
    cout << sample3() << "\n";
    cout << sample4() << "\n";
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)

BENCH_VALUE_TEST("sample 1", sample1(), (vector<int>{2, 1, 4, 3}))
BENCH_VALUE_TEST("sample 2", sample2(), (vector<int>{}))
BENCH_VALUE_TEST("sample 3", sample3(), (vector<int>{1}))
BENCH_VALUE_TEST("sample 4", sample4(), (vector<int>{2, 1, 3}))
