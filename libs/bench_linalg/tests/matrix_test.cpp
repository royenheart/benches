#include <bench/linalg/matrix.hpp>
#include <gtest/gtest.h>

TEST(Matrix, ComputesNaiveGemm) {
    const std::vector<double> a{1, 2, 3, 4, 5, 6};
    const std::vector<double> b{7, 8, 9, 10, 11, 12};

    auto out = bench::linalg::gemm_naive({2, 3}, {3, 2}, a, b);

    EXPECT_EQ(out, (std::vector<double>{58, 64, 139, 154}));
}

TEST(Matrix, ComputesCroutLu) {
    const std::vector<double> a{2, 1, 4, 3};
    std::vector<double> l(4);
    std::vector<double> u(4);

    bench::linalg::lu_crout(a, l, u, 2);
    auto recomposed = bench::linalg::gemm_naive({2, 2}, {2, 2}, l, u);

    EXPECT_TRUE(bench::linalg::approximately_equal(recomposed, a));
}
