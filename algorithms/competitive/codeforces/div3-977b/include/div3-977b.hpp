#pragma once

#include <iostream>
#include <string>
#include <unordered_map>

std::unordered_map<std::string, int> times;

int answer() {
    int n;
    std::string s;
    std::cin >> n;
    std::cin >> s;
    times.clear();

    for (int i = 0; i < n - 1; i++) {
        auto news = s.substr(i, 2);
        if (times.count(news) > 0) {
            times[news]++;
        } else {
            times[news] = 1;
        }
    }

    int max_time = 0;
    std::string max_s;
    for (auto k : times) {
        if (k.second > max_time) {
            max_time = k.second;
            max_s = k.first;
        }
    }
    std::cout << max_s;

    return 0;
}