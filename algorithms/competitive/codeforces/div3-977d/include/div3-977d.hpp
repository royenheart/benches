#pragma once

#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <stack>
#include <vector>
#include <deque>
#include <algorithm>

#define MAX 101

size_t ns[MAX];
bool visited[MAX];
std::vector<std::deque<size_t>> segs;

// typedef struct node {
//     size_t value;
//     node *l, *r;
//     node() {l = nullptr; r = nullptr;}
// };

// // index -> value
// size_t ns[MAX];
// // 已被访问，index -> bool，未被访问为 false
// bool accessed[MAX];
// // value -> indexes，提供查找
// std::unordered_map<size_t, std::vector<int>> vs;
// // roots, value -> roots
// std::unordered_map<size_t, std::vector<node*>> roots;

// node *tree(int index) {
//     auto value = ns[index];
//     node *root = new node();
//     root->value = value;
//     accessed[index] = true;
//     auto ti = std::find(vs[value].begin(), vs[value].end(), index);
//     vs[value].erase(ti);
//     if (vs[value].size() == 0) {
//         vs.erase(value);
//     }

//     auto lv = value * 3;
//     auto rv = value * 2;
    
//     if (vs.count(lv) > 0) {
//         auto index = vs[lv].back();
//         auto tlv = tree(index);
//         root->l = tlv;
//     } /* else if (roots.count(lv) > 0) {
//         // 从 root 中找
//         auto tlv = roots[lv].back();
//         root->l = tlv;
//         roots[lv].pop_back();
//         if (roots[lv].size() == 0) {
//             roots.erase(lv);
//         }
//     } */

//     if (vs.count(rv) > 0) {
//         auto index = vs[rv].back();
//         auto rlv = tree(index);
//         root->r = rlv;
//     } /* else if (roots.count(rv) > 0) {
//         // 从 root 中找
//         auto rlv = roots[rv].back();
//         root->r = rlv;
//         roots[rv].pop_back();
//         if (roots[rv].size() == 0) {
//             roots.erase(rv);
//         }
//     } */

//     return root;
// }

// void dfs_m(node* tree) {
//     if (tree == nullptr) {
//         return;
//     }

//     dfs_m(tree->l);
//     std::cout << tree->value << " ";
//     dfs_m(tree->r);
// }

int answer() {
    int n;
    std::cin >> n;
    // 1. 任何树的节点通过旋转变换都可以作为根节点
    // 2. 但若是添加了一定规则的树，原理 1 不能被确定
    // 3. 值相同即相同，没有额外的区别
    // 4. 选取一个节点不断需求数，可通过 unordered_map 快速获取，同时需要一个数组记录已被加入的节点，获得一棵树
    //  改进，若已被加入，可以判断其是否为根节点，那么构造时加入，然后取消其为根节点的标志，这样遍历一次便可获得完整的树。
    //  因此还需要一个数组记录当前各个根节点
    //  最后数组剩下的根节点一定是最后的数
    // 5. 已被添加进树的数被忽略，遍历所有数
    // 遍历后获得多个森林，将这些森林按照一定规则进行组合 错误
    //  组合不代表一定有，可能就是独立子树
    //  若不保证有一个答案，那么生成的树遍历可能不代表正确的（因为本身就无法组成这样的序列）
    //  还有一个问题，顺序不一样可能遍历后生成的也会有不一样，可能一个是对的，一个是错的。
    // 组合完毕后得到一棵树，最后中序遍历

    //      0
    //   0     0
    // 0         0
    // 这种形式的数中序遍历才能正确。。。

    /*
    vs.clear();
    roots.clear();

    for (int i = 0; i < n; i++) {
        size_t v;
        std::cin >> v;
        ns[i] = v;
        accessed[i] = false;
        // [] 被重载为添加一个键
        vs[v].push_back(i);
    }

    for (int i = 0; i < n; i++) {
        if (accessed[i] == true) {
            continue;
        }
        auto v = ns[i];
        auto t = tree(i);
        roots[v].push_back(t);
    }

    for (auto root : roots) {
        auto t = root.second.front();
        dfs_m(t);
        std::cout << std::endl;
        // break;
    }
    */

    // 所以还是应该用双向队列
    // 先生成多个双向队列，最后组合。

    for (int i = 0; i < n; i++) {
        size_t v;
        std::cin >> v;
        ns[i] = v;
        visited[i] = false;        
    }

    for (int i = 0; i < n; i++) {
        if (visited[i]) continue;
        std::deque<size_t> newd;
        newd.push_back(ns[i]);
        segs.push_back(newd);
    }

    return 0;
}