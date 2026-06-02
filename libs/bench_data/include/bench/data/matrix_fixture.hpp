#pragma once

#include <bench/linalg/matrix.hpp>

#include <cstddef>
#include <filesystem>
#include <map>
#include <random>
#include <string>
#include <vector>

namespace bench::data {

struct MatrixCase {
    bench::linalg::MatrixShape a_shape;
    bench::linalg::MatrixShape b_shape;
    std::vector<double> a;
    std::vector<double> b;
    std::vector<double> expected;
};

using MatrixGroupKey = std::tuple<std::size_t, std::size_t, std::size_t>;
using MatrixGroups = std::map<MatrixGroupKey, std::vector<std::filesystem::path>>;

MatrixGroups discover_matrix_fixtures(const std::filesystem::path& folder);
MatrixCase read_matrix_case(const std::filesystem::path& file);
void write_matrix_case(const std::filesystem::path& file, const MatrixCase& matrix_case);
MatrixCase make_random_matrix_case(std::size_t m, std::size_t n, std::size_t p, std::mt19937& gen);
std::string matrix_fixture_name(std::size_t m, std::size_t n, std::size_t p, std::size_t index);

} // namespace bench::data
