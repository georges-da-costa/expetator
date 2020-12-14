import os
import random

class PercentageBench:
    'Cloud like benchmark, loads only a percentage of a core'
    def __init__(self, duration = 10, values = None):
        self.names = {'perc'}
        self.nb_processes = 0
        self.duration = duration
        self.values = values

    def build(self, executor):
        'Builds cloud-like benchmark'
        self.nb_processes = executor.nbcores // executor.nbhosts
        if 'OAR_NODE_FILE' in os.environ:
            self.nb_processes = 2*self.nb_processes

        basedir = os.path.dirname(os.path.abspath(__file__))

        executor.local('gcc %s/percentage_load.c -o /tmp/bin/percentage_load' % basedir)

        if not self.values is None:
            params = {'perc': self.values}
        else:
            params = {'perc': [lambda: random.randint(1, 100)]}
        return params

    def run(self, bench, params, executor):
        'Runs the cloud-like benchmark'
        ratio = params
        throughput = executor.local("mpirun --use-hwthread-cpus -np %s /tmp/bin/percentage_load %s %s" %
                                    (self.nb_processes, ratio, self.duration))
        
        return sum([float(value) for value in throughput.split()]), 'perc-%03d' % ratio
