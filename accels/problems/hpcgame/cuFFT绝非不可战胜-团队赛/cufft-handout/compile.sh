#!/bin/bash

sbatch -p GPU --gres=gpu:1 --gpus=1 -t 00:00:30 -o output.txt -e error.txt compile-job.sh
