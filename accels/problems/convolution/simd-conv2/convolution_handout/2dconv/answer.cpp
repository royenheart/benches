#include <vector>
#include <iostream>
#include "xsimd/xsimd.hpp"

using namespace std;
namespace xs = xsimd;
using vector_type = std::vector<double, xsimd::aligned_allocator<double>>;

// this function is not used in the code, just to make sure xsimd works
// it will use the strongest SIMD extension available, in our machine, it's AVX512
void mean(const vector_type& a, const vector_type& b, vector_type& res) {
    std::size_t size = a.size();
    constexpr std::size_t simd_size = xsimd::simd_type<double>::size;
    std::size_t vec_size = size - size % simd_size;

    for(std::size_t i = 0; i < vec_size; i += simd_size)
    {
        auto ba = xs::load_aligned(&a[i]);
        auto bb = xs::load_aligned(&b[i]);
        auto bres = (ba + bb) / 2.;
        bres.store_aligned(&res[i]);
    }
    for(std::size_t i = vec_size; i < size; ++i)
    {
        res[i] = (a[i] + b[i]) / 2.;
    }
}

int main(int argc, char *argv[]) {
    cout << "Hello world!" << endl;
    return 0;
}