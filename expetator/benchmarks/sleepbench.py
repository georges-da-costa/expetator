import time

class SleepBench:
    'Sleep benchmark'
    def __init__(self, default_time=30):
        self.names = {'sleep'}
        self.time = default_time

    def build(self, executor, deterministic):
        'returns the parameters'
        return {'sleep':[self.time]}

    def run(self, bench, params, executor):
        'Runs the sleep benchmark'
        time.sleep(params)
        return str(params), 'sleep-'+str(params)