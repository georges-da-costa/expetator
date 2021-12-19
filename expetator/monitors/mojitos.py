import os
import stat

def read_int(filename):
    """Read integer from file filename"""
    with open(filename) as file_id:
        return int(file_id.readline())


network_names = {'rxb', 'rxp', 'txb', 'txp'}
infiniband_names = {'irxb', 'irxp', 'itxb', 'itxp'}
rapl_names = {'dram0', 'dram1', 'package-00', 'package-11'}
load_names = {'user', 'nice', 'system', 'idle', 'iowait', 'irq',
              'softirq', 'steal', 'guest', 'guest_nice'}
perf_names = {'cpu_cycles', 'instructions', 'cache_references', 'cache_misses',
              'branch_instructions', 'branch_misses', 'bus_cycles', 'ref_cpu_cycles',
              'cache_l1d_r_a', 'cache_l1d_r_m', 'cache_l1d_w_a', 'cache_l1d_w_m', 'cache_l1d_p_a', 'cache_l1d_p_m',
              'cache_ll_r_a', 'cache_ll_r_m', 'cache_ll_w_a', 'cache_ll_w_m', 'cache_ll_p_a', 'cache_ll_p_m',
              'cache_dtlb_r_a', 'cache_dtlb_r_m', 'cache_dtlb_w_a', 'cache_dtlb_w_m', 'cache_dtlb_p_a', 'cache_dtlb_p_m',
              'cache_itlb_r_a', 'cache_itlb_r_m', 'cache_itlb_w_a', 'cache_itlb_w_m', 'cache_itlb_p_a', 'cache_itlb_p_m',
              'cache_bpu_r_a', 'cache_bpu_r_m', 'cache_bpu_w_a', 'cache_bpu_w_m', 'cache_bpu_p_a', 'cache_bpu_p_m',
              'cache_node_r_a', 'cache_node_r_m', 'cache_node_w_a', 'cache_node_w_m', 'cache_node_p_a', 'cache_node_p_m',
              'cache_op_read_r_a', 'cache_op_read_r_m', 'cache_op_read_w_a', 'cache_op_read_w_m', 'cache_op_read_p_a', 'cache_op_read_p_m',
              'cache_op_prefetch_r_a', 'cache_op_prefetch_r_m', 'cache_op_prefetch_w_a',
              'cache_op_prefetch_w_m', 'cache_op_prefetch_p_a', 'cache_op_prefetch_p_m',
              'cache_result_access_r_a', 'cache_result_access_r_m', 'cache_result_access_w_a',
              'cache_result_access_w_m', 'cache_result_access_p_a', 'cache_result_access_p_m',
              'cpu_clock', 'task_clock', 'page_faults', 'context_switches',
              'cpu_migrations', 'page_faults_min', 'page_faults_maj',
              'alignment_faults', 'emulation_faults', 'dummy', 'bpf_output'}

def get_names():
    return network_names | rapl_names | load_names | perf_names | infiniband_names

def get_structured_names():
    return {'network':network_names,
            'rapl':rapl_names,
            'load':load_names,
            'perfct':perf_names,
            'infiniband': infiniband_names}

class Mojitos:
    'Monitoring using MojitO/S'
    def __init__(self, sensor_set={'dram0'}, frequency=10):

        self.perf = len(sensor_set & perf_names) != 0
        self.network = len(sensor_set & network_names) != 0
        self.rapl = len(sensor_set & rapl_names) != 0
        self.load = len(sensor_set & load_names) != 0    
        self.infiniband = len(sensor_set & infiniband_names) != 0    
        
        self.executor = None

        self.names = sensor_set
        self.frequency = frequency
        self.cmdline = ''
        
    def build(self, executor):
        """Installs the mojito/s monitoring framework and add the permissions"""

        if True or self.rapl:
            # should work but do not work currently as to compile mojitos it
            # is always necessary to have rapl. Todo: update mojitos
            if False in [os.path.exists(filename) for filename in
                         ['/usr/share/doc/powercap-utils',
                          '/usr/share/doc/libpowercap-dev',
                          '/usr/share/doc/libpowercap0']]:
                executor.hosts('apt install -y libpowercap0 libpowercap-dev powercap-utils', root=True)
        if not os.path.exists('/tmp/mojitos'):
            executor.local('cd /tmp; git clone https://gitlab.irit.fr/sepia-pub/mojitos.git')
        else:
            executor.local('cd /tmp/mojitos; git pull')
        executor.local('cd /tmp/mojitos; make')
        executor.local('cp /tmp/mojitos/mojitos /tmp/bin/')
        if True or self.rapl:
            if read_int('/proc/sys/kernel/perf_event_paranoid') != 0:
                executor.hosts("sh -c 'echo 0 >/proc/sys/kernel/perf_event_paranoid'", root=True)
            mode = os.stat('/sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_max_power_uw')
            if not mode.st_mode & stat.S_IWUSR:
                executor.hosts("chmod a+rw /sys/class/powercap/intel-rapl/*/*", root=True)
                executor.hosts("chmod a+rw /sys/class/powercap/intel-rapl/*/*/*", root=True)

        self.executor = executor

        self.cmdline = '/tmp/bin/mojitos -t 0 -f %s' % self.frequency
        if self.perf:
            self.cmdline += ' -p ' + ','.join(self.names & perf_names)
        if self.network:
            self.cmdline += ' -d X'
        if self.infiniband:
            self.cmdline += ' -i X'
        if self.rapl:
            self.cmdline += ' -r'
        if self.load:
            self.cmdline += ' -u'
        self.cmdline += ' -o /dev/shm/monitoring &'


    def start(self):
        'Starts the monitoring right before the benchmark'
        self.executor.hosts(self.cmdline)

    def stop(self):
        'Stops the monitoring right before the benchmark'
        self.executor.hosts('killall mojitos')

    def save(self, experiment, benchname, beg_time):
        'Save the results when time is no more critical'
        filename_moj = experiment.output_file+'_mojitos'
        os.makedirs(filename_moj, exist_ok=True)
        if len(self.executor.hostnames) > 1:
            for hostname in self.executor.hostnames:
                self.executor.local('oarcp %s:/dev/shm/monitoring %s/%s_%s_%s' %
                                    (hostname, filename_moj, hostname, benchname, beg_time))
        else:
            self.executor.local('cp /dev/shm/monitoring %s/%s_%s_%s' %
                                    (filename_moj, 'localhost', benchname, beg_time))
