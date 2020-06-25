import json
from statistics import median, mean
from scipy.stats import trim_mean
import shutil
import os
import bisect

import requests
from IPython.display import clear_output

import pandas as pd
import zipfile

import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
import random


def best_freqs(df, groupname, group_label='fullname', metric='etp', leverage_name='fmax', ratio=1.05):
    local_df = df[df[group_label] == groupname].groupby(leverage_name).mean().reset_index()
    value = min(local_df[metric])
    optimal = list(local_df[local_df[metric]==value][leverage_name])[0]
    return optimal, set(local_df[local_df[metric]<=ratio*value][leverage_name])

def target_freq(buffer, freq, fullname, stay_is_zero=True):
    optimal_freq, frequencies = buffer[fullname]
    if freq in frequencies:
        if stay_is_zero:
            return 0
        else:
            return freq
    return optimal_freq

def add_objectives(df, objective_name='target', group_label='expe', metric='etp', ratio=1.05, stay_is_zero=True):
    buffer = {label:best_freqs(df,label, group_label=group_label, metric=metric, ratio=ratio) for label in df[group_label]}
    df[objective_name] = df.apply(lambda row: target_freq(buffer, row.fmax, row[group_label], stay_is_zero=stay_is_zero), axis=1)
    reachable_frequencies = {opti for opti,_ in buffer.values()}
    return reachable_frequencies



def colormap(val, percentage_limit):
    ratio = 100/percentage_limit
    red = min(1, max(0, ratio*val))
    return (red, 1-red, 0)

def show_graph(name, vect, colors, frequencies, spread=30000):
    f=plt.figure(figsize=(25,6))
    plt.ylabel(name)
    plt.xlabel("Frequency")
    freqs = [frequencies[i] for i,v in enumerate(vect) if v > 0]
    cols  = [colors[i] for i,v in enumerate(vect) if v > 0]
    plt.scatter([freq+random.randint(-spread,spread) for freq in freqs], 
                [v for v in vect if v>0] ,
                c= cols, marker='*')
    
def show_pct_distribution(vectors, knowledge, metric_name='etp', percentage_limit=10, key_label='fullname'):    
    metric = [colormap(row[metric_name]/min(knowledge[knowledge[key_label]==row[key_label]][metric_name])-1, percentage_limit) 
              for _,row in knowledge.iterrows()]

    for hw_pct in vectors:
        show_graph(hw_pct, vectors[hw_pct], metric, knowledge.fmax)

def show_heatmap(knowledge, x='fmax',y='fullname', metric='duration'):
    optimals=knowledge.groupby([x,y]).mean().groupby(y)
    optimals=optimals[metric]
    optimals=optimals.apply(list).apply(pd.Series)
    optimals.columns=knowledge[x].unique()
    optimals.style.background_gradient(cmap='Reds', axis=1)
    optimals =optimals.style.background_gradient(cmap='Reds', axis=1)
    return optimals

def get_monitoring_power(hostname, startTime, basename, fullname, hostlist=None, archive_fid=None):

    fullpath= '%s_power/%s_%s_%s' % (basename, hostname, fullname, startTime)
    if archive_fid is None:
        with open(fullpath) as file_id:
            data = json.loads(file_id.read())
    else:
        with archive_fid.open(fullpath) as file_id:
            data = json.loads(file_id.read())

    if hostlist is None:
        hostlist = hostname.split('.')[0]
    _data = [ (t,p) for (h, t, p) in data if h == hostlist]

    return _data[0]

def get_monitoring_mojitos(hostname, startTime, basename, fullname, hostlist=None, archive_fid=None):
    fullpath= '%s_mojitos/%s_%s_%s' % (basename, hostname, fullname, startTime)
    if archive_fid is None:
        with open(fullpath) as file_id:
            data = clean_dataframe(pd.read_csv(fullpath,sep=' '))
    else:
        with archive_fid.open(fullpath) as file_id:
            data = clean_dataframe(pd.read_csv(file_id,sep=' '))

    if '0' in data:
        data=data.drop('0', axis=1)
    if '1' in data:
        data=data.drop('1', axis=1)
    return data

