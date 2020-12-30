import os

class WaterMark:
    'Adds watermark to any benchmark'
    def __init__(self, benchmark, total_time=30, nb_steps=2):
        self.bench = benchmark
        self.total_time = total_time
        self.nb_steps = nb_steps

        self.names = { 'wt-'+str(total_time)+'-'+name  for name in benchmark.names}

    def build(self, executor):
        basedir = os.path.dirname(os.path.abspath(__file__))
        executor.local('mpicc %s/watermark.c -o /tmp/bin/watermark' % basedir)

        return { 'wt-%d-%s' %(self.total_time, key):val
                 for key,val in self.bench.build(executor).items()}

    def run(self, bench, params, executor):
        'Runs the benchmark with watermark'
        _, _, initial_bench = bench.split('-', maxsplit=2)
        executor.cores('/tmp/bin/watermark');
        value, name = self.bench.run(initial_bench, params, executor)
        executor.cores('/tmp/bin/watermark');

        return value, 'wt-%d-%s' % (self.total_time, name)
