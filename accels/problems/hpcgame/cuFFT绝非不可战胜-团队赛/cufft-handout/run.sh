#!/bin/bash

sbatch -p GPU --gres=gpu:1 --gpus=1 -t 00:20:00 -o output.txt -e error.txt run-job.sh $1 $2 $3