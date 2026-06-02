#!/bin/bash

function do_sync() {
sudo bash -c "echo 3 > /proc/sys/vm/drop_caches"
sudo sync
sleep 20
}

# export OMP_PROC_BIND=true
# export OMP_PLACES=cores
export OMP_SCHEDULE="auto"
export OMP_DISPLAY_ENV="true"
export KMP_SETTINGS="true"
# 使用紧凑布局并按顺序分配
# - granularity=fine：细粒度绑定
# - compact：线程会尽可能靠近地分配（相邻线程在相邻核心）
# - 1,0：从第一个核心(0)开始按顺序分配
export KMP_AFFINITY=granularity=fine,compact,1,0

module purge
module load compiler/2025.1.0 mpi/2021.15 mkl/2025.1 perf
WORKSPACE=reports/intel
mkdir -p $WORKSPACE

# Block200msWaitActive
do_sync
export KMP_BLOCKTIME=200ms
export OMP_WAIT_POLICY=active
EXP=Block200msWaitActive
mkdir -p $WORKSPACE/$EXP

sar -o $WORKSPACE/$EXP/load_imbalance_sar.dat 1 >/dev/null 2>&1 &
sar_pid=$!
perf record -e '{cycles,instructions}:S' -g -F 667 -C 0-79 -o $WORKSPACE/$EXP/load_imbalance_perf.data -- bash -c "./bin/intel/load_imbalance_test 80 400 1000 89991 20 2>&1 | tee $WORKSPACE/$EXP/load_imbalance_test.log"
kill -9 $sar_pid
LC_ALL='C' sar -A -f $WORKSPACE/$EXP/load_imbalance_sar.dat >$WORKSPACE/$EXP/load_imbalance_sar.txt
# perf script -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.script
# perf report -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.report

# Block100msWaitActive
do_sync
export KMP_BLOCKTIME=100ms
export OMP_WAIT_POLICY=active
EXP=Block100msWaitActive
mkdir -p $WORKSPACE/$EXP

sar -o $WORKSPACE/$EXP/load_imbalance_sar.dat 1 >/dev/null 2>&1 &
sar_pid=$!
perf record -e '{cycles,instructions}:S' -g -F 667 -C 0-79 -o $WORKSPACE/$EXP/load_imbalance_perf.data -- bash -c "./bin/intel/load_imbalance_test 80 400 1000 89991 20 2>&1 | tee $WORKSPACE/$EXP/load_imbalance_test.log"
kill -9 $sar_pid
LC_ALL='C' sar -A -f $WORKSPACE/$EXP/load_imbalance_sar.dat >$WORKSPACE/$EXP/load_imbalance_sar.txt
# perf script -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.script
# perf report -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.report

# Block50usWaitActive
do_sync
export KMP_BLOCKTIME=50us
export OMP_WAIT_POLICY=active
EXP=Block50usWaitActive
mkdir -p $WORKSPACE/$EXP

sar -o $WORKSPACE/$EXP/load_imbalance_sar.dat 1 >/dev/null 2>&1 &
sar_pid=$!
perf record -e '{cycles,instructions}:S' -g -F 667 -C 0-79 -o $WORKSPACE/$EXP/load_imbalance_perf.data -- bash -c "./bin/intel/load_imbalance_test 80 400 1000 89991 20 2>&1 | tee $WORKSPACE/$EXP/load_imbalance_test.log"
kill -9 $sar_pid
LC_ALL='C' sar -A -f $WORKSPACE/$EXP/load_imbalance_sar.dat >$WORKSPACE/$EXP/load_imbalance_sar.txt
# perf script -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.script
# perf report -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.report

# Block200msWaitPassive
do_sync
export KMP_BLOCKTIME=200ms
export OMP_WAIT_POLICY=passive
EXP=Block200msWaitPassive
mkdir -p $WORKSPACE/$EXP

sar -o $WORKSPACE/$EXP/load_imbalance_sar.dat 1 >/dev/null 2>&1 &
sar_pid=$!
perf record -e '{cycles,instructions}:S' -g -F 667 -C 0-79 -o $WORKSPACE/$EXP/load_imbalance_perf.data -- bash -c "./bin/intel/load_imbalance_test 80 400 1000 89991 20 2>&1 | tee $WORKSPACE/$EXP/load_imbalance_test.log"
kill -9 $sar_pid
LC_ALL='C' sar -A -f $WORKSPACE/$EXP/load_imbalance_sar.dat >$WORKSPACE/$EXP/load_imbalance_sar.txt
# perf script -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.script
# perf report -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.report