def read_experiment(filenames, only_complete=False, keep_only=None):
    if type(filenames) is str:
        filenames = [filenames]

    archive_fid={}
    tmp_knowledge = []
    for basename in filenames:
        if basename.endswith('.zip'):
            tmp_fid = zipfile.ZipFile(basename, 'r')
            filenames = [ fid for fid in tmp_fid.infolist()
                          if not '/' in fid.filename]
            basename = filenames[0].filename
            archive_fid[basename] = tmp_fid

            k = pd.read_csv(tmp_fid.open(filenames[0]), sep=' ')
        
        else:
            archive_fid[basename] = None
            k = pd.read_csv(basename, sep=' ')
        k['basename'] = basename

        if not keep_only is None:
            k=k[k['fullname'].str[:3].isin(keep_only)].reset_index(drop=True)

        if only_complete:
            nb_lev = len(k.fmax.unique())
            nb_expe = len(k) // nb_lev
            k = k[:nb_expe*nb_lev]

        tmp_knowledge.append(k)
    knowledge = pd.concat(tmp_knowledge, ignore_index=True)
    
    if only_complete:
        nb_lev = len(knowledge.fmax.unique())
        nb_expe = len(knowledge) // nb_lev
        ids_expe = [[i]*nb_lev for i in range(nb_expe)]
        knowledge['expe'] = [j for i in ids_expe for j in i]
    
    try:
        knowledge['power'] =  knowledge.apply(lambda row: mean(
            get_monitoring_power(row.hostname, row.startTime, row.basename, row.fullname, archive_fid=archive_fid[row.basename])[1][4:]
        ), axis=1)

        knowledge['energy']=knowledge.apply(lambda row: row.duration*row.power, axis=1)
        
        knowledge['etp']=knowledge.apply(lambda row: row.duration*row.energy, axis=1)
    except: # no energy monitoring associated
        print("No energy data")
        pass
    
    try:
        mojitos_data = [get_monitoring_mojitos(row.hostname, row.startTime, row.basename, row.fullname, archive_fid=archive_fid[row.basename]) for index, row in knowledge.iterrows()]
    except: # no monitoring associated
        mojitos_data = []
        
    for _, tmp_fid in archive_fid.items():
        if not tmp_fid is None:
            tmp_fid.close()
        
    return knowledge, mojitos_data


def find_le(elements, value):
    'Find rightmost value in elements less than or equal to value'
    position = bisect.bisect_right(elements, value)
    return elements[position-1]

def get_power_local(start, end, debug=False):
    'To use with a local powermeter link in laptops'
    directory = 'local_powermeter'
    file_list = sorted([int(filename) for filename in os.listdir(directory)])
    file_name = find_le(file_list, start)

    with open(directory+'/'+str(file_name)) as file_id:
        raw_data = [line.split() for line in file_id.readlines()]
    power_data = [(int(timestamp), float(power)) for (timestamp, power) in raw_data
                  if int(timestamp) >= start and int(timestamp) <= end]

    timestamps, values = zip(*power_data)

    res = {"items":[{"timestamps":timestamps, "values":values}]}
    data = json.dumps(res)
    if debug:
        print(data)
    return data

def get_power_g5k(host, site, start, end, password, debug):
    'Gets the power from nodes of Grid5000'
    request = 'https://api.grid5000.fr/stable/sites/%s/metrics/power/timeseries?resolution=1&only=%s&from=%s&to=%s' % (site, host, start, end)
    if debug:
        print(request)
        print(password)
    res = requests.get(request, auth=password)

    data = res.text
    if debug:
        print(data)
    if res.status_code != 200:
        print("problem to access api.grid5000.fr")
        print(res.text)
        return None
    return data


from cryptography.fernet import Fernet
import getpass

def get_g5k_password():
    try:
        with open('/home/gdacosta/.gdacosta/g5k.key', 'rb') as file:
            key = b'lsB2BLQ9vZ1uVMu7EwW6jTgzX8RyM1bA3obHNbPyWOE='
            f = Fernet(key)
            secret=file.read()
        return ('gdacosta', f.decrypt(secret).decode())
    except:
        return (input('Login on Grid5000'), getpass.getpass('password on Grid5000'))

