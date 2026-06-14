/**

给你一个链表数组，每个链表都已经按升序排列。

请你将所有链表合并到一个升序链表中，返回合并后的链表。

示例 1：

输入：lists = [[1,4,5],[1,3,4],[2,6]]
输出：[1,1,2,3,4,4,5,6]
解释：链表数组如下：
[
  1->4->5,
  1->3->4,
  2->6
]
将它们合并到一个有序链表中得到。
1->1->2->3->4->4->5->6
示例 2：

输入：lists = []
输出：[]
示例 3：

输入：lists = [[]]
输出：[]

提示：

k == lists.length
0 <= k <= 10^4
0 <= lists[i].length <= 500
-10^4 <= lists[i][j] <= 10^4
lists[i] 按 升序 排列
lists[i].length 的总和不超过 10^4

*/

#include <bench/competitive/problem.hpp>

#include <queue>
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
    ListNode* mergeSort(ListNode* left, ListNode* right) {
        ListNode result;
        ListNode* node = &result;
        while (left != nullptr && right != nullptr) {
            if (left->val < right->val) {
                node->next = left;
                left = left->next;
            } else {
                node->next = right;
                right = right->next;
            }
            node = node->next;
        }
        while (left != nullptr) {
            node->next = left;
            left = left->next;
            node = node->next;
        }
        while (right != nullptr) {
            node->next = right;
            right = right->next;
            node = node->next;
        }

        return result.next;
    }

    ListNode* mergeKLists(vector<ListNode*>& lists) {
        auto len = lists.size();
        if (len == 0) {
            return nullptr;
        }
        while (len > 1) {
            size_t i = 0;
            for (; i < len / 2; i++) {
                lists[i] = mergeSort(lists[i * 2], lists[(i * 2) + 1]);
            }
            if (len % 2 == 1) {
                lists[i] = lists[i * 2];
                len = i + 1;
            } else {
                len = i;
            }
        }
        return lists[0];
    }
};

struct ListNodeGreater {
    bool operator()(const ListNode* left, const ListNode* right) {
        return left->val > right->val;
    }
};

class Solution2 {
  public:
    ListNode* mergeKLists(vector<ListNode*>& lists) {
        priority_queue<ListNode*, vector<ListNode*>, ListNodeGreater> pg;
        ListNode result;
        ListNode* node = &result;
        for (auto* l : lists) {
            while (l != nullptr) {
                pg.emplace(l);
                l = l->next;
            }
        }

        while (!pg.empty()) {
            auto* cur = pg.top();
            pg.pop();
            // 必须先断开已有的链接，避免成环
            cur->next = nullptr;
            node->next = cur;
            node = node->next;
        }

        return result.next;
    }
};

vector<int> sample1() {
    auto list1 = bench::competitive::make_singly_list<ListNode>({1, 4, 5});
    auto list2 = bench::competitive::make_singly_list<ListNode>({1, 3, 4});
    auto list3 = bench::competitive::make_singly_list<ListNode>({2, 6});

    Solution sol;
    auto q = vector({list1.head(), list2.head(), list3.head()});
    ListNode* result = sol.mergeKLists(q);

    return bench::competitive::linked_list_to_vector(
        result, list1.size() + list2.size() + list3.size());
}

vector<int> sample2() {
    Solution sol;
    vector<ListNode*> q;
    ListNode* result = sol.mergeKLists(q);

    return bench::competitive::linked_list_to_vector(result, 0);
}

vector<int> sample1_2() {
    auto list1 = bench::competitive::make_singly_list<ListNode>({1, 4, 5});
    auto list2 = bench::competitive::make_singly_list<ListNode>({1, 3, 4});
    auto list3 = bench::competitive::make_singly_list<ListNode>({2, 6});

    Solution2 sol;
    auto q = vector({list1.head(), list2.head(), list3.head()});
    ListNode* result = sol.mergeKLists(q);

    return bench::competitive::linked_list_to_vector(
        result, list1.size() + list2.size() + list3.size());
}

vector<int> sample2_2() {
    Solution2 sol;
    vector<ListNode*> q;
    ListNode* result = sol.mergeKLists(q);

    return bench::competitive::linked_list_to_vector(result, 0);
}

vector<int> sample3_2() {
    auto list1 = bench::competitive::make_singly_list<ListNode>({1, 2, 2});
    auto list2 = bench::competitive::make_singly_list<ListNode>({1, 1, 2});

    Solution2 sol;
    auto q = vector({list1.head(), list2.head()});
    ListNode* result = sol.mergeKLists(q);

    return bench::competitive::linked_list_to_vector(result, list1.size() +
                                                                 list2.size());
}

vector<int> sample4_2() {
    auto list1 = bench::competitive::make_singly_list<ListNode>({-1, -1, -1});
    auto list2 = bench::competitive::make_singly_list<ListNode>({-2, -2, -1});

    Solution2 sol;
    auto q = vector({list1.head(), list2.head()});
    ListNode* result = sol.mergeKLists(q);

    return bench::competitive::linked_list_to_vector(result, list1.size() +
                                                                 list2.size());
}

int answer() {
    cout << sample1() << "\n";
    cout << sample2() << "\n";
    cout << sample1_2() << "\n";
    cout << sample2_2() << "\n";
    cout << sample3_2() << "\n";
    cout << sample4_2() << "\n";
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)
