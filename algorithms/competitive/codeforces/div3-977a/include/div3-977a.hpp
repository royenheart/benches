#pragma once

#include <iostream>

int answer() {
    size_t n, k;
    std::cin >> n >> k;
    for (auto i = 0; i < k; i++) {
        int l = n % 10;
        if (l == 0) {
            n /= 10;
        } else {
            n--;
        }
    }
    std::cout << n;
    return 0;
}