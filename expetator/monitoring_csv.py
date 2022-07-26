import os
import pandas as pd
import matplotlib.pyplot as plt
import sys


def _read_csv(filename):
    df = pd.read_csv(filename, sep=' ', skipinitialspace=True)
    if df.columns[-1].startswith('Unnamed'):
        df.drop(columns=df.columns[-1:], axis=1, inplace=True)
    return df



def read_host_csv(prefix, hostname, startTime, basename, fullname, archive_fid=None):
    fullpath= '%s_%s/%s_%s_%s' % (basename, prefix, hostname, fullname, startTime)
    if archive_fid is None:
        if not os.path.exists(fullpath):
            fullpath = '%s_%s/%s_%s_%s' % (basename, prefix, 'localhost', fullname, startTime)
        with open(fullpath) as file_id:
            data = _read_csv(fullpath)
    else:
        if not fullpath in archive_fid.namelist():
            fullpath = '%s_%s/%s_%s_%s' % (basename, prefix, 'localhost', fullname, startTime)
        with archive_fid.open(fullpath) as file_id:
            data = _read_csv(file_id)
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

    a = _read_csv(filename)
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
