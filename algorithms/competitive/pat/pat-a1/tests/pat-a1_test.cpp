#include <gtest/gtest.h>
#include <pat-a1.hpp>
#include <macros.hpp>

TEST(PATA1, Exp1) {
    macro_test(R"(10
0000000000
0000111010
1100100011
0000110001
0000000011
0000000000
0100000100
0001000000
0001000000
0001100000)", "7 8", 0, answer);
}

int main(int argc, char* argv[]) {
    testing::InitGoogleTest(&argc, argv);
    int result = RUN_ALL_TESTS();
    return result;
}