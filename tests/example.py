#!/usr/bin/python3
"""This script run HPC benchmarks with enabled monitoring

"""

import os
import sys
import platform

import expetator.experiment as experiment

from expetator.benchmarks import sleepbench
from expetator.monitors import mojitos, power
from expetator.leverages import dvfs, pct

BENCHMARKS = [sleepbench.SleepBench(default_time=5)]

LEVERAGES = [dvfs.Dvfs(dummy=True), pct.Pct(dummy=True)]

hw_pct = {'instructions', 'cache_misses'}
MONITORS = [mojitos.Mojitos(sensor_set = hw_pct),
            power.Power()]

if len(sys.argv) > 1:
    dest_dir = sys.argv[1]
else:
    dest_dir = '/tmp/demo'

cluster = platform.node().split('-')[0]

name = '%s/%s/demo' % (dest_dir, cluster)
os.makedirs(os.path.dirname(name), exist_ok=True)

experiment.run_experiment(name, BENCHMARKS,
                          leverages=LEVERAGES,
                          monitors=MONITORS,
                          sweep=True, times=1)
