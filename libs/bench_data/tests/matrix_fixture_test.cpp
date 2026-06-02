#include <bench/data/matrix_fixture.hpp>
#include <bench/linalg/matrix.hpp>
#include <gtest/gtest.h>

#include <filesystem>
#include <random>

TEST(MatrixFixture, RoundTripsBinaryMatrixCase) {
    const auto temp = std::filesystem::temp_directory_path() / "benches-matrix-fixture-test.bin";
    std::mt19937 gen(7);
    auto original = bench::data::make_random_matrix_case(2, 3, 2, gen);

    bench::data::write_matrix_case(temp, original);
    auto loaded = bench::data::read_matrix_case(temp);
    std::filesystem::remove(temp);

    EXPECT_EQ(loaded.a_shape.rows, 2u);
    EXPECT_EQ(loaded.a_shape.cols, 3u);
    EXPECT_EQ(loaded.b_shape.rows, 3u);
    EXPECT_EQ(loaded.b_shape.cols, 2u);
    EXPECT_TRUE(bench::linalg::approximately_equal(loaded.expected, original.expected));
}
