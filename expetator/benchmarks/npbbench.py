import os
import re

def standard_parameters(nbproc):
    if nbproc < 16:
        return {'ep':'C', 'bt':'A', 'sp':'A', 'cg':'B',
                'is':'C', 'ft':'B', 'lu':'A', 'mg':'C'}
    if nbproc < 64:
        return  {'ep':'C', 'bt':'B', 'sp':'B', 'cg':'C',
                 'is':'D', 'ft':'C', 'lu':'B', 'mg':'D'}
    if nbproc < 256:
        return  {'ep':'D', 'bt':'C', 'sp':'C', 'cg':'D',
                 'is':'D', 'ft':'C', 'lu':'C', 'mg':'D'}
    # nbproc >= 256
    return {'ep':'D', 'bt':'D', 'sp':'D', 'cg':'D',
            'is':'E', 'ft':'E', 'lu':'D', 'mg':'D'}
    

class NpbBench:
    'Nas Parallel Benchmark'
    def __init__(self, names={'ep', 'bt', 'sp', 'cg', 'is', 'ft', 'lu', 'mg'},
                 options=None):
        self.names = names
        self.params = options

    def build(self, executor):

        basedir = os.path.dirname(os.path.abspath(__file__))
        
        'Builds NPB benchmark'
        executor.local('tar xfC %s/NPB3.4-MPI.tgz /tmp/' % basedir, shell=False)
        executor.local('cp /tmp/NPB3.4-MPI/config/make.def.template /tmp/NPB3.4-MPI/config/make.def ')
        nbproc = executor.nbcores

        if self.params is None:
            self.params = standard_parameters(nbproc)

        for bench in self.names:
            executor.local('cd /tmp/NPB3.4-MPI/; make %s CLASS=%s'
                           %(bench, self.params[bench]))

        executor.local('cp /tmp/NPB3.4-MPI/bin/* /tmp/bin/')

        for key in self.params:
            self.params[key] = [(self.params[key], nbproc)]
        return self.params

    def run(self, bench, params, executor):
        """Runner for NPB benchmarks """
        classtype, nbproc = params
        output = executor.cores('/tmp/bin/%s.%s.x' % (bench, classtype))
        execution_time = float(re.search(' Time in seconds = *(.*)', output).group(1))
        benchname = bench+'-'+classtype+'-'+str(nbproc)
        return execution_time, benchname
