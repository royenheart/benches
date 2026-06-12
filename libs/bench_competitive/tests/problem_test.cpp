#include <bench/competitive/problem.hpp>
#include <gtest/gtest.h>

#include <cstddef>
#include <iostream>
#include <sstream>
#include <string>

namespace {

int increment_answer() {
    int value = 0;
    std::cin >> value;
    std::cout << value + 1;
    return 7;
}

int quiet_answer() {
    int value = 0;
    std::cin >> value;
    return value;
}

} // namespace

TEST(CompetitiveProblem, RunIoCaseCapturesOutputAndReturnValue) {
    const auto result = bench::competitive::run_io_case("increment", "41", "42",
                                                        7, increment_answer);

    EXPECT_EQ(result.name, "increment");
    EXPECT_EQ(result.actual_return, 7);
    EXPECT_EQ(result.expected_return, 7);
    EXPECT_EQ(result.actual_output, "42");
    EXPECT_EQ(result.expected_output, "42");
    EXPECT_TRUE(result.passed());
}

TEST(CompetitiveProblem, RunValueCaseComparesExpressionResult) {
    const auto result =
        bench::competitive::run_value_case("value", [] { return 21 * 2; }, 42);

    EXPECT_EQ(result.name, "value");
    EXPECT_EQ(result.actual_value, 42);
    EXPECT_EQ(result.expected_value, 42);
    EXPECT_TRUE(result.passed());
}

TEST(CompetitiveProblem, PerformanceRegistryRunsCapturedCases) {
    bench::competitive::clear_performance_cases();

    bench::competitive::register_performance_case("quiet", quiet_answer, "11",
                                                  3);

    EXPECT_EQ(bench::competitive::performance_case_count(), std::size_t{1});

    std::ostringstream report;
    const auto summary = bench::competitive::run_performance_cases(report);

    EXPECT_EQ(summary.cases_run, std::size_t{1});
    EXPECT_EQ(summary.total_iterations, std::size_t{3});
    EXPECT_NE(report.str().find("quiet"), std::string::npos);
    EXPECT_NE(report.str().find("iterations=3"), std::string::npos);

    bench::competitive::clear_performance_cases();
}
