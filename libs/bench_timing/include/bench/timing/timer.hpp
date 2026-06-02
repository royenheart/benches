#pragma once

#include <chrono>

namespace bench::timing {

class WallTimer {
public:
    WallTimer() : start_(Clock::now()) {}

    double elapsed_seconds() const {
        return std::chrono::duration<double>(Clock::now() - start_).count();
    }

private:
    using Clock = std::chrono::steady_clock;
    Clock::time_point start_;
};

} // namespace bench::timing
