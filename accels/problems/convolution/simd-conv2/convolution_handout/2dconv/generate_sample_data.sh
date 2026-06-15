#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

g++ -O2 -Wall -std=c++17 generate_conv_case.cpp -o generate_conv_case

case_dir="../../sample_data/conv_test_cases/32x32_4x4_seed0"
./generate_conv_case "$case_dir" 32 32 4 4 0
printf 'generated %s\n' "$case_dir"
