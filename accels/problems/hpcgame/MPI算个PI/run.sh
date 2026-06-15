#!/bin/bash
#run.sh
sbatch --cpus-per-task=1 --nodes=5 --ntasks-per-node=2 --partition=compute --qos=normal --output=output.txt ./job.sh