#pragma once

#include <functional>
#include <ios>
#include <iostream>
#include <sstream>
#include <string>
#include <type_traits>
#include <utility>

namespace bench::core {

class IoCapture {
public:
    explicit IoCapture(std::string input)
        : input_(std::move(input)),
          input_stream_(input_),
          old_cin_(std::cin.rdbuf(input_stream_.rdbuf())),
          old_cout_(std::cout.rdbuf(output_stream_.rdbuf())) {}

    IoCapture(const IoCapture&) = delete;
    IoCapture& operator=(const IoCapture&) = delete;

    ~IoCapture() {
        std::cin.rdbuf(old_cin_);
        std::cout.rdbuf(old_cout_);
    }

    std::string output() const {
        return output_stream_.str();
    }

private:
    std::string input_;
    std::istringstream input_stream_;
    std::ostringstream output_stream_;
    std::streambuf* old_cin_;
    std::streambuf* old_cout_;
};

template <typename Func>
auto run_with_io(std::string input, Func&& func) {
    using ReturnT = decltype(func());
    IoCapture capture(std::move(input));
    if constexpr (std::is_void_v<ReturnT>) {
        func();
        return std::pair<int, std::string>{0, capture.output()};
    } else {
        auto ret = func();
        return std::pair<ReturnT, std::string>{ret, capture.output()};
    }
}

} // namespace bench::core
