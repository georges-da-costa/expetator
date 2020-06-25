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

class Dvfs:
    'Cpufreq based DVFS'
    def __init__(self, dummy=False, baseline=False, frequencies=None):
        self.basedir = os.path.dirname(os.path.abspath(__file__))
        self.dummy = dummy
        self.baseline = baseline
        self.executor = None
        self.available_frequencies = frequencies

    def build(self, executor):
        'Gather the available Frequenciess'
        self.executor = executor
        self.executor.hosts(self.basedir+'/dvfs_pct.sh init')
        if self.available_frequencies is None:
            self.available_frequencies, _ = get_dvfs_values()
            if self.dummy:
                self.available_frequencies = [self.available_frequencies[0],
                                              self.available_frequencies[-1]]
            if self.baseline:
                self.available_frequencies = [self.available_frequencies[-1]]

    def available_states(self):
        'Returns all the Frequenciess'
        return self.available_frequencies

    def start(self, freq):
        'Sets the right frequency on all hosts'
        if freq in self.available_frequencies:
            self.executor.hosts('%s/dvfs_pct.sh freq %s' % (self.basedir, freq))

    def stop(self, output_file=None):
        'Reverts to the maximum frequency'
        self.executor.hosts(self.basedir+'/dvfs_pct.sh init')
            
    def get_state(self):
        'Returns the current min and max frequencies'
        cur_min_freq = read_int('/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq')
        cur_max_freq = read_int('/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq')
        return (cur_min_freq, cur_max_freq)

    def state_to_str(self):
        'Returns the current min and max frequencies as a string'
        (cur_min_freq, cur_max_freq) = self.get_state()
        return '%s %s' % (cur_min_freq, cur_max_freq)

    def get_labels(self):
        'Returns the label for frequenciess'
        return ('fmin', 'fmax')
