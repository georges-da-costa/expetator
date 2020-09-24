import time
import requests
import os
import json

def get_names():
    return {'powergpu'}

class Power:
    'Monitoring GPU using Power on g5k'
    def __init__(self, lbl='pow'):
        import time
        self.label = lbl
        self.executor = None
        self.names = get_names()
        self.g5k = 'OAR_NODE_FILE' in os.environ
        self.cwd = os.path.dirname(os.path.abspath(__file__))
        now = time.localtime()
        self.df = 'nvstats-%s%s%s-%s' % (now.tm_year, str(now.tm_mon).zfill(2), str(now.tm_mday).zfill(2), self.label)
 
    def build(self, executor):
        ''
        self.executor = executor
 
    def start(self):
        'Starts the monitoring right before the benchmark'
        self.executor.local('nvidia-smi daemon -i 0 -p %s -j %s -d 1' % (self.cwd, self.label), root=True)

    def stop(self):
        'Stops the monitoring right after the benchmark'
        self.executor.local('nvidia-smi daemon -t', root=True)

    def save(self, experiment, benchname, beg_time):
        'Save the results when time is no more critical'
        filename_moj = experiment.output_file+'_mojitos'
        os.makedirs(filename_moj, exist_ok=True)
        target =  '%s/%s_%s_%s' % (filename_moj, self.executor.hostnames[0], benchname, beg_time)
        inpath = self.cwd + '/' + self.df
        outpath = inpath + '.csv'
        self.executor.local('nvidia-smi replay -i 0 -f %s -r %s' % (inpath, outpath))
        with open(outpath) as file_id:
            content = [line.split() for line in file_id.readlines()]
            beg_date = time.strftime('%Y-%m-%d', time.localtime(float(beg_time)))
            lout = []  # lines to save
            hdr = None
            for l in content:
                if hdr is None and l[0].startswith('#T'):
                    hdr = ['timestamp'] + l[1:]
                    lout.append(' '.join(hdr) + '\n')
                if l[0].startswith('#'):
                    continue
                sec = int(time.mktime(time.strptime(beg_date + ' ' + l[0] + ' CEST', '%Y-%m-%d %H:%M:%S %Z')))
                lr = [str(sec)] + l[1:]
                lout.append(' '.join(lr) + '\n')

        with open(target, 'w') as file_id:
            file_id.writelines(lout)

        # delete in the end to keep evidence in case of exception above:
        self.executor.local('rm %s %s' % (inpath, outpath))

