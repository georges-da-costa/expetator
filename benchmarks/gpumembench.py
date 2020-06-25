import random
import os

class GpuMemBench:
    'Cloud-like gpu benchmark'

    def __init__(self):
        self.names = {'gpumem'}
        
    def build(self, executor, deterministic):
        'Builds the gpu benchmark'
        basedir = os.path.dirname(os.path.abspath(__file__))
        
        executor.local('nvcc -arch=sm_70 %s/m.cu -o /tmp/bin/gpu' % basedir)
        if deterministic:
            params = {'gpumem':[(r/100) for r in range(10, 100, 10)]}
        else:
            params = {'gpumem':[lambda: (random.randint(10, 100)/100)]}
        return params

    def run(self, bench, params, executor):
        'Runs the gpu benchmark on gpu 0'
        (datasz) = params
        delta = executor.local('/tmp/bin/gpu -s 0 0 %s' %(datasz))
        return delta.strip(), 'gpumem-%s' %(int(datasz*100))
