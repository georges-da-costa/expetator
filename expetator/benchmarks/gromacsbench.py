import os
import random
import re
from distutils import spawn

## From https://www.mpibpc.mpg.de/16460085/bench.pdf

class GromacsBench:
    'Molecular simulation benchmark'
    def __init__(self, params=None, default_steps = 1500):
        self.names = {'gromacs'}

        self.datasets = params
        self.default_steps = default_steps
        
    def build(self, executor):
        'Install the gromacs benchmark'

        if spawn.find_executable('mdrun_mpi') is None:
            executor.hosts('apt install -y gromacs gromacs-openmpi', root=True)

        basedir = os.path.dirname(os.path.abspath(__file__))
        if self.datasets is None:
            
            executor.local('rsync %s/gromacs*.tpr /tmp/bin' % basedir)
            names = [filename[7:-4] for filename in os.listdir('/tmp/bin') if
                     filename.startswith('gromacs') and filename.endswith('.tpr')]
            self.datasets = [(name, self.default_steps) for name in names]

        else:
            for (name, _) in self.datasets:
                executor.local('rsync %s/gromacs%s.tpr /tmp/bin' % (basedir, name))

        print(self.datasets)
        return {'gromacs': self.datasets}

    def run(self, bench, params, executor):
        'Runs gromacs benchmark'
        name, niter = params
        output = executor.cores('-x GMX_MAXBACKUP=-1 mdrun_mpi -s /tmp/bin/gromacs%s.tpr -nsteps %s 2>&1' % (name, niter))
        delta = re.search('Time:[^\n]*\n', output).group(0).split()[2]
        return delta, 'gromacs-%s-%s' % (name, niter)
