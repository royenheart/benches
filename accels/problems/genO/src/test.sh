#!/bin/bash

name=$1

# module load icc/latest mkl/latest
# icpc -Ofast -ffast-math -xHost -std=c++17 -Wall -qopenmp -o answer ./answer.cpp 
# g++ -Ofast -ffast-math -march=native -mtune=native -std=c++17 -Wall -fopenmp -o answer ./answer.cpp 

g++ -O3 -std=c++17 -fopenmp -o answer answer.cpp
g++ -O0 -g -ggdb -std=c++17 -DDebug -fopenmp -o answer.debug answer.cpp

ans1=$(echo "100 322231 123123 12323" > answer.$1.out)
ans1=$(echo "123123123 21312312 213132 213123" > answer.$1.out)