#pragma once

#include <cmath>
#include <cstddef>
#include <stdexcept>
#include <vector>

namespace bench::linalg {

struct MatrixShape {
    std::size_t rows{};
    std::size_t cols{};
};

inline std::size_t offset(MatrixShape shape, std::size_t row, std::size_t col) {
    return row * shape.cols + col;
}

inline std::vector<double> zeros(MatrixShape shape) {
    return std::vector<double>(shape.rows * shape.cols, 0.0);
}

inline std::vector<double> gemm_naive(
    MatrixShape a_shape,
    MatrixShape b_shape,
    const std::vector<double>& a,
    const std::vector<double>& b) {
    if (a_shape.cols != b_shape.rows) {
        throw std::invalid_argument("gemm_naive shape mismatch");
    }
    if (a.size() != a_shape.rows * a_shape.cols || b.size() != b_shape.rows * b_shape.cols) {
        throw std::invalid_argument("gemm_naive data size mismatch");
    }

    std::vector<double> out(a_shape.rows * b_shape.cols, 0.0);
    for (std::size_t i = 0; i < a_shape.rows; ++i) {
        for (std::size_t j = 0; j < b_shape.cols; ++j) {
            for (std::size_t k = 0; k < a_shape.cols; ++k) {
                out[offset({a_shape.rows, b_shape.cols}, i, j)] +=
                    a[offset(a_shape, i, k)] * b[offset(b_shape, k, j)];
            }
        }
    }
    return out;
}

inline bool approximately_equal(
    const std::vector<double>& lhs,
    const std::vector<double>& rhs,
    double epsilon = 1e-4) {
    if (lhs.size() != rhs.size()) {
        return false;
    }
    for (std::size_t i = 0; i < lhs.size(); ++i) {
        if (std::abs(lhs[i] - rhs[i]) > epsilon) {
            return false;
        }
    }
    return true;
}

inline void lu_crout(
    const std::vector<double>& a,
    std::vector<double>& l,
    std::vector<double>& u,
    std::size_t n) {
    if (a.size() != n * n || l.size() != n * n || u.size() != n * n) {
        throw std::invalid_argument("lu_crout expects n by n matrices");
    }

    std::fill(l.begin(), l.end(), 0.0);
    std::fill(u.begin(), u.end(), 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        u[offset({n, n}, i, i)] = 1.0;
    }

    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t j = 0; j < i + 1; ++j) {
            double s = 0.0;
            for (std::size_t k = 0; k < j; ++k) {
                s += l[offset({n, n}, i, k)] * u[offset({n, n}, k, j)];
            }
            l[offset({n, n}, i, j)] = a[offset({n, n}, i, j)] - s;
        }
        for (std::size_t j = i + 1; j < n; ++j) {
            double s = 0.0;
            for (std::size_t k = 0; k < i; ++k) {
                s += l[offset({n, n}, i, k)] * u[offset({n, n}, k, j)];
            }
            u[offset({n, n}, i, j)] =
                (a[offset({n, n}, i, j)] - s) / l[offset({n, n}, i, i)];
        }
    }
}

} // namespace bench::linalg
