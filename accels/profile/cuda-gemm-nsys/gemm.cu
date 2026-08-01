// Naive CUDA GEMM (C = A * B) with NVTX ranges for Nsight Systems.
// Usage: gemm [N] [iters]   (square NxN matrices, default N=1024, iters=10)

#include <cuda_runtime.h>
#include <nvtx3/nvToolsExt.h>

#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <vector>

#define CUDA_CHECK(call)                                                       \
  do {                                                                         \
    cudaError_t err__ = (call);                                                \
    if (err__ != cudaSuccess) {                                                \
      fprintf(stderr, "CUDA error %s:%d: %s\n", __FILE__, __LINE__,            \
              cudaGetErrorString(err__));                                      \
      std::exit(EXIT_FAILURE);                                                 \
    }                                                                          \
  } while (0)

__global__ void gemm_naive(const float *A, const float *B, float *C, int N) {
  int row = blockIdx.y * blockDim.y + threadIdx.y;
  int col = blockIdx.x * blockDim.x + threadIdx.x;
  if (row >= N || col >= N)
    return;

  float sum = 0.0f;
  for (int k = 0; k < N; ++k) {
    sum += A[row * N + k] * B[k * N + col];
  }
  C[row * N + col] = sum;
}

static void fill_matrix(std::vector<float> &m, int seed) {
  srand(static_cast<unsigned>(seed));
  for (size_t i = 0; i < m.size(); ++i) {
    m[i] = static_cast<float>((rand() % 100) / 100.0f);
  }
}

static float checksum(const std::vector<float> &m) {
  double s = 0.0;
  for (float v : m)
    s += v;
  return static_cast<float>(s);
}

int main(int argc, char **argv) {
  int N = 1024;
  int iters = 10;
  if (argc >= 2)
    N = std::atoi(argv[1]);
  if (argc >= 3)
    iters = std::atoi(argv[2]);
  if (N <= 0 || iters <= 0) {
    fprintf(stderr, "Usage: %s [N] [iters]\n", argv[0]);
    return EXIT_FAILURE;
  }

  const size_t bytes = static_cast<size_t>(N) * static_cast<size_t>(N) * sizeof(float);
  const double flops = 2.0 * static_cast<double>(N) * N * N;

  printf("Naive GEMM  N=%d  iters=%d  matrix bytes=%.2f MiB\n", N, iters,
         bytes / (1024.0 * 1024.0));

  std::vector<float> hA(static_cast<size_t>(N) * N);
  std::vector<float> hB(static_cast<size_t>(N) * N);
  std::vector<float> hC(static_cast<size_t>(N) * N, 0.0f);
  fill_matrix(hA, 1);
  fill_matrix(hB, 2);

  float *dA = nullptr, *dB = nullptr, *dC = nullptr;
  CUDA_CHECK(cudaMalloc(&dA, bytes));
  CUDA_CHECK(cudaMalloc(&dB, bytes));
  CUDA_CHECK(cudaMalloc(&dC, bytes));

  {
    nvtxRangePushA("H2D");
    CUDA_CHECK(cudaMemcpy(dA, hA.data(), bytes, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(dB, hB.data(), bytes, cudaMemcpyHostToDevice));
    nvtxRangePop();
  }

  dim3 block(16, 16);
  dim3 grid((N + block.x - 1) / block.x, (N + block.y - 1) / block.y);

  // Warmup (excluded from timed NVTX range)
  {
    nvtxRangePushA("warmup");
    gemm_naive<<<grid, block>>>(dA, dB, dC, N);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaDeviceSynchronize());
    nvtxRangePop();
  }

  cudaEvent_t start, stop;
  CUDA_CHECK(cudaEventCreate(&start));
  CUDA_CHECK(cudaEventCreate(&stop));

  {
    nvtxRangePushA("gemm_iters");
    CUDA_CHECK(cudaEventRecord(start));
    for (int i = 0; i < iters; ++i) {
      char name[64];
      snprintf(name, sizeof(name), "gemm_naive#%d", i);
      nvtxRangePushA(name);
      gemm_naive<<<grid, block>>>(dA, dB, dC, N);
      nvtxRangePop();
    }
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaEventRecord(stop));
    CUDA_CHECK(cudaEventSynchronize(stop));
    nvtxRangePop();
  }

  float ms = 0.0f;
  CUDA_CHECK(cudaEventElapsedTime(&ms, start, stop));
  const float avg_ms = ms / static_cast<float>(iters);
  const double gflops = (flops / (avg_ms * 1e-3)) / 1e9;

  {
    nvtxRangePushA("D2H");
    CUDA_CHECK(cudaMemcpy(hC.data(), dC, bytes, cudaMemcpyDeviceToHost));
    nvtxRangePop();
  }

  printf("avg kernel time: %.3f ms\n", avg_ms);
  printf("throughput:      %.2f GFLOPS\n", gflops);
  printf("C checksum:      %.6f (sanity only)\n", checksum(hC));

  CUDA_CHECK(cudaEventDestroy(start));
  CUDA_CHECK(cudaEventDestroy(stop));
  CUDA_CHECK(cudaFree(dA));
  CUDA_CHECK(cudaFree(dB));
  CUDA_CHECK(cudaFree(dC));
  return EXIT_SUCCESS;
}
