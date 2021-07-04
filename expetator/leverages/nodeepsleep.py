import os

source_script = """#!/usr/bin/python3

import signal
import os

def signal_handler(signal_number, frame):
    os.close(fd)

fd = os.open("/dev/cpu_dma_latency", os.O_RDWR)
os.write(fd, b'\\0\\0\\0\\0')

signal.signal(signal.SIGINT, signal_handler)
signal.pause()
"""

terminate_script = """#!/bin/bash
ps aux | grep script_nodeepsleep.py | grep sudo | awk '{print $2}' | xargs sudo-g5k kill
"""

class Nodeepsleep:
    'Activates or deactivates CX'
    def __init__(self, modes = {True, False}):
        self.modes = modes
        self.binary = '/tmp/bin/script_nodeepsleep.py'
        self.terminate = '/tmp/bin/terminate_nodeepsleep.py'
        self.cur_mode = False
        
    def build(self, executor):
        'Builds the software'
        self.executor = executor
        with open(self.binary, 'w') as out_file:
            out_file.write(source_script)
        os.chmod(self.binary, 0o777)

        with open(self.terminate, 'w') as out_file:
            out_file.write(terminate_script)
        os.chmod(self.terminate, 0o777)
        
    def available_states(self):
        'Returns all the modes'
        return self.modes

    def start(self, mode):
        'Sets the right mode on all hosts'
        self.curr_mode = mode
        if mode:
            self.executor.hosts(self.binary+' &', root=True)

    def stop(self, output_file=None):
        'Stops the script'
        if self.curr_mode:
            self.executor.hosts(self.terminate, root=True)
        self.curr_mode = False
            
    def get_state(self):
        'Returns the current state'
        return self.curr_mode

    def state_to_str(self):
        'Returns the current state as a string'
        return '%s' % self.curr_mode

    def get_labels(self):
        'Returns the label for the C0 state'
        return ('C0only', )
