#!/bin/bash

function GameLife_nvc() {
	# nvc++ -g -O0 -I/home/royenheart/softwares/opencv-4.6.0/include/opencv4 -I/home/royenheart/softwares/opencv-4.6.0/include/opencv4/opencv2 -I./src -L/home/royenheart/softwares/opencv-4.6.0/lib -lopencv_core -lopencv_highgui -lopencv_imgproc -o ./out/GameLife_nvcc -std=c++17 -L/lib/x86_64-linux-gnu -lcudart ./src/GameLife.cu ./src/image.cpp

	# using NVIDIA HPC SDK cuda runtime
	nvc++ -g -O0 -I/home/royenheart/softwares/opencv-4.6.0/include/opencv4 -I/home/royenheart/softwares/opencv-4.6.0/include/opencv4/opencv2 -I./src -L/home/royenheart/softwares/opencv-4.6.0/lib -lopencv_core -lopencv_highgui -lopencv_imgproc -o ./out/GameLife_nvcc -std=c++17 -L$NVHPC_ROOT/cuda/lib64/ -lcudart ./src/GameLife.cu ./src/image.cu

	rm -f ./*.o
}

function GameLife_clang() {
	# --cuda-compile-host-device --cuda-gpu-arch=sm_70
	# clang++-16 -g -O0 -I/home/royenheart/softwares/opencv-4.6.0/include/opencv4 -I/home/royenheart/softwares/opencv-4.6.0/include/opencv4/opencv2 -I./src -L/home/royenheart/softwares/opencv-4.6.0/lib -lopencv_core -lopencv_highgui -lopencv_imgproc --cuda-compile-host-device --cuda-gpu-arch=sm_70 -o ./out/GameLife_clang -std=c++17 -L/lib/x86_64-linux-gnu -lcudart ./src/GameLife.cu ./src/image.cpp

	# using NVIDIA HPC SDK cuda runtime
	clang++-16 -g -O0 -I/home/royenheart/softwares/opencv-4.6.0/include/opencv4 -I/home/royenheart/softwares/opencv-4.6.0/include/opencv4/opencv2 -I./src -L/home/royenheart/softwares/opencv-4.6.0/lib -lopencv_core -lopencv_highgui -lopencv_imgproc --cuda-compile-host-device --cuda-gpu-arch=sm_70 -o ./out/GameLife_clang -std=c++17 -L$NVHPC_ROOT/cuda/lib64/ -lcudart ./src/GameLife.cu ./src/image.cu

	rm -f ./*.o
}

function cudaMultiStream_nvc() {
	# nvc++ -g -O0 -I./src -o ./out/cudaMultiStream_nvc -std=c++17 -L/lib/x86_64-linux-gnu -lcudart ./src/cudaMultiStream.cu

	# using NVIDIA HPC SDK cuda runtime
	nvc++ -g -O0 -I./src -o ./out/cudaMultiStream_nvc -std=c++17 -L$NVHPC_ROOT/cuda/lib64/ -lcudart ./src/cudaMultiStream.cu

	rm -f ./*.o
}

function caustics() {
	nvc++ -O3 -o ./out/caustics -L$NVHPC_ROOT/cuda/lib64/ -lcudart ./src/caustics.cu
}

# GameLife_nvc
# GameLife_clang
# cudaMultiStream_nvc
caustics