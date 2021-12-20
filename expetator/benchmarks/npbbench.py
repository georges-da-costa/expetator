import os
import re
import math

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
    



def test_lu(nb):
	xdim = int(math.sqrt(nb))
	ydim = nb // xdim
	while(xdim*ydim != nb and 2*ydim >= xdim):
		xdim += 1
		ydim = nb // xdim
	return xdim*ydim == nb and 2*ydim >= xdim

def get_lu(nb):
	val = max(nb, 1)
	while(not test_lu(val)):
		val -= 1
	return val


def get_square(nb):
	tmp = int(math.sqrt(nb))
	return tmp*tmp

def get_power_of_2(i):
	return 2**int(math.log2(i))
    
def npb_constraints(name, nbproc):
    if name in ['cg', 'is']:
        return get_power_of_2(nbproc)
    if name in ['lu']:
        return get_lu(nbproc)
    return nbproc # for 'ep', 'bt', 'sp', 'ft', 'mg'
    
    
class NpbBench:
    'Nas Parallel Benchmark'
    def __init__(self, names={'ep', 'bt', 'sp', 'cg', 'is', 'ft', 'lu', 'mg'},
                 options=None):
        self.names = names
        self.params = options

    def build(self, executor):

        basedir = os.path.dirname(os.path.abspath(__file__))
        
        'Builds NPB benchmark'

        target_file = os.path.expanduser('~/.local/tmp/NPB3.4-MPI.tar.gz')
        if not os.path.isfile(target_file):
            os.makedirs(os.path.expanduser('~/.local/tmp/'), exist_ok=True)
            executor.local('wget https://www.nas.nasa.gov/assets/npb/NPB3.4.tar.gz -O %s' % target_file)
        executor.local('tar xfC %s /tmp/' % target_file, shell=False)
        executor.local('cp /tmp/NPB3.4/NPB3.4-MPI/config/make.def.template /tmp/NPB3.4/NPB3.4-MPI/config/make.def')
        executor.local("sed -i 's/mpif90/mpif90 -fallow-argument-mismatch -fallow-invalid-boz/' /tmp/NPB3.4/NPB3.4-MPI/config/make.def")
        nbproc = executor.nbcores

        if self.params is None:
            self.params = standard_parameters(nbproc)

        for bench in self.names:
            executor.local('cd /tmp/NPB3.4/NPB3.4-MPI/; make %s CLASS=%s'
                           %(bench, self.params[bench]))

        executor.local('cp /tmp/NPB3.4/NPB3.4-MPI/bin/* /tmp/bin/')

        for key in self.params:
            self.params[key] = [(self.params[key], npb_constraints(key, nbproc))]
        return self.params

    def run(self, bench, params, executor):
        """Runner for NPB benchmarks """
        classtype, nbproc = params
        output = executor.mpi('/tmp/bin/%s.%s.x' % (bench, classtype),
                              executor.mpi_core_file, nbproc)

        execution_time = float(re.search(' Time in seconds = *(.*)', output).group(1))
        benchname = bench+'-'+classtype+'-'+str(nbproc)
        return execution_time, benchname
