#!/bin/bash

# check if hostname begin with "gpu" with regular expression

if [[ $(hostname) =~ ^gpu.* ]]; then
    # if yes, run the following command
    echo "This script is running on a GPU machine"
    module load nvtools
    if [ -d "build" ] ; then
        rm -rf build
    fi
    mkdir build
    cd build
    cmake ..
    make
    cp sparseFFT ../
    cd ..
else
    # if no, run the following command
    echo "This script must be run on a GPU machine"
fi