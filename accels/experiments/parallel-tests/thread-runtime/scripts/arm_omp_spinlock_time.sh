#!/bin/bash

function do_sync() {
sudo bash -c "echo 3 > /proc/sys/vm/drop_caches"
sudo sync
sleep 20
}

export OMP_SCHEDULE="auto"
# 同时打印 OMP 和 KMP 设置，方便进行调试
export OMP_DISPLAY_ENV="true"
export KMP_SETTINGS="true"
# 使用紧凑布局并按顺序分配
# - granularity=fine：细粒度绑定
# - compact：线程会尽可能靠近地分配（相邻线程在相邻核心）
# - 1,0：从第一个核心(0)开始按顺序分配
export KMP_AFFINITY=verbose,granularity=fine,compact,1,0
# 显式指定 CPU 也行，proclist 表示将索引 i 的线程绑定到对应的 CPU，需要加上 explicit 指示符号
# export KMP_AFFINITY=verbose,granularity=fine,proclist=[0-63],explicit

module purge
export MODULEPATH=$HOME/envs:$MODULEPATH
module load bisheng/4.2.0.1 kml/2.5.0
# module load openmpi/3.1.6-default perf
WORKSPACE=reports/arm
mkdir -p $WORKSPACE

# ./load_imbalance_test 64 400 500 52000 20

# Block200msWaitActive
do_sync
# Arm not suppport ms / ns identifier
export KMP_BLOCKTIME=200
export OMP_WAIT_POLICY=active
EXP=Block200msWaitActive
mkdir -p $WORKSPACE/$EXP

sar -o $WORKSPACE/$EXP/load_imbalance_sar.dat 1 >/dev/null 2>&1 &
sar_pid=$!
perf record -e '{cycles,instructions}:S' -g -F 667 -C 0-63 -o $WORKSPACE/$EXP/load_imbalance_perf.data -- bash -c "PATH=$PATH LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./bin/arm/load_imbalance_test 64 400 500 52000 20 2>&1 | tee $WORKSPACE/$EXP/load_imbalance_test.log"
kill -9 $sar_pid
LC_ALL='C' sar -A -f $WORKSPACE/$EXP/load_imbalance_sar.dat >$WORKSPACE/$EXP/load_imbalance_sar.txt
# perf script -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.script
# perf report -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.report

# Block100msWaitActive
do_sync
export KMP_BLOCKTIME=100
export OMP_WAIT_POLICY=active
EXP=Block100msWaitActive
mkdir -p $WORKSPACE/$EXP

sar -o $WORKSPACE/$EXP/load_imbalance_sar.dat 1 >/dev/null 2>&1 &
sar_pid=$!
perf record -e '{cycles,instructions}:S' -g -F 667 -C 0-63 -o $WORKSPACE/$EXP/load_imbalance_perf.data -- bash -c "PATH=$PATH LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./bin/arm/load_imbalance_test 64 400 500 52000 20 2>&1 | tee $WORKSPACE/$EXP/load_imbalance_test.log"
kill -9 $sar_pid
LC_ALL='C' sar -A -f $WORKSPACE/$EXP/load_imbalance_sar.dat >$WORKSPACE/$EXP/load_imbalance_sar.txt
# perf script -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.script
# perf report -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.report

# Block50msWaitActive
do_sync
export KMP_BLOCKTIME=50
export OMP_WAIT_POLICY=active
EXP=Block50msWaitActive
mkdir -p $WORKSPACE/$EXP

sar -o $WORKSPACE/$EXP/load_imbalance_sar.dat 1 >/dev/null 2>&1 &
sar_pid=$!
perf record -e '{cycles,instructions}:S' -g -F 667 -C 0-63 -o $WORKSPACE/$EXP/load_imbalance_perf.data -- bash -c "PATH=$PATH LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./bin/arm/load_imbalance_test 64 400 500 52000 20 2>&1 | tee $WORKSPACE/$EXP/load_imbalance_test.log"
kill -9 $sar_pid
LC_ALL='C' sar -A -f $WORKSPACE/$EXP/load_imbalance_sar.dat >$WORKSPACE/$EXP/load_imbalance_sar.txt
# perf script -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.script
# perf report -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.report

# Block10msWaitActive
do_sync
export KMP_BLOCKTIME=10
export OMP_WAIT_POLICY=active
EXP=Block10msWaitActive
mkdir -p $WORKSPACE/$EXP

sar -o $WORKSPACE/$EXP/load_imbalance_sar.dat 1 >/dev/null 2>&1 &
sar_pid=$!
perf record -e '{cycles,instructions}:S' -g -F 667 -C 0-63 -o $WORKSPACE/$EXP/load_imbalance_perf.data -- bash -c "PATH=$PATH LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./bin/arm/load_imbalance_test 64 400 500 52000 20 2>&1 | tee $WORKSPACE/$EXP/load_imbalance_test.log"
kill -9 $sar_pid
LC_ALL='C' sar -A -f $WORKSPACE/$EXP/load_imbalance_sar.dat >$WORKSPACE/$EXP/load_imbalance_sar.txt

# Block200msWaitPassive
do_sync
export KMP_BLOCKTIME=200
export OMP_WAIT_POLICY=passive
EXP=Block200msWaitPassive
mkdir -p $WORKSPACE/$EXP

sar -o $WORKSPACE/$EXP/load_imbalance_sar.dat 1 >/dev/null 2>&1 &
sar_pid=$!
perf record -e '{cycles,instructions}:S' -g -F 667 -C 0-63 -o $WORKSPACE/$EXP/load_imbalance_perf.data -- bash -c "PATH=$PATH LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./bin/arm/load_imbalance_test 64 400 500 52000 20 2>&1 | tee $WORKSPACE/$EXP/load_imbalance_test.log"
kill -9 $sar_pid
LC_ALL='C' sar -A -f $WORKSPACE/$EXP/load_imbalance_sar.dat >$WORKSPACE/$EXP/load_imbalance_sar.txt
# perf script -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.script
# perf report -i $WORKSPACE/$EXP/load_imbalance_perf.data -I --header > $WORKSPACE/$EXP/load_imbalance_perf.report
