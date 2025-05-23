Monitors
========

Available monitors
------------------

.. autoclass:: expetator.monitors.kwollect.Power

For Grid5000 you can select the most precise wattmeter for you own cluster using the following invocation
```
kwollect.Power(metric=kwollect.get_g5k_target_metric())
```
Example of use of KWollect, ie power monitoring of servers on grid5000.
The result will be in a file **/tmp/power_demo_${HOST}_${TIMESTAMP_START}** and directories starting with **/tmp/power_demo_${HOST}_${TIMESTAMP_START}_power**

.. code-block:: python

    #! /usr/bin/python3
    
    from expetator.benchmarks import SleepBench
    from expetator.monitors import kwollect
    
    import expetator.experiment as experiment
    
    MONITORS = [ kwollect.Power(metric=kwollect.get_g5k_target_metric())
               ]
    BENCHMARKS = [SleepBench(default_time=10)]
    
    experiment.run_experiment('/tmp/power_demo',
                              benchmarks = BENCHMARKS,
                              monitors = MONITORS,
                             )


.. autoclass:: expetator.monitors.lperf.Lperf

.. autoclass:: expetator.monitors.mojitos.Mojitos

Example of use of MojitO/S with RAPL, system load, and ethernet network. 
The result will be in a file **/tmp/mojitos_demo_${HOST}_${TIMESTAMP_START}** and directories starting with **/tmp/mojitos_demo_${HOST}_${TIMESTAMP_START}_mojitos**

.. code-block:: python

    #! /usr/bin/python3

    from expetator.benchmarks import SleepBench
    from expetator.monitors import mojitos

    import expetator.experiment as experiment

    MONITORS = [ mojitos.Mojitos(sensor_set = {'dram0', 'load', 'rxp'})
               ]
    BENCHMARKS = [SleepBench(default_time=10)]
    
    experiment.run_experiment('/tmp/mojitos_demo',
                              benchmarks = BENCHMARKS,
                              monitors = MONITORS,
                             )
	       
.. autoclass:: expetator.monitors.powergpu.Power


Example of use of an available benchmark :

.. code-block:: python

    import expetator.experiment as experiment
    from expetator.benchmarks import SleepBench
    from expetator.monitors import Mojitos

    experiment.run_experiment("/tmp/mojitos_demo",
                              [ SleepBench(default_time=2) ],
			      monitors = [ Mojitos(sensor_set={'user'})]
                             )

The result will be in a file **/tmp/mojitos_demo_${HOST}_${TIMESTAMP_START}** and directories starting with **/tmp/mojitos_demo_${HOST}_${TIMESTAMP_START}_\***
	       
How to make your own monitor
----------------------------

A monitor is an object with the following properties
 * The constructor can take parameters (such as the elements to monitor or the frequency)
 * The **build** method must build, configure, install packages using **executor**. Resulting binaries must be put in **/tmp/bin** which will be copied on all nodes
 * The **start** method must start the monitor while the **stop** one must stop it. These two methods must be fast and run the processes in background
 * The **save** method is invocated later when all monitors are stoped anc is used to retrive the data.


All monitors will **start** in parallel just prior running the benchmark and will **stop** just after.

Example of monitor
------------------

Here is an example of a simple benchmark in a file **demo_monitor.py**

.. code-block:: python

    import os

    import expetator.experiment as experiment
    from  expetator.benchmarks import SleepBench

    class DemoMonitor:
        def __init__(self, c_code = 'monitor.c'):
            self.c_code = c_code
            self.executor = None
            self.cmd_line = None

        def build(self, executor):
            executor.local('gcc -o /tmp/bin/monitor %s' % self.c_code)
            self.executor = executor
            self.cmdline = '/tmp/bin/monitor > /dev/shm/mon &'
    
        def start(self):
            'Starts the monitoring right before the benchmark'
            self.process = self.executor.hosts(self.cmdline, background=True)

        def stop(self):
            'Stops the monitoring right before the benchmark'
            self.process.kill()

        def save(self, experiment, benchname, beg_time):
            'Save the results when time is no more critical'
            directory = experiment.output_file+'_monitoring_demo'
            os.makedirs(directory, exist_ok=True)
            if len(self.executor.hostnames) > 1:
                for hostname in self.executor.hostnames:
                    self.executor.local('oarcp %s:/dev/shm/mon %s/%s_%s_%s' %
                                        (hostname, directory, hostname, benchname, beg_time))
            else:
                self.executor.local('cp /dev/shm/mon %s/%s_%s_%s' %
                                        (directory, 'localhost', benchname, beg_time))

    if __name__ == "__main__":
        experiment.run_experiment(
            "/tmp/demo", [SleepBench(default_time=2)],
    	    monitors=[DemoMonitor()],
        )

With the following benchmark code in a file **monitor.c** in the same directory

.. code-block:: C

    #include <stdio.h>
    #include <unistd.h>

    int main() {
        for(unsigned int i=0; ; i++) {
            sleep(.1);
            printf("%d\n", i);
        }
    }
