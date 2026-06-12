#include <bench/competitive/problem.hpp>

#include <iostream>

typedef struct node node;
struct node {
    int v;
    node* l;
    node* r;
    node() {
        l = nullptr;
        r = nullptr;
    }
};

int ins[21];
int pres[21];
int d0 = 0;
int d1 = 0;
int d2 = 0;

node* cons_tree(int ins_l, int ins_r, int pres_l, int pres_r) {
    if (ins_r < ins_l) {
        return nullptr;
    }
    int root_v = pres[pres_l];
    int i;
    node* root = new node();
    for (i = ins_l; i <= ins_r; i++) {
        if (ins[i] == root_v) {
            break;
        }
    }
    node* l = cons_tree(ins_l, i - 1, pres_l + 1, pres_l + i - ins_l);
    node* r = cons_tree(i + 1, ins_r, pres_l + i - ins_l + 1, pres_r);
    root->l = l;
    root->r = r;
    return root;
}

// 前序深度遍历
void pre(node* tree) {
    if (tree == nullptr) {
        return;
    }

    // 先访问中间节点
    int l = (tree->l == nullptr) ? 0 : 1;
    int r = (tree->r == nullptr) ? 0 : 1;
    int v = l + r;
    switch (v) {
    case 0:
        d0++;
        break;
    case 1:
        d1++;
        break;
    case 2:
        d2++;
        break;
    default:
        break;
    }
    pre(tree->l);
    pre(tree->r);
    return;
}

int answer() {
    int n;
    std::cin >> n;

    // 获取中序遍历，所有 key 都互不相同
    for (int i = 0; i < n; i++) {
        std::cin >> ins[i];
    }

    // 获取前序遍历
    for (int i = 0; i < n; i++) {
        std::cin >> pres[i];
    }

    node* tree = cons_tree(0, n - 1, 0, n - 1);

    pre(tree);

    std::cout << d1 << " * " << d2 << " / " << d0 << " = " << d1 * d2 / d0;

    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)

BENCH_IO_TEST("sample 1",
              R"(9
2 3 1 5 4 7 8 6 9
1 2 3 6 7 4 5 8 9)",
              R"(2 * 3 / 4 = 1)", 0, answer)

BENCH_PERF_TEST("sample 1", answer,
                R"(9
2 3 1 5 4 7 8 6 9
1 2 3 6 7 4 5 8 9)",
                1)
