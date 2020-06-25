import os

def read_int(filename):
    """Read integer from file filename"""
    with open(filename) as file_id:
        return int(file_id.readline())

def get_dvfs_values():
    """Returns the list of available Frequencies and PCTs"""
    fmin = read_int('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq')
    boost = read_int('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq')
    fmax = read_int('/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq')
    nbpstate = read_int('/sys/devices/system/cpu/intel_pstate/num_pstates')
    delta = (boost-fmin) // (nbpstate-1)
    nbpct = (fmax - fmin) // delta
    pctmin = fmin * 100 // boost
    pctmax = fmax * 100 // boost

    frequencies = range(fmin, fmax+1, delta)
    pcts = [(pctmax*i + pctmin*(nbpct-i))//nbpct for i in range(0, nbpct+1)]
    return frequencies, pcts

class Pct:
    'Intel based PCT'
    def __init__(self, dummy=False, baseline=False):
        self.basedir = os.path.dirname(os.path.abspath(__file__))
        self.dummy = dummy
        self.baseline = baseline
        self.executor = None
        self.available_pcts = []

    def build(self, executor):
        'Gather the available PCTs'
        self.executor = executor
        self.executor.hosts(self.basedir+'/dvfs_pct.sh init')
        _, self.available_pcts = get_dvfs_values()
        if self.dummy:
            self.available_pcts = [self.available_pcts[0], self.available_pcts[-1]]
        if self.baseline:
            self.available_pcts = [self.available_pcts[-1]]

    def available_states(self):
        'Returns all the PCTs'
        return self.available_pcts

    def start(self, pct):
        'Sets the right pct on all hosts'
        if pct in self.available_pcts:
            self.executor.hosts('%s/dvfs_pct.sh pct %s' % (self.basedir, pct))

    def stop(self, experiment):
        'Reverts to the maximum PCT'
        self.executor.hosts('%s/dvfs_pct.sh pct %s' % (self.basedir, max(self.available_pcts)))
            
    def get_state(self):
        'Returns the current min and max pcts'
        cur_min_pct = read_int('/sys/devices/system/cpu/intel_pstate/min_perf_pct')
        cur_max_pct = read_int('/sys/devices/system/cpu/intel_pstate/max_perf_pct')
        return (cur_min_pct, cur_max_pct)

    def state_to_str(self):
        'Returns the current min and max pcts as a string'
        (cur_min_pct, cur_max_pct) = self.get_state()
        return '%s %s' % (cur_min_pct, cur_max_pct)

    def get_labels(self):
        'Returns the label for pcts'
        return ('pctmin', 'pctmax')