def get_power(hostname, start, end, password='', debug=False, cachedir='cache', copydest=None):
    'Generic method to obtain the power of a benchmark, either on g5k or local'
    try:
        host, site, _, _ = hostname.split('.')
    except:
        host, site = hostname, 'local'

    if debug:
        print('Get_Power', hostname, start, end)
    try:
        source = '%s/%s_%s_%s_%s' %(cachedir, host, site, start, end)
        if debug:
            print(source)
        with open(source, 'r') as file:
            data = file.read()
        if debug:
            print('file found')
        if not copydest is None:
            shutil.copy(source, copydest)
            if debug:
                print('file copied in ', copydest)
    except:
        if site == 'local':
            data = get_power_local(start, end, debug)
        else:
            data = get_power_g5k(host, site, start, end, password, debug)

    if not data is None:
        with open('%s/%s_%s_%s_%s' %(cachedir, host, site, start, end), 'w') as file:
            file.write(data)

    raw = json.loads(data)['items'][0]
    timestamps = raw['timestamps']
    values = raw['values']
    if len(values) == 0:
        return None
    return timestamps, values

def power_to_energy(timestamps, power):
    'Approximates missing timestamps'
    mu = median([timestamps[i+1]-timestamps[i] for i in range(len(timestamps)-1)])

    energy = power[0] * mu/2

    for tidx in range(len(timestamps)-1):
        delta = timestamps[tidx+1]-timestamps[tidx]
        energy += (power[tidx]+power[tidx+1])*(delta)/2

    energy += power[-1]*mu/2
    return energy

def get_energy(hostname, start_time, end_time, password='', debug=False):
    'Retunrs the energy consumed during an experiment'
    (timestamps, values) = get_power(hostname, start_time, end_time, password, debug)
    return power_to_energy(timestamps, values)

def update_progress(progress):
    'progress bar for jupyter notebook'
    bar_length = 20
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >= 1:
        progress = 1

    block = int(round(bar_length * progress))

    clear_output(wait=True)
    text = "Progress: [{0}] {1:.1f}%".format("#"*block + "-"*(bar_length - block), progress*100)
    print(text)

def clean_dataframe(dataframe):
    'Removes unuseful values'
    dataframe = dataframe.dropna(axis='columns').drop(["#timestamp"], axis=1)
    return dataframe

def normalize_dataframe(dataframe):
    'removes unuseful values and normalize the remaining values between 0 and 1'
    tmp = (dataframe-dataframe.min())/(dataframe.max()-dataframe.min())
    return clean_dataframe(tmp)

from sklearn.feature_selection import VarianceThreshold
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Cleaning the data
## Helper functions
def get_unused_features(dataset, debug=False, threshold_pca=1e-5):
    # Create a PCA that will retain 90% of the variance
    pca = PCA(n_components=.9, svd_solver = 'full', whiten=True)
    X = StandardScaler().fit_transform(dataset)
    X_pca = pca.fit_transform(X)

    # Returs the vector of the base un function of the input features
    rho = pd.DataFrame(pca.components_,columns=dataset.columns)

    # Sums the absolute contribution of each feature to each vector weighted by the
    # importance of the vector
    variables = abs(rho).T.dot(pca.explained_variance_ratio_).sort_values(ascending=False)

    unused_features = variables[variables <= threshold_pca]
    if debug:
        print(variables)
        print('Number of unused features', len(unused_features), ', names:', unused_features)

    return set(unused_features.index)

def get_correlated_features(dataset, debug=False, threshold=.99):
    corr = dataset.corr()
    corr = corr.stack()
    corr = corr[corr.index.get_level_values(0) < corr.index.get_level_values(1)]
    corr = corr[abs(corr)>=threshold]
    if debug:
        print(corr)
    return {name for (_, name) in corr.index}

import numpy as np
def get_constant_features(dataset, threshold=.01):
    constant_filter = VarianceThreshold(threshold=threshold)
    constant_filter.fit(dataset)
    return set(dataset.columns[np.logical_not(constant_filter.get_support())])

## Exported function
def prune_vectors(vectors):
    constant_features_agg = get_constant_features(vectors)
    unused_features_agg = get_unused_features(vectors)
    correlated_features_agg = get_correlated_features(vectors)

    removed_pct = unused_features_agg | correlated_features_agg | constant_features_agg
    return vectors.drop(unused_features_agg | correlated_features_agg | constant_features_agg, axis=1)

# Read the dataset
def mojitos_to_vectors(mojitos_data, knowledge, proportiontocut=.1):
    tmp = pd.DataFrame([ trim_mean(bench_run, proportiontocut=proportiontocut) for bench_run in mojitos_data],
                      columns = mojitos_data[0].columns)
    tmp['freq'] = knowledge.fmax
    return tmp



