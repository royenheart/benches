#include <bench/core/io_capture.hpp>
#include <gtest/gtest.h>

#include <iostream>

TEST(IoCapture, CapturesStdinStdoutAndReturnValue) {
    auto [ret, output] = bench::core::run_with_io("41", [] {
        int value = 0;
        std::cin >> value;
        std::cout << value + 1;
        return 7;
    });

    EXPECT_EQ(ret, 7);
    EXPECT_EQ(output, "42");
}
