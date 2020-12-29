import json
import os

def read_int(filename):
    """Read integer from file filename"""
    with open(filename) as file_id:
        return int(file_id.readline())

class Powercap:
    def __init__(self, function=None, term=0):
        self.term = term
        self.function = function
        self.values = None
        self.executor = None
        self.basedir = os.path.dirname(os.path.abspath(__file__))

    def build(self, executor):
        self.executor = executor
        
        target = '/sys/devices/virtual/powercap/intel-rapl/intel-rapl:0/constraint_%d_max_power_uw' % self.term
        value = read_int(target)
        if self.function is None:
            self.values = [0, value]
        else:
            self.values = self.function(value)

        self.executor.hosts(self.basedir+'/powercap.sh init')
        
    def available_states(self):
        return self.values
            
    def start(self, cap):
        self.executor.hosts('%s/powercap.sh cap %d %s' % (self.basedir, self.term, cap))

    def stop(self, output_file=None):
        self.executor.hosts(self.basedir+'/powercap.sh quit')

    def get_state(self):
        cur_cap = read_int('/sys/devices/virtual/powercap/intel-rapl/intel-rapl:0/constraint_%d_power_limit_uw' % self.term)
        return cur_cap

    def state_to_str(self):
        return str(self.get_state())

    def get_labels(self):
        return ('cap%d' % self.term, )
