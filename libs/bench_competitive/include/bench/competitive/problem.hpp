#pragma once

#include <bench/competitive/binary_tree.hpp>
#include <bench/competitive/debug_print.hpp>
#include <bench/competitive/linked_list.hpp>
#include <bench/core/io_capture.hpp>
#include <bench/timing/timer.hpp>

#include <cstddef>
#include <functional>
#include <iostream>
#include <ostream>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

#if defined(BENCH_COMPETITIVE_BUILD_TEST)
#include <gtest/gtest.h>
#endif

namespace bench::competitive {

template <typename ReturnT> struct IoCaseResult {
    std::string name;
    ReturnT actual_return;
    ReturnT expected_return;
    std::string actual_output;
    std::string expected_output;

    bool passed() const {
        return actual_return == expected_return &&
               actual_output == expected_output;
    }
};

template <typename ActualT, typename ExpectedT> struct ValueCaseResult {
    std::string name;
    ActualT actual_value;
    ExpectedT expected_value;

    bool passed() const { return actual_value == expected_value; }
};

struct PerformanceSummary {
    std::size_t cases_run = 0;
    std::size_t total_iterations = 0;
    double total_seconds = 0.0;
};

template <typename Func, typename ExpectedReturn>
auto run_io_case(std::string name, std::string input,
                 std::string expected_output, ExpectedReturn expected_return,
                 Func&& func) {
    auto [actual_return, actual_output] =
        bench::core::run_with_io(std::move(input), std::forward<Func>(func));
    using ReturnT = std::decay_t<decltype(actual_return)>;

    return IoCaseResult<ReturnT>{
        std::move(name), actual_return, static_cast<ReturnT>(expected_return),
        std::move(actual_output), std::move(expected_output)};
}

template <typename Func, typename ExpectedT>
auto run_value_case(std::string name, Func&& func, ExpectedT&& expected) {
    auto actual = std::forward<Func>(func)();
    using ActualT = std::decay_t<decltype(actual)>;
    using StoredExpectedT = std::decay_t<ExpectedT>;

    return ValueCaseResult<ActualT, StoredExpectedT>{
        std::move(name),
        std::move(actual),
        std::forward<ExpectedT>(expected),
    };
}

namespace detail {

struct PerformanceCase {
    std::string name;
    std::size_t iterations;
    std::function<void()> run_once;
};

inline std::vector<PerformanceCase>& performance_registry() {
    static std::vector<PerformanceCase> cases;
    return cases;
}

} // namespace detail

inline void clear_performance_cases() {
    detail::performance_registry().clear();
}

inline std::size_t performance_case_count() {
    return detail::performance_registry().size();
}

template <typename Func>
bool register_performance_case(std::string name, Func&& func, std::string input,
                               std::size_t iterations) {
    auto runner = [captured_input = std::move(input),
                   captured_func = std::forward<Func>(func)]() mutable {
        bench::core::run_with_io(captured_input, captured_func);
    };

    detail::performance_registry().push_back(detail::PerformanceCase{
        std::move(name),
        iterations,
        std::move(runner),
    });
    return true;
}

inline PerformanceSummary
run_performance_cases(std::ostream& output = std::cout) {
    PerformanceSummary summary;
    auto& cases = detail::performance_registry();
    if (cases.empty()) {
        output << "no performance cases\n";
        return summary;
    }

    for (auto& perf_case : cases) {
        bench::timing::WallTimer timer;
        for (std::size_t i = 0; i < perf_case.iterations; ++i) {
            perf_case.run_once();
        }
        const double seconds = timer.elapsed_seconds();
        summary.cases_run += 1;
        summary.total_iterations += perf_case.iterations;
        summary.total_seconds += seconds;

        const double average =
            perf_case.iterations == 0
                ? 0.0
                : seconds / static_cast<double>(perf_case.iterations);
        output << perf_case.name << ": iterations=" << perf_case.iterations
               << " total_seconds=" << seconds << " avg_seconds=" << average
               << '\n';
    }

    return summary;
}

} // namespace bench::competitive

#define BENCH_COMPETITIVE_DETAIL_CONCAT_INNER(lhs, rhs) lhs##rhs
#define BENCH_COMPETITIVE_DETAIL_CONCAT(lhs, rhs)                              \
    BENCH_COMPETITIVE_DETAIL_CONCAT_INNER(lhs, rhs)
#define BENCH_COMPETITIVE_DETAIL_TEST_NAME(line)                               \
    BENCH_COMPETITIVE_DETAIL_CONCAT(Case_, line)

#if defined(BENCH_COMPETITIVE_BUILD_TEST)

/// Defines the normal executable entry point for this problem file.
/// In test builds this is disabled because xmake links gtest_main.
/// \param func A no-argument callable, typically answer().
#define BENCH_COMPETITIVE_MAIN(func)

