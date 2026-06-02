#include <gtest/gtest.h>
#include <p1540.hpp>
#include <macros.hpp>

TEST(P1540Test, Exp1) {
    macro_test(R"(3 7
1 2 1 5 4 4 1)", "5", 0, answer);
}

int main(int argc, char* argv[]) {
    testing::InitGoogleTest(&argc, argv);
    int result = RUN_ALL_TESTS();
    return result;
}