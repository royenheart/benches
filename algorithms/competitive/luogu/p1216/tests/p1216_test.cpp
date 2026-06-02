#include <gtest/gtest.h>
#include <p1216.hpp>
#include <macros.hpp>

TEST(P1216Test, Exp1) {
    macro_test(R"(5
7
3 8
8 1 0
2 7 4 4
4 5 2 6 5)", "30", 0, answer);
}

int main(int argc, char* argv[]) {
    testing::InitGoogleTest(&argc, argv);
    int result = RUN_ALL_TESTS();
    return result;
}
