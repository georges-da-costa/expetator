#!/bin/bash

# manager.sh
hostname

SUDO=sudo

if [[ `hostname` == *grid5000.fr ]]
then
    SUDO=sudo-g5k
fi

set_cap () {
        echo $CAP | tee /sys/devices/virtual/powercap/intel-rapl/intel-rapl\:*/constraint_${TERM}_power_limit_uw
}

init() {
    if [ ! -w /sys/devices/virtual/powercap/intel-rapl/intel-rapl\:0/constraint_0_power_limit_uw ]
    then
	GROUP=`groups | cut -f 1 -d ' '`
	${SUDO} chmod g+w /sys/devices/virtual/powercap/intel-rapl/intel-rapl*/constraint_*_power_limit_uw
	${SUDO} chgrp $GROUP /sys/devices/virtual/powercap/intel-rapl/intel-rapl*/constraint_*_power_limit_uw
    fi
}

quit() {
    cat /sys/devices/virtual/powercap/intel-rapl/intel-rapl\:0/constraint_0_max_power_uw | tee  /sys/devices/virtual/powercap/intel-rapl/intel-rapl\:*/constraint_0_power_limit_uw
    cat /sys/devices/virtual/powercap/intel-rapl/intel-rapl\:0/constraint_1_max_power_uw | tee  /sys/devices/virtual/powercap/intel-rapl/intel-rapl\:*/constraint_1_power_limit_uw
}

if [ $1 == 'init' ]
then
    init
fi
if [ $1 == 'quit' ]
then
    quit
fi
if [ $1 == 'cap' ]
then
    TERM=$2
    CAP=$3
    set_cap
fi
