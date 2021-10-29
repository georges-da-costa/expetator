import json
import pandas as pd

## Power
def read_run_list(prefix, hostname, startTime, basename, fullname, hostlist=None, archive_fid=None):
    fullpath= '%s_%s/%s_%s_%s' % (basename, prefix, hostname, fullname, startTime)
    result = []

    try:
        if archive_fid is None:
            with open(fullpath) as file_id:
                raw_data = json.loads(file_id.read())
        else:
            with archive_fid.open(fullpath) as file_id:
                raw_data = json.loads(file_id.read())
    
        data = {host:(timestamp, values) for (host, timestamp, values) in raw_data}
    
        for host in hostlist.split(';'):
            name, _ = host.split('.', maxsplit=1)
            df = pd.DataFrame(list(data[name])).transpose()
            df.columns = ["#timestamp", prefix]
            result.append(df)
    except:
        pass
    
    return result

def read_bundle_list(prefix, bundle, archive_fid=None):
    'Reads the power files associated to a bundle'    
    list_data = [read_run_list(prefix, row.hostname, row.startTime, row.basename, row.fullname, row.hostlist, archive_fid) 
                    for index, row in bundle.iterrows()]
    return list_data

