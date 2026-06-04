#pragma once

#include <queue>
#include <iostream>

int answer() {
    int l;
    std::cin >> l;

    int s1s = 0;
    int s2s = 0;
    bool first_output = true;
    std::queue<int> q;

    auto emit_line_prefix = [&first_output]() {
        if (!first_output) {
            std::cout << "\n";
        }
        first_output = false;
    };

    for (int i = 0; i < l; i++) {
        char o;
        std::cin >> o;
        if (o == 'O') {
            if (s2s == 0) {
                if (s1s == 0) {
                    emit_line_prefix();
                    std::cout << "ERROR";
                } else {
                    emit_line_prefix();
                    std::cout << q.front() << " " << s1s * 2 + 1;
                    s2s = s1s - 1;
                    s1s = 0;
                    q.pop();
                }
            } else {
                emit_line_prefix();
                std::cout << q.front() << " " << 1;
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
