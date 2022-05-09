import os
import pandas as pd
import matplotlib.pyplot as plt
import sys

def read_host_csv(prefix, hostname, startTime, basename, fullname, archive_fid=None):
    fullpath= '%s_%s/%s_%s_%s' % (basename, prefix, hostname, fullname, startTime)
    if archive_fid is None:
        with open(fullpath) as file_id:
            data = pd.read_csv(fullpath,sep=' ', skipinitialspace=True)
    else:
        with archive_fid.open(fullpath) as file_id:
            data = pd.read_csv(file_id,sep=' ')
    data = data.dropna(axis='columns')
    return data

def read_run_csv(prefix, hostname, startTime, basename, fullname, hostlist, archive_fid=None):
    return [read_host_csv(prefix, host, startTime, basename, fullname, archive_fid) for host in hostlist.split(';')]
       
def read_bundle_csv(prefix, bundle, archive_fid=None):
    'Reads mojitO/S-like files associated to a bundle'
    csv_data = [read_run_csv(prefix, row.hostname, row.startTime, row.basename, row.fullname, row.hostlist, archive_fid) 
                    for index, row in bundle.iterrows()]
    return csv_data




def write_host_csv(prefix, hostname, startTime, basename, fullname, data, target_directory):
    fullpath= '%s/%s_%s/%s_%s_%s' % (target_directory, basename, prefix, hostname, fullname, startTime)
    os.makedirs('%s/%s_%s' % (target_directory, basename, prefix), exist_ok=True)

    data.to_csv(fullpath,sep=' ', index=False)


def write_run_csv(prefix, hostname, startTime, basename, fullname, hostlist, data, target_directory):
    for index, host in enumerate(hostlist.split(';')):
        write_host_csv(prefix, host, startTime, basename, fullname, data[index], target_directory)


def write_bundle_csv(prefix, bundle, data, target_directory):
    for index, row in bundle.iterrows():
        write_run_csv(prefix, row.hostname, row.startTime, row.basename, row.fullname, row.hostlist, data[index], target_directory) 

def show_csv(filename, norm=False):
    filename = sys.argv[-1]

    a = pd.read_csv(filename, sep = " ")
    a['#timestamp'] = a['#timestamp']-a['#timestamp'][0]
    if norm:
        tmp = (a/a.max())
        tmp['#timestamp'] = a['#timestamp']
        a = tmp
    a.plot(x='#timestamp')
    plt.show(block=True)

def show_csv_main():
    filename = sys.argv[-1]
    norm = len(sys.argv) == 3
    show_csv(filename, norm)
