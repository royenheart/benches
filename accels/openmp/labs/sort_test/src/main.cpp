#include <vector>
#include <algorithm>
#include <iostream>
#include <omp.h>

int main() {
    omp_set_num_threads(2);
    
    std::vector<int> v = {1, 2, 3, 4, 5, 6, 7, 8, 9};
    auto i1 = v.begin();
    auto j1 = v.end();
    j1 -= 4;
    auto i2 = v.begin();
    auto j2 = v.end();
    i2 += 4;

    #pragma omp task
    std::sort(i1, j2, [](int a, int b) { return a > b; });
    #pragma omp task
    std::sort(i2, j2, [](int a, int b) { return a < b; });
    
    for (auto i : v) {
        std::cout << i << " ";
    }
    std::cout << std::endl;

    return 0;
}