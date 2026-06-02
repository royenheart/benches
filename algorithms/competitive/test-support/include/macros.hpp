#pragma once
#include <string>
#include <sstream>
#include <functional>
#include <gtest/gtest.h>

template <typename T, typename... Args>
void macro_test(std::string in, std::string exout, T exret, T (*func)(Args...), Args&&... args) {
    std::istringstream input(in);
    std::streambuf* origCin = std::cin.rdbuf(input.rdbuf());
    std::ostringstream output;
    std::streambuf* origCout = std::cout.rdbuf(output.rdbuf());

    T ret = func(std::forward<Args>(args)...);
    
    EXPECT_EQ(ret, exret);
    EXPECT_EQ(output.str(), exout);

    std::cin.rdbuf(origCin);
    std::cout.rdbuf(origCout);
}