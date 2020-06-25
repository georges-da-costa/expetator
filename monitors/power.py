import time
import requests
import os
import json

def get_names():
    return {'power'}

class Power:
    'Monitoring using Power on g5k'
    def __init__(self):
        self.hostnames = None
        self.site = None
        self.start_time = None
        self.end_time = None
        self.executor = None
        self.names = get_names()
        self.g5k = 'OAR_NODE_FILE' in os.environ
        self.local_script = '%s/laptop_power_monitor.py &' % os.path.dirname(os.path.abspath(__file__))
        
    def build(self, executor):
        """Prepare the right request only needed on g5k"""
        if self.g5k:
            self.hostnames = ','.join([fullname.split('.')[0] for fullname in executor.hostnames])
            self.site = executor.hostnames[0].split('.')[1]
        self.executor = executor
        
    def start(self):
        'Starts the monitoring right before the benchmark'
        if self.g5k:
            self.start_time = int(time.time())
        else:
            self.executor.local(self.local_script)
            
    def stop(self):
        'Stops the monitoring right after the benchmark'
        if self.g5k:
            self.end_time = int(time.time())
        else:
            self.executor.local('killall laptop_power_monitor.py')

    def save(self, experiment, benchname, beg_time):
        'Save the results when time is no more critical'
        filename_power = experiment.output_file+'_power'
        os.makedirs(filename_power, exist_ok=True)
        target =  '%s/%s_%s_%s' % (filename_power, self.executor.hostnames[0], benchname, beg_time)
        if self.g5k:

            request = 'https://api.grid5000.fr/stable/sites/%s/metrics/power/timeseries?resolution=1&only=%s&from=%s&to=%s' % (self.site, self.hostnames, self.start_time, self.end_time)
            time.sleep(5)
            res = requests.get(request)

            
            if res.status_code == 200:
                data = res.text
                raws = json.loads(data)['items']

                result = [(raw['uid'], raw['timestamps'],raw['values']) for raw in raws]
        else:
            self.executor.local('cp /dev/shm/power_measures %s' % target)
            with open('/dev/shm/power_measures') as file_id:
                content = [line.split() for line in file_id.readlines()[1:]]
            content = [(int(t), float(p)) for t,p in content]
            result = [('localhost',)+tuple(zip(*content))]

        with open(target, 'w') as file_id:
            file_id.write(json.dumps(result))
