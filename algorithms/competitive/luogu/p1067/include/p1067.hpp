#pragma once
#include <iostream>
#include <sstream>
#include <string>

int answer() {
    int n;
    std::cin >> n;
    std::string out;
    for (int i = n; i >= 0; i--) {
        int a;
        std::cin >> a;
        if (a != 0) {
            if (a > 0) {
                out.push_back('+');
            } else {
                out.push_back('-');
            }
            if (i != 0) {
                if (abs(a) != 1) {
                    out.append(std::to_string(abs(a)));
                }
                out.append("x");
                if (i != 1) {
                    out.push_back('^');
                    out.append(std::to_string(i));
                }
            } else {
                out.append(std::to_string(abs(a)));
            }
        }
    }
    if (out.length() > 0 && out[0] == '+') {
        out = out.substr(1);
    }
    std::cout << out;
    return 0;
}
