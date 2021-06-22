import os
import stat

def read_int(filename):
    """Read integer from file filename"""
    with open(filename) as file_id:
        return int(file_id.readline())


class Lperf:
    'Monitoring using a modified version of Linux Perf tool'
    def __init__(self, sensor_set={'instructions'}, interval=100):

        self.executor = None
        self.names = sensor_set
        self.interval = interval
        self.cmdline = ''
        
    def build(self, executor):
        """Installs and modifies the Linux Perf Tool"""

        current_path=os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists('/tmp/lperf/tools/perf/perf'):
            executor.local('mkdir /tmp/lperf; tar xj -C /tmp/lperf/ -f %s/lperf_tools.tar.bz2' % current_path)
            executor.local('patch -i %s/lperf_builtin-stat.diff /tmp/lperf/tools/perf/builtin-stat.c' % current_path)
            executor.local('cd /tmp/lperf/tools/perf/; make')
        executor.local('cp /tmp/lperf/tools/perf/perf /tmp/bin/lperf')
        if read_int('/proc/sys/kernel/perf_event_paranoid') != 0:
            executor.hosts("sh -c 'echo 0 >/proc/sys/kernel/perf_event_paranoid'", root=True)

        self.executor = executor

        self.cmdline = '/tmp/bin/lperf stat -x "!" -I %s -a -A -e %s' % (self.interval, ','.join(self.names))
        self.cmdline += ' -o /dev/shm/lperf_monitoring &'

    def start(self):
        'Starts the monitoring right before the benchmark'
        self.executor.hosts(self.cmdline)

    def stop(self):
        'Stops the monitoring right before the benchmark'
        self.executor.hosts('killall lperf')

    def save(self, experiment, benchname, beg_time):
        'Save the results when time is no more critical'
        filename_moj = experiment.output_file+'_lperf'
        os.makedirs(filename_moj, exist_ok=True)
        if len(self.executor.hostnames) > 1:
            for hostname in self.executor.hostnames:
                self.executor.local('oarcp %s:/dev/shm/lperf_monitoring %s/%s_%s_%s' %
                                    (hostname, filename_moj, hostname, benchname, beg_time))
        else:
            self.executor.local('cp /dev/shm/lperf_monitoring %s/%s_%s_%s' %
                                    (filename_moj, 'localhost', benchname, beg_time))
