#include <gtest/gtest.h>
#include <p1067.hpp>
#include <macros.hpp>

TEST(P1067Test, Exp1) {
    macro_test(R"(5 
100 -1 1 -3 0 10)", "100x^5-x^4+x^3-3x^2+10", 0, answer);
}

TEST(P1067Test, Exp2) {
    macro_test(R"(3 
-50 0 0 1 )", "-50x^3+1", 0, answer);
}

TEST(P1067Test, Exp3) {
    macro_test(R"(0 
1)", "1", 0, answer);
}

TEST(P1067Test, Exp4) {
    macro_test(R"(0 
0)", "", 0, answer);
}

TEST(P1067Test, Exp5) {
    macro_test(R"(1 
1 -10)", "x-10", 0, answer);
}

int main(int argc, char* argv[]) {
    testing::InitGoogleTest(&argc, argv);
    int result = RUN_ALL_TESTS();
    return result;
}

