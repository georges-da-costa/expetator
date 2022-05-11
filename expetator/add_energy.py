#! /usr/bin/python3

import sys
import scipy.integrate as integrate
from statistics import mean, median

import expetator.bundle as bundle
import expetator.monitoring_list as monitoring_list

import matplotlib.pyplot as plt

def add_energy(basename, bundle_data=None, zip_fid=None):
    if bundle_data is None:
        bundle_data, zip_fid = bundle.init_bundle(basename)

    power = monitoring_list.read_bundle_list('power', bundle_data, zip_fid)
    
    energy = []
    delta = []
    mean_power = []
    med_power = []
    
    for experiment in power:
        expe_energy = 0
        expe_delta = 0
        expe_power = []
        try:
            for power_profile in experiment:
                tmp_delta = max(power_profile['#timestamp']) - min(power_profile['#timestamp'])
                expe_delta = max(expe_delta, tmp_delta)
        
                expe_energy += integrate.trapz(power_profile['power'], x=power_profile['#timestamp'])
                
                expe_power.extend(power_profile['power'])
        except:
            pass
        if expe_power == []:
            expe_energy = -1
            expe_delta = -1
            expe_power = [-1]

        energy.append(expe_energy)
        delta.append(expe_delta)
        mean_power.append(mean(expe_power))
        med_power.append(median(expe_power))
        
    bundle_data['energy'] = energy
    bundle_data['time'] = delta
    bundle_data['mean_power'] = mean_power
    bundle_data['median_power'] = med_power

    return(bundle_data)

def main():
    basename = sys.argv[1]
    bundle_data = add_energy(basename)

    bundle_data.to_csv(basename+".csv", sep=' ', index=False)

if __name__ == "__main__":
    main()
