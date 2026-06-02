#pragma once

#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <tuple>

std::unordered_map<int, char> bits;
std::vector<std::tuple<int, int>> pairs;
std::unordered_set<int> pairs_seted;

int answer() {
    int n;
    std::cin >> n;
    int max_single_num = (n > 9)?9:n;
    for (int i = 0; i < n; i++) {
        int a, b;
        std::cin >> a >> b;
        // 大于 9 才能判定为是序号，即使 n < 9, 若使用 n 判定，会导致写的也会被判定为序号
        if (a > 9 || b == 0) {
            // a 必定序号
            bits[a] = b + '0';
            continue;
        }
        if (a == 0 || b > 9) {
            // a 必定是写的
            bits[b] = a + '0';
            continue;
        }
        pairs.push_back(std::tuple(a, b));
    }

    // 当 a，b 都是 1 - (n > 9)?n:9;
    // 选择组合，但是还需要满足选择得到的序号是能从 1 排到 n 的（首先满足）
    // 在这里相当于只需要得到 1 至 9 的部分或者全部即可，大于 9 必定已经确定。
    // 且需要满足选择的使得数最小
    // 即序号越小，对应的数需越小
    // 剩下 2 3，只会剩下 2 对
    // 但如果选择了 2 3 中的 3 作为序号，那么 2 序号没了，这个时候下次遇到 2 序号时，剥夺设置（erase），再次自小到大遍历 
    // 即剥夺 pairs 的所有权
    // 1 2
    // 2 3
    // 3 4
    bool next_itr = true;
    while (next_itr) {
        // 遍历可能的序号，若 n < 9，那就是 1-n，否则使用 1-9 即可。
        for (int i = 1; i <= max_single_num; i++) {
            if (bits.count(i) == 0) {
                int smallest = 10;
                int pair_j = 10;
                for (int j = 0; j < pairs.size(); j++) {
                    if (pairs_seted.count(j) == 1) {
                        continue;
                    }
                    auto a = std::get<0>(pairs[j]);
                    auto b = std::get<1>(pairs[j]);
                    if (a == i && b < smallest) {
                        smallest = b;
                        pair_j = j;
                    }
                    if (b == i && a < smallest) {
                        smallest = a;
                        pair_j = j;
                    }
                }
                // 被占用了
                if (pair_j == 10) {
                    // 可能有多个占用，选一个占用最少的
                    int small = 10;
                    for (auto pair_j_iter : pairs_seted) {
                        auto a = std::get<0>(pairs[pair_j_iter]);
                        auto b = std::get<1>(pairs[pair_j_iter]);
                        if (a == i && b < small) {
                            small = b;
                        } else if (b == i && a < small) {
                            small = a;
                        }
                    }
                    bits[i] = '0' + small;
                    bits.erase(small);
                } else {
                    // 未被占用
                    bits[i] = '0' + smallest;
                    pairs_seted.emplace(pair_j);
                }
            }
        }
        next_itr = false;
        for (int i = 1; i <= max_single_num; i++) {
            if (bits.count(i) == 0) {
                next_itr = true;
                break;
            }
        }
    }
    
    for (int i = 1; i <= n; i++) {
        std::cout << bits[i];
    }

    return 0;
}