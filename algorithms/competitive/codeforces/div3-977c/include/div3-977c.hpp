#pragma once

#include <iostream>
#include <vector>
#include <algorithm>

std::vector<int> seq;

int answer() {
    int n, k;
    std::cin >> n >> k;
    seq.clear();
    for (int i = 0; i < n; i++) {
        int tmp;
        std::cin >> tmp;
        seq.push_back(tmp);
    }
    std::sort(seq.begin(), seq.end());

    if (k >= n) {
        std::cout << seq[n - 1];
        return 0;
    }

    int l = (k == 0)?1:seq[k - 1];
    int r = seq[k];

    if (l < r) {
        std::cout << l;
    } else {
        std::cout << -1;
    }

    return 0;
}