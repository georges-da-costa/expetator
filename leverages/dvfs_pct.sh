#!/bin/bash

# manager.sh
hostname

SUDO=sudo

if [[ `hostname` == *grid5000.fr ]]
then
    SUDO=sudo-g5k
fi

set_freq () {
        echo $FREQ | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_max_freq
#        echo $FREQ | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_min_freq
#        echo $FREQ | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_max_freq
}

init() {
    GROUP=`groups | cut -f 1 -d ' '`
    if [ ! -w /sys/devices/system/cpu/intel_pstate/no_turbo ]
    then
	${SUDO} chmod g+w /sys/devices/system/cpu/intel_pstate/no_turbo
	${SUDO} chgrp $GROUP /sys/devices/system/cpu/intel_pstate/no_turbo
	${SUDO} chmod g+w /sys/devices/system/cpu/cpu*/cpufreq/scaling_*_freq
	${SUDO} chgrp $GROUP /sys/devices/system/cpu/cpu*/cpufreq/scaling_*_freq
	${SUDO} chmod g+w /sys/devices/system/cpu/intel_pstate/max_perf_pct
	${SUDO} chgrp $GROUP /sys/devices/system/cpu/intel_pstate/max_perf_pct
    fi
    
    echo 1 |  tee /sys/devices/system/cpu/intel_pstate/no_turbo

    fmin=`cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq`
    boost=`cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq`
    echo $fmin | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_min_freq
    echo $boost | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_max_freq
    fmax=`cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq`
}

quit() {
    init
    echo 0 | tee /sys/devices/system/cpu/intel_pstate/no_turbo
}

set_pct () {
    echo $PCT | tee /sys/devices/system/cpu/intel_pstate/max_perf_pct
#    echo $PCT | ${SUDO} tee /sys/devices/system/cpu/intel_pstate/min_perf_pct
#    echo $PCT | ${SUDO} tee /sys/devices/system/cpu/intel_pstate/max_perf_pct
}

set_noboost () {
    echo $NOBOOST | tee /sys/devices/system/cpu/intel_pstate/no_turbo
}

if [ $1 == 'init' ]
then
    init
fi
if [ $1 == 'quit' ]
then
    quit
fi
if [ $1 == 'freq' ]
then
   FREQ=$2
   set_freq
fi
if [ $1 == 'pct' ]
then
   PCT=$2
   set_pct
fi
if [ $1 == 'noboost' ]
then
    NOBOOST=$2
    set_noboost
fi
