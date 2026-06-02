#include <gtest/gtest.h>
#include <pat-a4.hpp>
#include <macros.hpp>

TEST(PATA4, Exp1) {
    macro_test(R"(12
7 11
8 9
3 1
2 12
4 6
10 0
5 1
2 5
6 8
1 4
7 2
9 3)", R"(359114268072)", 0, answer);
}

int main(int argc, char* argv[]) {
    testing::InitGoogleTest(&argc, argv);
    int result = RUN_ALL_TESTS();
    return result;
}