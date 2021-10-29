import pandas as pd

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

