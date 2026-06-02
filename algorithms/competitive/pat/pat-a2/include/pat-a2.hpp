#pragma once

#include <iostream>
#include <queue>

int s1s = 0;
int s2s = 0;
std::queue<int> q;

int answer() {
    int l;
    std::cin >> l;
    for (int i = 0; i < l; i++) {
        char o;
        std::cin >> o;
        if (o == 'O') {
            if (s2s == 0) {
                if (s1s == 0) {
                    std::cout << "ERROR" << std::endl;
                } else {
                    std::cout << q.front() << " " << s1s * 2 + 1 << std::endl;
                    s2s = s1s - 1;
                    s1s = 0;
                    q.pop();
                }
            } else {
                std::cout << q.front() << " " << 1 << std::endl;
                s2s--;
                q.pop();
            }
        } else {
            unsigned int e;
            std::cin >> e;
            q.push(e);
            s1s++;
        }
    }

    return 0;
}