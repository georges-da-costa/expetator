
class GpuClock:
    'nvidia-smi graphics/sm clock setting'
    def __init__(self, dummy=False, baseline=False, steps=2, zoomfrom=0, zoomto=0):
        self.dummy = dummy
        self.baseline = baseline
        self.executor = None
        self.available_frequencies = []
        self.available_frequencies_mem = []
        self.clock_mem_max = None
        self.clock_sm_min = None
        self.nsteps = steps 
        # zoomfrom/to enables full freq. granularity within a clock window:
        if zoomto != 0 and zoomfrom != zoomto:
            self.zoom = (zoomfrom, zoomto)
        else:
            self.zoom = None

    def build(self, executor):
        'Gather the available frequencies'
        self.executor = executor
        q = "nvidia-smi -i 0 --query-supported-clocks=gr --format=csv,noheader,nounits | tr '\n' ' '"
        clk_s = self.executor.local(q)
        clk = sorted([int(f) for f in clk_s.strip().split(' ')])
        self.clock_sm_min = clk[0]
        self.available_frequencies = [clk[(i*(len(clk)-1))//(self.nsteps-1)] for i in range(self.nsteps)]
        q = "nvidia-smi -i 0 --query-supported-clocks=mem --format=csv,noheader,nounits | tr '\n' ' '"
        clk_s = self.executor.local(q)
        self.available_frequencies_mem = sorted([int(f) for f in clk_s.strip().split(' ')])
        self.clock_mem_max = self.available_frequencies_mem[-1]
        if self.zoom is not None:
            # pick all available freq within the zoom window:
            clkz = [f for f in clk if self.zoom[0] <= f and f <= self.zoom[1]]
            rest = [f for f in self.available_frequencies if f < self.zoom[0] or self.zoom[1] < f]
            self.available_frequencies = sorted(clkz + rest)
        if self.dummy:
            self.available_frequencies = [self.available_frequencies[0], self.available_frequencies[-1]]
        if self.baseline:
            self.available_frequencies = [self.available_frequencies[-1]]

    def available_states(self):
        'Returns all the frequencies'
        return self.available_frequencies

    def start(self, freq):
        'Sets the right frequency range on gpu 0'
        if freq in self.available_frequencies:
            self.executor.local('nvidia-smi -i 0 -ac  %s,%s' % (self.clock_mem_max, freq), root=True)
            #self.executor.local('nvidia-smi -i 0 -lgc  %s,%s' % (self.clock_sm_min, freq), root=True)

    def stop(self, output_file=None):
        'Reverts to the maximum frequency'
        self.executor.local('nvidia-smi -i 0 -rac', root=True)
        #self.executor.local('nvidia-smi -i 0 -rgc', root=True)
            
    def get_state(self):
        'Returns the current min and max application frequencies'
        cur_min = self.clock_sm_min
        cur_max = int(self.executor.local('nvidia-smi -i 0 --query-gpu=clocks.applications.gr --format=csv,noheader,nounits'))
        return (cur_min, cur_max, self.clock_mem_max)

    def state_to_str(self):
        'Returns the current min and max frequencies as a string'
        (cur_min, cur_max, mem_max) = self.get_state()
        return '%s %s %s' % (cur_min, cur_max, mem_max)

    def get_labels(self):
        'Returns the label for frequencies'
        return ('fmin', 'fmax', 'fmemax')

