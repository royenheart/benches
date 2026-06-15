#!/bin/bash
module load mpi/2021.8.0
mpicc cpi.c -lm -o cpi