/// Registers an input/output correctness test for an OJ-style solution.
/// Runs func() with case_input redirected to std::cin, captures std::cout, and
/// compares both stdout and the return value.
/// \param case_name Test label shown by gtest through SCOPED_TRACE.
/// \param case_input Input text fed to std::cin.
/// \param case_output Expected stdout text.
/// \param case_return Expected return value from func().
/// \param func A no-argument callable, typically answer().
#define BENCH_IO_TEST(case_name, case_input, case_output, case_return, func)   \
    TEST(BenchCompetitiveIo, BENCH_COMPETITIVE_DETAIL_TEST_NAME(__LINE__)) {   \
        SCOPED_TRACE(case_name);                                               \
        const auto result = ::bench::competitive::run_io_case(                 \
            case_name, case_input, case_output, case_return, func);            \
        EXPECT_EQ(result.actual_return, result.expected_return);               \
        EXPECT_EQ(result.actual_output, result.expected_output);               \
    }

/// Registers a value correctness test for API-style solutions.
/// Evaluates expression once and compares it with case_expected_value.
/// Prefer a no-argument wrapper, such as fast_case(), when the call expression
/// contains commas or when comparing several implementations.
/// \param case_name Test label shown by gtest through SCOPED_TRACE.
/// \param expression Expression to evaluate.
/// \param case_expected_value Expected value.
#define BENCH_VALUE_TEST(case_name, expression, case_expected_value)           \
    TEST(BenchCompetitiveValue,                                                \
         BENCH_COMPETITIVE_DETAIL_TEST_NAME(__LINE__)) {                       \
        SCOPED_TRACE(case_name);                                               \
        const auto result = ::bench::competitive::run_value_case(              \
            case_name, [&] { return (expression); }, case_expected_value);     \
        EXPECT_EQ(result.actual_value, result.expected_value);                 \
    }

/// Registers a wall-clock benchmark case.
/// In test builds this is intentionally disabled.
/// \param name Benchmark label.
/// \param func A no-argument callable.
/// \param input Input text fed to std::cin for each iteration.
/// \param iterations Number of repeated runs.
#define BENCH_PERF_TEST(name, func, input, iterations)

#elif defined(BENCH_COMPETITIVE_BUILD_BENCH)

/// Defines the benchmark executable entry point for this problem file.
/// In benchmark builds it runs all BENCH_PERF_TEST cases registered in the
/// file.
/// \param func Accepted for source compatibility with the normal executable.
#define BENCH_COMPETITIVE_MAIN(func)                                           \
    int main() {                                                               \
        ::bench::competitive::run_performance_cases(std::cout);                \
        return 0;                                                              \
    }

/// Registers an input/output correctness test for an OJ-style solution.
/// In benchmark builds this is disabled; use BENCH_PERF_TEST for timing.
/// \param name Test label.
/// \param input Input text.
/// \param expected_output Expected stdout text.
/// \param expected_return Expected return value.
/// \param func A no-argument callable.
#define BENCH_IO_TEST(name, input, expected_output, expected_return, func)

/// Registers a value correctness test for API-style solutions.
/// In benchmark builds this is disabled; use BENCH_PERF_TEST for timing.
/// \param name Test label.
/// \param expression Expression to evaluate.
/// \param expected_value Expected value.
#define BENCH_VALUE_TEST(name, expression, expected_value)

/// Registers a no-argument callable for repeated wall-clock timing.
/// input is redirected to std::cin for each iteration. To compare several
/// implementations, add one BENCH_PERF_TEST per implementation with the same
/// input and iterations, then run algo_<file>_bench.
/// \param name Benchmark label.
/// \param func A no-argument callable.
/// \param input Input text fed to std::cin for each iteration, or "" for no IO.
/// \param iterations Number of repeated runs.
#define BENCH_PERF_TEST(name, func, input, iterations)                         \
    namespace {                                                                \
    const bool BENCH_COMPETITIVE_DETAIL_CONCAT(bench_competitive_perf_case_,   \
                                               __LINE__) =                     \
        ::bench::competitive::register_performance_case(                       \
            name, func, input, static_cast<std::size_t>(iterations));          \
    }

#else

/// Defines the normal executable entry point for this problem file.
/// Expands to int main() { return func(); }.
/// \param func A no-argument callable, typically answer().
#define BENCH_COMPETITIVE_MAIN(func)                                           \
    int main() { return (func)(); }

/// Registers an input/output correctness test for an OJ-style solution.
/// In normal builds this is disabled, so the file remains submission-friendly.
/// \param name Test label.
/// \param input Input text.
/// \param expected_output Expected stdout text.
/// \param expected_return Expected return value.
/// \param func A no-argument callable.
#define BENCH_IO_TEST(name, input, expected_output, expected_return, func)

/// Registers a value correctness test for API-style solutions.
/// In normal builds this is disabled, so the file remains submission-friendly.
/// \param name Test label.
/// \param expression Expression to evaluate.
/// \param expected_value Expected value.
#define BENCH_VALUE_TEST(name, expression, expected_value)

/// Registers a wall-clock benchmark case.
/// In normal builds this is disabled; use the generated algo_<file>_bench
/// target.
/// \param name Benchmark label.
/// \param func A no-argument callable.
/// \param input Input text fed to std::cin for each iteration.
/// \param iterations Number of repeated runs.
#define BENCH_PERF_TEST(name, func, input, iterations)

#endif
