/**
 * @file rayTracing.cpp
 * @brief 测试三种情况：1. 在GPU直接开辟内存使用（非静态，全局内存） 2. 常量内存
 * @version 0.1
 * @date 2022-08-08
 * 
 */

#include <hip/hip_runtime.h>
#include <opencv2/opencv.hpp>
#include <cstdlib>
#include <iostream>
#include <ctime>

#define INF 2e10f
#define rnd(x) (x * rand() / RAND_MAX)
#define SPHERES 200
#define DIM 1024

struct sphere {
    float r, g, b;
    float radius;
    float x, y, z;
    __device__ float hit(float ox, float oy, float *n) {
        float dx = ox - x;
        float dy = oy - y;
        if (dx * dx + dy * dy < radius * radius) {
            float dz = sqrtf(radius * radius - dx * dx - dy * dy);
            *n = dz / sqrtf(radius * radius);
            return dz + z;
        }
        return -INF;
    }
};

// __constant__ sphere s[SPHERES];

__global__ void kernel(sphere *s, unsigned char *ptr) {
    int x = hipThreadIdx_x + hipBlockIdx_x * hipBlockDim_x;
    int y = hipThreadIdx_y + hipBlockIdx_y * hipBlockDim_y;
    int offset = x + y * hipBlockDim_x * hipGridDim_x;
    float ox = x - DIM / 2;
    float oy = y - DIM / 2;

    float maxz = -INF;
    float r = 0, g = 0, b = 0;
    for (int i = 0; i < SPHERES; i++) {
        float n;
        float z = s[i].hit(ox, oy, &n);
        if (z > maxz) {
            float fscale = n;
            r = s[i].r * fscale;
            g = s[i].g * fscale;
            b = s[i].b * fscale;
            maxz = z;
        }
    }

    ptr[offset * 4 + 0] = (int)(r * 255);
    ptr[offset * 4 + 1] = (int)(g * 255);
    ptr[offset * 4 + 2] = (int)(b * 255);
    ptr[offset * 4 + 3] = 255;
}

int main(int argc, char **argv) {
    sphere *s;

    srand(time(NULL));

    hipEvent_t start, stop;
    hipEventCreate(&start);
    hipEventCreate(&stop);
    hipEventRecord(start, 0);

    cv::Mat image(DIM, DIM, CV_8UC4);
    unsigned char *dev_bitmap;

    hipMalloc((void**)&dev_bitmap, image.total() * image.elemSize());
    hipMalloc((void**)&s, sizeof(sphere) * SPHERES);

    sphere* temp_s = (sphere*)malloc(sizeof(sphere) * SPHERES);
    for (int i = 0; i < SPHERES; i++) {
        temp_s[i].r = rnd(1.0f);
        temp_s[i].g = rnd(1.0f);
        temp_s[i].b = rnd(1.0f);
        temp_s[i].x = rnd(1000.0f) - 500;
        temp_s[i].y = rnd(1000.0f) - 500;
        temp_s[i].z = rnd(1000.0f) - 500;
        temp_s[i].radius = rnd(100.0f) + 20;
    }

    hipMemcpy(s, temp_s, sizeof(sphere) * SPHERES, hipMemcpyHostToDevice);
    free(temp_s);

    dim3 grids(DIM / 16, DIM / 16);
    dim3 threads(16, 16);
    hipLaunchKernelGGL(kernel, grids, threads, 0, 0, s, dev_bitmap);

    hipMemcpy(image.ptr(), dev_bitmap, image.total() * image.elemSize(), hipMemcpyDeviceToHost);

    hipEventRecord(stop, 0);
    hipEventSynchronize(stop);
    float elapsedTime;
    hipEventElapsedTime(&elapsedTime, start, stop);
    printf("Time to generate: %3.6f ms\n", elapsedTime);
    hipEventDestroy(start);
    hipEventDestroy(stop);

    cv::imshow("Ray Tracing", image);
    cv::waitKey(0);

    hipFree(s);
    hipFree(dev_bitmap);

    return 0;
}
