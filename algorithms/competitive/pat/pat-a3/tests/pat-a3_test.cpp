#include <gtest/gtest.h>
#include <pat-a3.hpp>
#include <macros.hpp>

TEST(PATA3, Exp1) {
    macro_test(R"(9
2 3 1 5 4 7 8 6 9
1 2 3 6 7 4 5 8 9)", R"(2 * 3 / 4 = 1)", 0, answer);
}

int main(int argc, char* argv[]) {
    testing::InitGoogleTest(&argc, argv);
    int result = RUN_ALL_TESTS();
    return result;
}