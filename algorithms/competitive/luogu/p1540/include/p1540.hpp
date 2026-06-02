#pragma once
#include <iostream>
#include <queue>

bool set[1001] = {false};
std::queue<int> mem;

int answer() {
    int m, n;
    int count = 0;
    std::cin >> m >> n;
    for (int i = 0; i < n; i++) {
        int w;
        std::cin >> w;
        if (set[w] == false) {
            count++;
            set[w] = true;
            mem.push(w);
            if (mem.size() > m) {
                set[mem.front()] = false;
                mem.pop();
            }
        }
    }
    std::cout << count;
    return 0;
}