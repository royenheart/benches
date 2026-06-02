#include <gtest/gtest.h>
#include <pat-a2.hpp>
#include <macros.hpp>

TEST(PATA2, Exp1) {
    macro_test(R"(10
I 20
I 32
O
I 11
O
O
O
I 100
I 66
O)", R"(20 5
32 1
11 3
ERROR
100 5)", 0, answer);
}

int main(int argc, char* argv[]) {
    testing::InitGoogleTest(&argc, argv);
    int result = RUN_ALL_TESTS();
    return result;
}