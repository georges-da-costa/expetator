#!/usr/bin/python3
"""This script run HPC benchmarks with enabled monitoring

"""

import os
import random
import time
import itertools
from pathlib import Path

from functools import reduce
from execo import Process

class Executor:
    'Allow access to the platform'
    def __init__(self):
        self.mpi_host_file = '/dev/shm/mpi_host_file'
        self.mpi_core_file = '/dev/shm/mpi_core_file'
        self.mpi_options = ''
        self.hostnames = ['localhost']
        self.nbhosts = 1
        self.nbcores = os.cpu_count()
        self.sudo = 'sudo'
        self.ssh = 'ssh'
        if 'OAR_NODE_FILE' in os.environ:
            with open(os.environ['OAR_NODE_FILE']) as filename:
                content = [host.strip() for host in filename.readlines()]
                # reduce is used to keep the file order
                self.hostnames = reduce(lambda l, x: l if x in l else l+[x], content, [])
                self.nbcores = len(content)
            self.nbhosts = len(self.hostnames)
            self.mpi_options = '--map-by node --mca orte_rsh_agent oarsh'
            self.sudo = 'sudo-g5k'
            self.ssh = 'oarsh'

        with open(self.mpi_host_file, 'w') as file_id:
            for host in self.hostnames:
                file_id.write(host+" slots=1\n")

        with open(self.mpi_core_file, 'w') as file_id:
            for host in self.hostnames:
                file_id.write(host+" slots=%s\n" % (self.nbcores//self.nbhosts))

    def local(self, cmd, shell=True, root=False):
        """Executes the cmd command and returns stdout after cmd exits"""
        if root:
            cmd = self.sudo+' '+cmd
        print('DEBUG:', cmd)
        proc = Process(cmd, shell=shell)
        proc.run()
        return proc.stdout

    def mpi(self, cmd, host_file, nb_processes, root=False):
        'Executes mpi cmd and returns stdout'
        if root:
            cmd = self.sudo+' '+cmd
        mpi_cmd = 'mpirun %s -np %s --machinefile %s %s' % \
                 (self.mpi_options, nb_processes, host_file, cmd)
        return self.local(mpi_cmd)

    def hosts(self, cmd, root=False):
        """Executes cmd on each host, returns rank=0 stdout"""
        return self.mpi(cmd, self.mpi_host_file, self.nbhosts, root)

    def cores(self, cmd):
        """Executes cmd on each core, returns rank=0 stdout"""
        return self.mpi(cmd, self.mpi_core_file, self.nbcores)

    def sync(self, directory):
        'Synchronize one directory accross all nodes of the experiment'
        if len(self.hostnames) > 1:
            remote = str(Path(directory).parents[0])
            for host in self.hostnames[1:]:
                self.local('oarcp -r %s %s:%s' % (directory, host, remote))

    def get_network_if(self):
        'returns the current network interface name'
        route = self.local('ip route').split()
        default_pos = route.index('default')
        dev_pos = route.index('dev', default_pos)
        return route[dev_pos+1]

################################
# Experiment
#
class Experiment:
    'Store and runs a complete experiments'
    params = {}
    def __init__(self, name, executor, benchmarks, monitors=[], leverages=[]):
        self.executor = executor
        self.output_file = '%s_%s_%s' %(name, self.executor.hostnames[0], int(time.time()))

        os.makedirs('/tmp/bin/', exist_ok=True)
        
        self.monitors = monitors
        for monitor in monitors:
            monitor.build(self.executor)

        self.hw_modes = leverages
        for leverage in leverages:
            leverage.build(self.executor)

        self.bench_suites = benchmarks
        self.build_benchs()

        self.executor.sync('/tmp/bin')
        
    def build_benchs(self):
        'Builds all the benchmarks'
        for bench_suite in self.bench_suites:
            tmp_params = bench_suite.build(self.executor)
            self.params.update(tmp_params)

    def start_monitors(self):
        'Starts all the monitors'
        for monitor in self.monitors:
            monitor.start()
    def stop_monitors(self):
        'Stops all the monitors'
        for monitor in self.monitors:
            monitor.stop()
    def save_monitors(self, benchname, beg_time):
        'Save all the monitored values'
        for monitor in self.monitors:
            monitor.save(self, benchname, beg_time)

    def get_hw_actions(self):
        'Returns all possible combination of leverages'
        possibilities = [[(leverage, state) for state in leverage.available_states()]
                         for leverage in self.hw_modes]
        return itertools.product(*possibilities)
    def start_actions(self, actions):
        'Put each leverage in the right state'
        for (leverage, state) in actions:
            leverage.start(state)

    def stop_actions(self, actions, pattern):
        'Revert to stable state'
        for (leverage, _) in actions:
            leverage.stop(pattern)

    def get_all_benchnames(self):
        'returns the list of benchmark names'
        return set().union(*[suite.names for suite in self.bench_suites])
    def get_params(self, bench):
        'returns the list of parameters for a specific benchmark'
        return self.params[bench]
    def run_bench(self, bench, param):
        'runs a benchmark with param and returns stdout'
        for bench_suite in self.bench_suites:
            if bench in bench_suite.names:
                return bench_suite.run(bench, param, self.executor)

    def print_header(self):
        'Prints the initial header in the experimental output file'
        if os.path.exists(self.output_file):
            return
        res = ['hostname','fullname','nproc','duration', 'startTime', 'endTime']
        for leverage in self.hw_modes:
            res.extend(leverage.get_labels())
        res.append('hostlist')
        with open(self.output_file, 'w') as output_file:
            output_file.write(' '.join(res)+'\n')

    def monitor_bench(self, bench, param):
        'Runs and monitor the benchmark and then save the results'
        output_time = ''
        self.print_header()
        hw_state = ' '.join([leverage.state_to_str() for leverage in self.hw_modes])
        print('\nstarting ', self.output_file, bench, param, 'at', hw_state)

        while output_time == '':
            time.sleep(5)

            beg_time = int(time.time())
            self.start_monitors()
            output_time, benchname = self.run_bench(bench, param)
            self.stop_monitors()
            end_time = int(time.time())

        result = '%s %s %s %s %s %s ' % (self.executor.hostnames[0], benchname,
                                            self.executor.nbcores, output_time,
                                            beg_time, end_time)
        if hw_state != '':
            result += hw_state+' '
        result += ';'.join(self.executor.hostnames)
        result += '\n'
        with open(self.output_file, 'a') as output_file:
            output_file.write(result)

        self.save_monitors(benchname, beg_time)
        return "%s_%s/%s_%s_%s" % (self.output_file, "%s",
                                   self.executor.hostnames[0],
                                   benchname, beg_time)

def run_experiment(name, benchmarks, leverages=[], monitors=[], sweep=False, times=1):
    """Typical experiment"""
    executor = Executor()

    expe = Experiment(name, executor, benchmarks,
                      monitors=monitors, leverages=leverages)

    for _ in range(times):
        for bench in expe.get_all_benchnames():
            for param in expe.get_params(bench):
                if callable(param):
                    param = param()
                for actions in expe.get_hw_actions():
                    expe.start_actions(actions)
                    pattern = expe.monitor_bench(bench, param)
                    expe.stop_actions(actions, pattern)
    return expe.output_file
