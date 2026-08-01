#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

N="${1:-1024}"
ITERS="${2:-10}"

if [[ ! -x ./gemm ]]; then
  echo "gemm not found. Run ./build.sh or make first."
  exit 1
fi

nsys profile -o gemm_report -f true --stats=true \
  --trace=cuda,nvtx,osrt \
  ./gemm "$N" "$ITERS"

echo
echo "Report: gemm_report.nsys-rep"
echo "Open with: nsys-ui gemm_report.nsys-rep"
