import os
import random

class MemBench:
    '''Memory benchmark
Parameter is a function taking the max number of cores and returning a list of integer
The parameter is the number of memory intensive processes started'''
    def __init__(self, param_func=None):
        self.names = {'mem'}
        self.param_func = param_func

    def build(self, executor):
        'Builds memory benchmark'
        nb_processes = executor.nbcores // executor.nbhosts
        if 'OAR_NODE_FILE' in os.environ:
            nb_processes = 2*nb_processes

        basedir = os.path.dirname(os.path.abspath(__file__))
        executor.local('gcc -DNTIMES=2000 -O %s/mem.c -o /tmp/bin/mem' % basedir)
        #params = {'mem':list(range(1,2*nbproc+1))}
        #params = {'mem':list(range(1,4))}

        if self.param_func is None:
            params = {'mem': [1, nb_processes]}
        else:
            params = {'mem' : self.param_func(nb_processes)}

        return params

    def run(self, bench, params, executor):
        'Runs the memory benchmark'
        nbproc = params
        execution_time = executor.local("/tmp/bin/mem %s" % nbproc)
        return execution_time.strip(), 'mem-%02d' % nbproc
