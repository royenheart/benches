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

    // #pragma omp task is OpenMP 3.0+; MSVC /openmp (2.0) lacks it, so guard
    // it and run the sorts serially there.
#if defined(_OPENMP) && _OPENMP >= 200805
    #pragma omp task
#endif
    std::sort(i1, j2, [](int a, int b) { return a > b; });
#if defined(_OPENMP) && _OPENMP >= 200805
    #pragma omp task
#endif
    std::sort(i2, j2, [](int a, int b) { return a < b; });
    
    for (auto i : v) {
        std::cout << i << " ";
    }
    std::cout << std::endl;

    return 0;
}