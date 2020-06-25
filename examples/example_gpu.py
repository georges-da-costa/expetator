#!/usr/bin/python3
"""This script run HPC benchmarks with enabled monitoring

"""

import os
import sys
import platform

import expetator.experiment as experiment

from expetator.benchmarks import sleepbench, cpubench, mpibench, membench, npbbench, gpucpubench, gpumembench
from expetator.monitors import mojitos, power, powergpu
from expetator.leverages import dvfs, gpuclock, gpupow

BENCHMARKS = [gpucpubench.GpuCpuBench(), gpumembench.GpuMemBench()]

LEVERAGES = [gpupow.GpuPower(steps=2), gpuclock.GpuClock(steps=2)]

hw_pct = mojitos.get_names() ## All available sensors
MONITORS = [mojitos.Mojitos(sensor_set = hw_pct),
            power.Power(), powergpu.Power()]

if len(sys.argv) > 1:
    dest_dir = sys.argv[1]
else:
    dest_dir = '/tmp/demo'

cluster = platform.node().split('-')[0]

name = '%s/%s/demo_gpu' % (dest_dir, cluster)
os.makedirs(os.path.dirname(name), exist_ok=True)

experiment.run_experiment(name, BENCHMARKS,
                          leverages=LEVERAGES,
                          monitors=MONITORS,
                          sweep=True, times=1)
