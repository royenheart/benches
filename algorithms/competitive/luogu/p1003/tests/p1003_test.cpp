#include <gtest/gtest.h>
#include <p1003.hpp>
#include <macros.hpp>

TEST(P1003Test, Exp1) {
    macro_test(R"(3
1 0 2 3
0 2 3 3
2 1 3 3
2 2)", "3", 0, answer);
}

TEST(P1003Test, Exp2) {
    macro_test(R"(3
1 0 2 3
0 2 3 3
2 1 3 3
4 5)", "-1", 0, answer);
}

int main(int argc, char* argv[]) {
    testing::InitGoogleTest(&argc, argv);
    int result = RUN_ALL_TESTS();
    return result;
}

