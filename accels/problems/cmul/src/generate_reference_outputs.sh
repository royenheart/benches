#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ "$#" -eq 0 ]; then
  set -- 1x1x1 2x2x2 10x10x10
fi

g++ -O2 -Wall -std=c++17 gen_matrix.cpp rhs.cpp -lm -o gen_matrix
mkdir -p rights

for shape in "$@"; do
  IFS=x read -r n1 n2 n3 <<< "$shape"
  if [ -z "${n1:-}" ] || [ -z "${n2:-}" ] || [ -z "${n3:-}" ]; then
    printf 'invalid shape %s; expected N1xN2xN3\n' "$shape" >&2
    exit 2
  fi
  ./gen_matrix "$n1" "$n2" "$n3"
  mv right.dat "rights/right.${n1}.${n2}.${n3}.dat"
done
