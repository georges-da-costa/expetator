#!/bin/bash

function wl_cpu() {

  step=25            # increment step (%)
  ubenchs=( 'ub_cpu_cu' 'ub_cpu_alu' 'ub_cpu_rand' )

  # idle power in CX
  sleep $TIME

  # idle power in C0
  sudo ${SHARED_PATH}/bin/setcpulatency 0 &
  sleep $TIME
  sudo killall setcpulatency

  # Collect CPU stressed power for each ubench
  for b in ${ubenchs[@]}; do
    echo "bench: $b"
    for ((c=0; c<$cpus; c++)); do
      ${SHARED_PATH}/bin/$b &> /dev/null &
      pid=$!
      for ((l=$step; l<100; l+=$step)); do
        cpulimit -p $pid -l $l &> /dev/null &
        sleep $TIME
        killall cpulimit
      done
      sleep $TIME
    done
    killall $b &> /dev/null
  done
}

function wl_mem() {
  mem_id=('2' '3' '4')
  op_id=('1' '2')

  for ((c=0; c<$cpus; c++)); do
    for m in ${mem_id[@]}; do
      for o in ${op_id[@]}; do
        ${SHARED_PATH}/bin/ub_mem_access $m 0 $o &
        PID=$!
  	taskset -c -p ${c} ${PID} &> /dev/null &
        sleep $TIME
        killall ub_mem_access &> /dev/null
      done
    done
  done
}

function wl_nic_start() {
  # Start iperf server in the front end node
  oarsh ${REMOTE_HOST} "iperf3 -s &> /dev/null &"
}

function wl_nic_stop() {
  # Stop local and remote jobs
  oarsh ${REMOTE_HOST} "killall iperf3"
}

function wl_nic() {
    wl_nic_start
    
    band=('200' '400' '1000')
    for b in ${band[@]}; do
	# download
	iperf3 -R -c ${REMOTE_HOST} -t $TIME -b ${b}M &> /dev/null

	# upload
	iperf3 -c ${REMOTE_HOST} -t $TIME -b ${b}M &> /dev/null
    done

    wl_nic_stop
}

function wl_max() {
  wl_nic_start

  TIME2=`expr 3 \* $TIME`

  ## Start Benchs
  # CPU stress
  for ((c=0; c<$cpus; c++)); do
    ${SHARED_PATH}/bin/ub_cpu_rand &
  done

  # Cache L3 and RAM Write Accesses
  ${SHARED_PATH}/bin/ub_mem_access 3 0 1 &
  ${SHARED_PATH}/bin/ub_mem_access 4 0 1 &

  # No latency (C0)
  sudo ${SHARED_PATH}/bin/setcpulatency 0 &
  
  # Start network transactions and collect power measurements
  iperf3 -R -c ${REMOTE_HOST} -t $TIME2 -b 1000M &> /dev/null

  ## Cleanup
  # Stop remote server
  wl_nic_stop

  # Stop CPU stress
  killall ub_cpu_rand ub_cpu_alu ub_cpu_fpu ub_cpu_cu

  # Stop Memory stress
  killall ub_mem_access

  # Stop C-state
  sudo killall setcpulatency
}

function main() {
  # CPU intensive
  wl_cpu 

  # Memory and CPU intensive
  wl_mem

  # Network intensive
  wl_nic

  # All together
  wl_max
}

# global variables
cpus=`cat /proc/cpuinfo | grep processor | wc -l`  # Get number of processor's cores

TIME=$1

SHARED_PATH=/tmp/

REMOTE_HOST=$2


main
