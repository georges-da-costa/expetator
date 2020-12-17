import time


class WaterMark:
    'Adds watermark to any benchmark'
    def __init__(self, benchmark, total_time=30, nb_steps=3):
        self.bench = benchmark
        self.total_time = total_time
        self.nb_steps = nb_steps

        self.low = int(total_time/(2*nb_steps+1))
        self.high = (total_time-self.low*(nb_steps+1))/nb_steps
        
        self.names = { 'wt-'+str(total_time)+'-'+name  for name in benchmark.names}

    def build(self, executor):
        return { 'wt-%d-%s' %(self.total_time, key):val
                 for key,val in self.bench.build(executor).items()}

    def run(self, bench, params, executor):
        'Runs the benchmark with watermark'
        self.do_watermark(executor)
        value, name = self.bench.run(bench, params, executor)
        self.do_watermark(executor)
        return value, 'wt-%d-%s' % (self.total_time, name)

    def do_watermark(self, executor):
        print('Watermark', self.total_time, 's')
        
        mark = 'cat /dev/zero > /dev/null & pid=$!; sleep %f; kill -9 ${pid}' % self.high
        for _ in range(self.nb_steps):
            time.sleep(self.low)
            executor.cores(mark)
        time.sleep(self.low)
