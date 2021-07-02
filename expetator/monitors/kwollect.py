import time
import datetime
import requests
import os
import json

def get_names():
    return {'kwollect'}

class Power:
    'Monitoring using Kwollect on g5k'
    def __init__(self, metric = 'wattmetre_power_watt'):
        self.hostnames = None
        self.site = None
        self.start_time = None
        self.end_time = None
        self.executor = None
        self.names = get_names()
        self.metric = metric
        
    def build(self, executor):
        """Prepare the right request only needed on g5k"""
        self.hostnames = ','.join([fullname.split('.')[0] for fullname in executor.hostnames])
        self.site = executor.hostnames[0].split('.')[1]
        self.executor = executor
        
    def start(self):
        'Starts the monitoring right before the benchmark'
        self.start_time = int(time.time())
            
    def stop(self):
        'Stops the monitoring right after the benchmark'
        self.end_time = int(time.time())

    def save(self, experiment, benchname, beg_time):
        'Save the results when time is no more critical'
        filename_power = experiment.output_file+'_power'
        os.makedirs(filename_power, exist_ok=True)
        target =  '%s/%s_%s_%s' % (filename_power, self.executor.hostnames[0], benchname, beg_time)

        request = 'https://api.grid5000.fr/stable/sites/%s/metrics?metrics=%s&start_time=%s&end_time=%s&nodes=%s' % (self.site, self.metric, self.start_time, self.end_time, self.hostnames)

        delta = int(time.time())-self.end_time
        if delta < 6:
            time.sleep(6-delta)

        res = requests.get(request)

        data = res.text
        
        raws = json.loads(data)
        host_list = self.hostnames.split(',')
        
        timestamps = {host:[] for host in host_list}
        values = {host:[] for host in host_list}
        for elements in raws:
            device_id = elements['device_id']
            try:
                timestamps[device_id].append(datetime.datetime.strptime(elements['timestamp'], "%Y-%m-%dT%H:%M:%S%z").timestamp())
            except:
                timestamps[device_id].append(datetime.datetime.strptime(elements['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z").timestamp())

            values[device_id].append(elements['value'])
        result = [(host, timestamps[host], values[host]) for host in host_list]

        with open(target, 'w') as file_id:
            file_id.write(json.dumps(result))
