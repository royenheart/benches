#!/bin/bash

    module load nvtools
    if [ ! -f "sparseFFT" ]; then
        # compile
        ./compile.sh
    fi
    # run
    ./sparseFFT $1 $2 $3
