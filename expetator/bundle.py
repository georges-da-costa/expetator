import pandas as pd
import numpy as np
import json

def init_bundle(bundlename):
    'Reads an experiment file'
    if bundlename.endswith('.zip'):
        zip_fid = zipfile.ZipFile(bundlename, 'r')
        bundlename = bundlename[:-4]
        experiments = pd.read_csv(zip_fid.open(bundlename), sep=' ')
    else:    
        zip_fid = None
        experiments = pd.read_csv(bundlename, sep=' ')
    
    experiments['basename'] = bundlename
    return experiments, zip_fid

def merge_timeseries_blocks(references, additions, prefix = 'add_', key='#timestamp'):
    return [
        [
            merge_timeseries(references[experiment_id][host_id],
                             additions[experiment_id][host_id],prefix, key)
            for host_id in range(len(references[experiment_id]))
        ]
        for experiment_id in range(len(references))
    ]

def merge_timeseries(reference, addition, prefix = 'add_', key='#timestamp'):
    reference = reference.copy()
    
    delta = reference[key][0] - addition[key][0]
    intermediate_timestamps = reference[key]-delta
    
    for column in addition:
        if column != key:
            new_name = prefix+addition[column].name
            
    
            data = np.interp(intermediate_timestamps, addition[key], addition[column])

            reference[new_name] =data

    return reference

    delta_ref = reference[key][0]
    span_ref = max(reference[key]) - reference[key][0]
    delta_add = addition[key][0]
    span_add = max(addition[key]) - addition[key][0]
    
    print(delta_ref, span_ref)
    print(delta_add, span_add)

def normy(focus):
    df = focus.loc[:, focus.columns != '#timestamp']
    norm_focus=(df-df.min())/(df.max()-df.min())
    norm_focus['#timestamp'] = focus['#timestamp']
    return norm_focus
    
