import random
import os

class GpuMemBench:
    'Cloud-like gpu benchmark'

    def __init__(self):
        self.names = {'gpumem'}
        
    def build(self, executor):
        'Builds the gpu benchmark'
        basedir = os.path.dirname(os.path.abspath(__file__))
        
        executor.local('/usr/local/cuda-10.1/bin/nvcc -arch=sm_70 %s/m.cu -o /tmp/bin/gpu' % basedir)

        params = {'gpumem':[(r/100) for r in range(10, 100, 10)]}

        return params

    def run(self, bench, params, executor):
        'Runs the gpu benchmark on gpu 0'
        (datasz) = params
        delta = executor.local('/tmp/bin/gpu -s 0 0 %s' %(datasz))
        return delta.strip(), 'gpumem-%s' %(int(datasz*100))
