#!/bin/bash

module load mpi/2021.8.0

export I_MPI_PIN_RESPECT_CPUSET=0;
# mpirun ./cpi
I_MPI_OFI_PROVIDER=tcp mpirun -genv I_MPI_FABRICS=shm:ofi -iface eno2 ./cpi