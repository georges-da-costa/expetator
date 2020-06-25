
class GpuPower:
    'nvidia-smi power limit setting'
    def __init__(self, dummy=False, baseline=False, steps=3):
        self.dummy = dummy
        self.baseline = baseline
        self.executor = None
        self.available_power_limit = []
        self.nsteps = steps
        self.power_min = 150
        self.power_max = 300

    def build(self, executor):
        'Gather the maximum power limit for GPU 0'
        from math import ceil
        self.executor = executor
        self.power_min = int(float(self.executor.local('nvidia-smi -i 0 --query-gpu=power.min_limit --format=csv,noheader,nounits')))
        self.power_max = int(float(self.executor.local('nvidia-smi -i 0 --query-gpu=power.max_limit --format=csv,noheader,nounits')))
        powers = range(self.power_min, self.power_max+1, 10)
        self.available_power_limit = [powers[(i*(len(powers)-1))//(self.nsteps-1)] for i in range(self.nsteps)]
        if self.dummy:
            self.available_power_limit = [self.available_power_limit[0], self.available_power_limit[-1]]
        if self.baseline:
            self.available_power_limit = [self.available_power_limit[-1]]

    def available_states(self):
        'Returns all the power limits'
        return self.available_power_limit

    def start(self, power):
        'Sets the right power limit on gpu 0'
        if power in self.available_power_limit:
            self.executor.local('nvidia-smi -i 0 -pl  %s' % (power), root=True)

    def stop(self, output_file=None):
        'Reverts to the maximum power limit'
        self.executor.local('nvidia-smi -i 0 -pl %s' % (self.power_max), root=True)
            
    def get_state(self):
        'Returns the current min and max power limits'
        cur_min = self.power_min  # constant
        cur_max = int(float(self.executor.local('nvidia-smi -i 0 --query-gpu=power.limit --format=csv,noheader,nounits')))
        return (cur_min, cur_max)

    def state_to_str(self):
        'Returns the current min and max power limits as a string'
        (cur_min, cur_max) = self.get_state()
        return '%s %s' % (cur_min, cur_max)

    def get_labels(self):
        'Returns the label for power limits'
        return ('pmin', 'pmax')

