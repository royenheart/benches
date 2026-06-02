#pragma once

#include <cuda_runtime.h>

namespace bench::cuda {

class EventTimer {
public:
    EventTimer() {
        cudaEventCreate(&start_);
        cudaEventCreate(&stop_);
    }

    EventTimer(const EventTimer&) = delete;
    EventTimer& operator=(const EventTimer&) = delete;

    ~EventTimer() {
        cudaEventDestroy(start_);
        cudaEventDestroy(stop_);
    }

    void start() {
        cudaEventRecord(start_, 0);
    }

    float stop_milliseconds() {
        cudaEventRecord(stop_, 0);
        cudaEventSynchronize(stop_);
        float elapsed = 0.0f;
        cudaEventElapsedTime(&elapsed, start_, stop_);
        return elapsed;
    }

private:
    cudaEvent_t start_{};
    cudaEvent_t stop_{};
};

} // namespace bench::cuda
