#! /bin/bash

module load xsimd

cd build
cmake ..
make
cp answer ..
cd ..