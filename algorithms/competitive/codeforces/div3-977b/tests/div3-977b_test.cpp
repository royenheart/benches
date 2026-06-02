#include <gtest/gtest.h>
#include <div3-977b.hpp>
#include <macros.hpp>

TEST(DIV3977BTest, Exp1) {
    macro_test(R"(7
ABACABA)", "BA", 0, answer);
}

TEST(DIV3977BTest, Exp2) {
    macro_test(R"(5
ZZZAA)", "ZZ", 0, answer);
}

int main(int argc, char* argv[]) {
    testing::InitGoogleTest(&argc, argv);
    int result = RUN_ALL_TESTS();
    return result;
}

