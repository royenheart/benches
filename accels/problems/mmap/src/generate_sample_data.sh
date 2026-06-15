#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

g++ -O2 -Wall -std=c++17 data_gen.cpp -o data_gen_cpp
./data_gen_cpp input.bin 4 12 0
printf 'generated input.bin with 4096 integers\n'
