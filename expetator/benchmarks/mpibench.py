import os
import random

class MpiBench:
    'Complex mpi benchmark'
    def __init__(self, params=None):
        self.names = {'mpi'}
        self.params = {'mpi': params}

    def build(self, executor):
        'Builds the complex mpi benchmark'

        basedir = os.path.dirname(os.path.abspath(__file__))
        
        nbproc = executor.nbcores
        if nbproc < 16:
            executor.local('mpicc %s/mpi_generic.c -o /tmp/bin/mpi_generic' % basedir)
        elif nbproc <32:
            executor.local('mpicc -DSIZE=65536 %s/mpi_generic.c -o /tmp/bin/mpi_generic' % basedir)
        else:
            executor.local('mpicc -DSIZE=8192 %s/mpi_generic.c -o /tmp/bin/mpi_generic' % basedir)

        if self.params['mpi'] is None:
            self.params = {'mpi':[(16, 0, 0, 0), (0, 16, 0, 0),
                                  (0, 0, 16, 0), (0, 0, 0, 16), (4, 4, 4, 4)]}
                
        return self.params

    def run(self, bench, params, executor):
        'Runs the complex mpi benchmark'
        pcpu, pmem, pmpi, pbar = params
        delta = executor.cores('/tmp/bin/mpi_generic -c %s -m %s -n %s -b %s'
                               % (pcpu*3000, pmem, pmpi, pbar))
        return delta.strip(), 'mpigeneric-%s-%s-%s-%s' % (pcpu, pmem, pmpi, pbar)
