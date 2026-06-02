#include <bench/data/matrix_fixture.hpp>

#include <fstream>
#include <regex>
#include <stdexcept>

namespace bench::data {

namespace {

void read_exact(std::ifstream& stream, char* data, std::streamsize size) {
    stream.read(data, size);
    if (stream.gcount() != size) {
        throw std::runtime_error("short read while loading matrix fixture");
    }
}

void write_vector(std::ofstream& stream, const std::vector<double>& values) {
    stream.write(reinterpret_cast<const char*>(values.data()),
                 static_cast<std::streamsize>(values.size() * sizeof(double)));
}

std::vector<double> read_vector(std::ifstream& stream, std::size_t count) {
    std::vector<double> values(count);
    read_exact(stream,
               reinterpret_cast<char*>(values.data()),
               static_cast<std::streamsize>(values.size() * sizeof(double)));
    return values;
}

} // namespace

MatrixGroups discover_matrix_fixtures(const std::filesystem::path& folder) {
    if (!std::filesystem::is_directory(folder)) {
        throw std::runtime_error("matrix fixture folder does not exist: " + folder.string());
    }

    MatrixGroups groups;
    const std::regex pattern(R"(matrix-([0-9]+)-([0-9]+)-([0-9]+)\.([0-9]+)\.bin)");
    for (const auto& entry : std::filesystem::directory_iterator(folder)) {
        if (!entry.is_regular_file()) {
            continue;
        }
        std::smatch matches;
        const auto filename = entry.path().filename().string();
        if (!std::regex_match(filename, matches, pattern)) {
            continue;
        }
        const auto m = static_cast<std::size_t>(std::stoull(matches[1]));
        const auto n = static_cast<std::size_t>(std::stoull(matches[2]));
        const auto p = static_cast<std::size_t>(std::stoull(matches[3]));
        groups[MatrixGroupKey{m, n, p}].push_back(entry.path());
    }
    return groups;
}

MatrixCase read_matrix_case(const std::filesystem::path& file) {
    std::ifstream input(file, std::ios::binary);
    if (!input) {
        throw std::runtime_error("cannot open matrix fixture: " + file.string());
    }

    std::size_t sizes[3]{};
    read_exact(input, reinterpret_cast<char*>(sizes), sizeof(sizes));
    const auto m = sizes[0];
    const auto n = sizes[1];
    const auto p = sizes[2];

    MatrixCase matrix_case;
    matrix_case.a_shape = {m, n};
    matrix_case.b_shape = {n, p};
    matrix_case.a = read_vector(input, m * n);
    matrix_case.b = read_vector(input, n * p);
    matrix_case.expected = read_vector(input, m * p);
    return matrix_case;
}

void write_matrix_case(const std::filesystem::path& file, const MatrixCase& matrix_case) {
    std::filesystem::create_directories(file.parent_path());
    std::ofstream output(file, std::ios::binary);
    if (!output) {
        throw std::runtime_error("cannot write matrix fixture: " + file.string());
    }

    const std::size_t sizes[3]{
        matrix_case.a_shape.rows,
        matrix_case.a_shape.cols,
        matrix_case.b_shape.cols,
    };
    output.write(reinterpret_cast<const char*>(sizes), sizeof(sizes));
    write_vector(output, matrix_case.a);
    write_vector(output, matrix_case.b);
    write_vector(output, matrix_case.expected);
}

MatrixCase make_random_matrix_case(std::size_t m, std::size_t n, std::size_t p, std::mt19937& gen) {
    std::uniform_real_distribution<double> values(-100.0, 100.0);
    MatrixCase matrix_case;
    matrix_case.a_shape = {m, n};
    matrix_case.b_shape = {n, p};
    matrix_case.a.resize(m * n);
    matrix_case.b.resize(n * p);
    for (double& value : matrix_case.a) {
        value = values(gen);
    }
    for (double& value : matrix_case.b) {
        value = values(gen);
    }
    matrix_case.expected = bench::linalg::gemm_naive(matrix_case.a_shape, matrix_case.b_shape,
                                                     matrix_case.a, matrix_case.b);
    return matrix_case;
}

std::string matrix_fixture_name(std::size_t m, std::size_t n, std::size_t p, std::size_t index) {
    return "matrix-" + std::to_string(m) + "-" + std::to_string(n) + "-" +
           std::to_string(p) + "." + std::to_string(index) + ".bin";
}

} // namespace bench::data
