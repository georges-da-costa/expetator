import random
import os

class GpuCpuBench:
    'Cloud-like gpu benchmark'

    def __init__(self):
        self.names = {'gpucpu'}
        
    def build(self, executor, deterministic):
        basedir = os.path.dirname(os.path.abspath(__file__))
        'Builds the gpu benchmark'
        executor.local('nvcc -arch=sm_70 %s/m.cu -o /tmp/bin/gpu' % basedir)
        if deterministic:
            params = {'gpucpu':[(r/100) for r in range(75, 126, 50)]}
        else:
            params = {'gpucpu':[lambda: (random.randint(75, 125)/100)]}
        return params

    def run(self, bench, params, executor):
        'Runs the gpu benchmark on gpu 0'
        (datasz) = params
        delta = executor.local('/tmp/bin/gpu -s 0 1 %s' %(datasz))
        return delta.strip(), 'gpucpu-%s' %(int(datasz*100))
