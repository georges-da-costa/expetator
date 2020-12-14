import random
import os

class CpuBench:
    'Cloud-like cpu benchmark'
    def __init__(self, param_func=None, time_ref=30):
        self.names = {'cpu'}
        self.param_func = param_func
        self.time_ref = time_ref
        self.nb_processes = 1
        
    def build(self, executor):
        'Builds the cpu benchmark'

        self.nb_processes = executor.nbcores // executor.nbhosts
        if 'OAR_NODE_FILE' in os.environ:
            self.nb_processes = 2*self.nb_processes

        basedir = os.path.dirname(os.path.abspath(__file__))
            
        executor.local('gcc %s/cpu.c -o /tmp/bin/cpu' % basedir)
        ref = int(executor.local('/tmp/bin/cpu --test'))
        time_ref = 30

        if self.param_func is None:
            params = {'cpu':[(ref//3, self.time_ref),
                             ((2*ref)//3, self.time_ref),
                             (ref//2, self.time_ref),
                             (ref*2, self.time_ref)]}
        else:
            params = {'cpu': [ (res, self.time_ref) for res in self.param_func(ref)]}

        return params

    def run(self, bench, params, executor):
        'Runs the cpu benchmark'
        (load, length) = params

        delta = executor.local('/tmp/bin/cpu %s %s %s'
                               % (load, length, self.nb_processes))
        return delta.strip(), 'cpu-%s-%s' %(load, length)
