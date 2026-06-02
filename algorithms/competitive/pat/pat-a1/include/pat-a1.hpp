#pragma once

#include <iostream>
#include <stack>
#include <vector>
#include <tuple>

#define MAX 102

char map[MAX][MAX] = {0};
std::stack<std::tuple<int, int>> poses;

// 到达第 0 行即可

bool reach_dfs() {
    while (!poses.empty()) {
        auto t = poses.top();
        poses.pop();
        auto p = std::get<0>(t);
        auto q = std::get<1>(t);
        for (; p > 0; p--) {
            if (map[p][q] == 1) {
                break;
            }
        }
        if (p == 0) {
            return true;
        }
        p++; q--;
        for (; q > 0; q--) {
            if (map[p][q] == 1) {
                break;
            }
            if (map[p - 1][q] == 0) {
                poses.push(std::tuple<int, int>(p - 1, q));
                break;
            }
        }
        if (q == 0) {
            return true;
        }
    }
    
    return false;
}

int answer() {
    int size;
    std::cin >> size;
    for (int i = 1; i <= size; i++) {
        for (int j = 1; j <= size; j++) {
            char a;
            std::cin >> a;
            if (a == '0') {
                map[i][j] = 0;
            } else {
                map[i][j] = 1;
            }
        }
    }

    std::vector<int> pp;
    pp.clear();

    for (int q = 1; q <= size; q++) {
        while (!poses.empty()) poses.pop();
        poses.push(std::tuple(size + 1, q));
        bool is = reach_dfs();
        if (!is) {
            pp.push_back(q);
        }
    }

    auto iter = pp.begin();
    for (; iter != pp.end() - 1; iter++) {
        std::cout << *iter << " ";
    }
    std::cout << *iter;

    return 0;
}