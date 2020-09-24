import json
import os

###### ! to move to executor
import execo

from expetator.leverages import dvfs
from expetator.monitors import mojitos

def save_scheduler(code_elements, skel_path, output_path, debug=False):
    name, arguments, nb_arguments, pcts, code = code_elements

    with open(skel_path) as file:
        content = file.read()

    content = content.replace('//DEFINE PCT', pcts)
    content = content.replace('ARGUMENTS;', arguments, 1)
    content = content.replace('NBARGUMENTS;', nb_arguments, 1)
    content = content.replace('//CORE_LOOP', code)

    if debug:
        print(content)
    with open(output_path, 'w') as file:
        file.write(content)    

class NeoSched(dvfs.Dvfs):
    def __init__(self, schedulers, dummy=False, baseline=False):
        dvfs.Dvfs.__init__(self, dummy=dummy, baseline=baseline)
        self.schedulers = {}

        for file_sched in schedulers:
            with open(file_sched) as file_id:
                element = json.load(file_id)
                self.schedulers[element[0]] = element

        self.names = list(self.schedulers)
    
    def build(self, executor):
        dvfs.Dvfs.build(self, executor)
        self.available_frequencies = self.names + self.available_frequencies
        moj = mojitos.Mojitos()
        moj.build(executor)
        basedir = os.path.dirname(os.path.abspath(__file__))
        executor.local('cp -f %s/neosched_* /tmp/mojitos/' % basedir)

        executor.local('mkdir -p /tmp/neosched')
        for scheduler in self.names:
            save_scheduler(self.schedulers[scheduler], '/tmp/mojitos/neosched_skel.c',
                           '/tmp/mojitos/neosched_lib.c')

            executor.local('cd /tmp/mojitos; make -f neosched_mak')
            executor.local('cp -f /tmp/mojitos/neosched /tmp/neosched/%s' % scheduler)

        executor.sync('/tmp/neosched')
        self.algorithm = 0

    def start(self, freq):
        self.algorithm = freq
        if freq in self.schedulers:
            print('starts /tmp/neosched/%s' %freq)
            self.remote=execo.action.Remote('/tmp/neosched/%s' % freq,
                                            self.executor.hostnames,
                                            connection_params={'ssh':self.executor.ssh}).start()
        else:
            dvfs.Dvfs.start(self, freq)

    def stop(self, output_file = None):
        if self.algorithm in self.schedulers:
            execo.action.Remote('killall /tmp/neosched/%s' %
                                self.algorithm,
                                self.executor.hostnames,
                                connection_params={'ssh':self.executor.ssh}).run()
            self.remote.wait()

            if not output_file is None:
                dest = output_file % 'neosched'
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                self.executor.local('mv /dev/shm/neosched.data %s' % dest)

        dvfs.Dvfs.stop(self, output_file)

    def get_state(self):
        if self.algorithm in self.schedulers:
            return (0, self.algorithm)
        else:
            return dvfs.Dvfs.get_state(self)
