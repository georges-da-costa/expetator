#!/usr/bin/python3

import time
import os
import sys
import signal

def read_int(filename):
    """Read integer from file filename"""
    with open(filename) as file_id:
        return int(file_id.readline())

def handler(arg):
    stay=False
    
signal.signal(15, handler)
    
stay=True

with open('/dev/shm/power_measures','w') as power_file:
    power_file.write('#timestamp power\n')

try:
    while stay:
        mili_volt=read_int('/sys/class/power_supply/BAT0/voltage_now')
        mili_ampere=read_int('/sys/class/power_supply/BAT0/current_now')
        watt = mili_volt*mili_ampere/1000000000000
    
        current_time=time.time()
        int_current_time=int(current_time)
    
        with open('/dev/shm/power_measures','a') as power_file:
            power_file.write(str(int_current_time)+' '+str(watt)+'\n')
        time.sleep(1-(current_time-int_current_time))
except:
    pass

