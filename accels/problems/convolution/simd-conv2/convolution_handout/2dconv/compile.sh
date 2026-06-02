#! /bin/bash
sbatch -p compute -q normal -N 1 -n 1 -c 1 -t 2 --job-name=compile_conv --error=error.log --output=output.log compile-job.sh