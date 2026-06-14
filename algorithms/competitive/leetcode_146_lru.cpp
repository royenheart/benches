/**

请你设计并实现一个满足  LRU (最近最少使用) 缓存 约束的数据结构。
实现 LRUCache 类：
LRUCache(int capacity) 以 正整数 作为容量 capacity 初始化 LRU 缓存
int get(int key) 如果关键字 key 存在于缓存中，则返回关键字的值，否则返回 -1 。
void put(int key, int value) 如果关键字 key 已经存在，则变更其数据值 value
；如果不存在，则向缓存中插入该组 key-value 。如果插入操作导致关键字数量超过
capacity ，则应该 逐出 最久未使用的关键字。 函数 get 和 put 必须以 O(1)
的平均时间复杂度运行。

示例：

输入
["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]
输出
[null, null, null, 1, null, -1, null, -1, 3, 4]

解释
LRUCache lRUCache = new LRUCache(2);
lRUCache.put(1, 1); // 缓存是 {1=1}
lRUCache.put(2, 2); // 缓存是 {1=1, 2=2}
lRUCache.get(1);    // 返回 1
lRUCache.put(3, 3); // 该操作会使得关键字 2 作废，缓存是 {1=1, 3=3}
lRUCache.get(2);    // 返回 -1 (未找到)
lRUCache.put(4, 4); // 该操作会使得关键字 1 作废，缓存是 {4=4, 3=3}
lRUCache.get(1);    // 返回 -1 (未找到)
lRUCache.get(3);    // 返回 3
lRUCache.get(4);    // 返回 4

提示：

1 <= capacity <= 3000
0 <= key <= 10000
0 <= value <= 105
最多调用 2 * 105 次 get 和 put

*/

#include <bench/competitive/problem.hpp>

#include <unordered_map>

using namespace std;

struct LRUNode {
    int key;
    int val;
    LRUNode* next;
    LRUNode* prev;
    LRUNode() : key(0), val(0), next(nullptr), prev(nullptr) {};
    LRUNode(int key) : key(key) {};
    LRUNode(int key, int val)
        : key(key), val(val), next(nullptr), prev(nullptr) {};
    LRUNode(int key, int val, LRUNode* next)
        : key(key), val(val), next(next), prev(nullptr) {};
    LRUNode(int key, int val, LRUNode* next, LRUNode* prev)
        : key(key), val(val), next(next), prev(prev) {};
};

class LRUCache {
  public:
    LRUCache(int capacity) : capacity(capacity) {
        head = new LRUNode();
        tail = new LRUNode(0, 0, head, head);
        head->next = tail;
        head->prev = tail;
    };

    int get(int key) {
        auto node = index.find(key);
        if (node != index.end()) {
            auto* lrun = node->second;
            update_node(lrun);
            return lrun->val;
        }
        return -1;
    }

    void put(int key, int value) {
        auto node = index.find(key);
        if (node != index.end()) {
            auto* lrun = node->second;
            lrun->val = value;
            update_node(lrun);
        } else {
            auto* new_node = new LRUNode(key, value, head->next, head);
            index[key] = new_node;
            update_node(new_node);
            curr_eles++;
        }

        if (curr_eles > capacity) {
            auto* delete_node = tail->prev;
            delete_node->prev->next = delete_node->next;
            delete_node->next->prev = delete_node->prev;
            index.erase(delete_node->key);
            delete delete_node;
            curr_eles--;
        }
    }

  private:
    int curr_eles = 0;
    int capacity;
    LRUNode* head;
    LRUNode* tail;
    // key -> LRUNode
    unordered_map<int, LRUNode*> index;

    void update_node(LRUNode* lrun) {
        lrun->prev->next = lrun->next;
        lrun->next->prev = lrun->prev;
        auto* tmp = head->next;
        lrun->next = tmp;
        lrun->prev = head;
        head->next = lrun;
        tmp->prev = lrun;
    }
};

/**
 * Your LRUCache object will be instantiated and called as such:
 * LRUCache* obj = new LRUCache(capacity);
 * int param_1 = obj->get(key);
 * obj->put(key,value);
 */

void sample1() {
    LRUCache cache(2);
    cache.put(1, 1);
    cache.put(2, 2);
    cout << cache.get(1) << endl; // 返回 1
    cache.put(3, 3); // 该操作会使得关键字 2 作废，缓存是 {1=1, 3=3}
    cout << cache.get(2) << endl; // 返回 -1 (未找到)
    cache.put(4, 4); // 该操作会使得关键字 1 作废，缓存是 {4=4, 3=3}
    cout << cache.get(1) << endl; // 返回 -1 (未找到)
    cout << cache.get(3) << endl; // 返回 3
    cout << cache.get(4) << endl; // 返回 4
}

int answer() {
    sample1();
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)
