#include <gtest/gtest.h>
#include <div3-977d.hpp>
#include <macros.hpp>

TEST(DIV3977DTest, Exp1) {
    macro_test(R"(6
4 8 6 3 12 9)", "9 3 6 12 4 8 ", 0, answer);
}

TEST(DIV3977DTest, Exp2) {
    macro_test(R"(4
42 28 84 126)", "126 42 84 28 ", 0, answer);
}

TEST(DIV3977DTest, Exp3) {
    macro_test(R"(2
1000000000000000000 3000000000000000000)", "3000000000000000000 1000000000000000000 ", 0, answer);
}

int main(int argc, char* argv[]) {
    testing::InitGoogleTest(&argc, argv);
    int result = RUN_ALL_TESTS();
    return result;
}

