#include <gtest/gtest.h>
#include <div3-977a.hpp>
#include <macros.hpp>

TEST(DIV3977ATest, Exp1) {
    macro_test(R"(512 4)", "50", 0, answer);
}

TEST(DIV3977ATest, Exp2) {
    macro_test(R"(1000000000 9)", "1", 0, answer);
}

int main(int argc, char* argv[]) {
    testing::InitGoogleTest(&argc, argv);
    int result = RUN_ALL_TESTS();
    return result;
}

