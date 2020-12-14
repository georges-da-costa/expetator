import os
import random
import time

class GenericBench:
    'Wide coverage benchmark, from memory to processor and network'
    def __init__(self, step_duration = 4, step_size = 25):
        self.names = {'generic'}
        self.duration = step_duration
        self.step = step_size
        self.remote = "localhost"

    def build(self, executor):
        'Builds the wide coverage benchmark'
        if len(executor.hostnames) > 1:
            self.remote = executor.hostnames[-1]

        basedir = os.path.dirname(os.path.abspath(__file__))
        for source in ["ub_cpu_cu", "ub_cpu_alu",
                       "ub_cpu_rand", "setcpulatency", "ub_mem_access"]:
            executor.local('gcc %s/genericbench/%s.c -o /tmp/bin/%s' %
                           (basedir, source, source))
        executor.local('cp %s/genericbench/uc-generic.sh /tmp/bin' % basedir)
        executor.hosts('apt install -y iperf3 cpulimit', root=True)
        executor.local('chmod go+w /dev/cpu_dma_latency', root=True)
        params = {'generic': [None]}

        return params

    def run(self, bench, params, executor):
        'Runs the wide coverage benchmark'

        starting_time = time.time()
        throughput = executor.local("/tmp/bin/uc-generic.sh %s %s" %
                                    (self.duration, self.remote))
        delta = time.time() - starting_time
        return delta, 'generic'
