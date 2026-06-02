#include <gtest/gtest.h>
#include <div3-977c.hpp>
#include <macros.hpp>

TEST(DIV3977CTest, Exp1) {
    macro_test(R"(7 4
3 7 5 1 10 3 20)", "5", 0, answer);
}

TEST(DIV3977CTest, Exp2) {
    macro_test(R"(7 2
3 7 5 1 10 3 20)", "-1", 0, answer);
}

TEST(DIV3977CTest, Exp3) {
    macro_test(R"(1 0
1)", "-1", 0, answer);
}

TEST(DIV3977CTest, Exp4) {
    macro_test(R"(1 0
2)", "1", 0, answer);
}

TEST(DIV3977CTest, Exp5) {
    macro_test(R"(2 3
1 2)", "2", 0, answer);
}

int main(int argc, char* argv[]) {
    testing::InitGoogleTest(&argc, argv);
    int result = RUN_ALL_TESTS();
    return result;
}

