Leverages
=========

Available leverages
-------------------

Most of these leverages only work on Grid5000, and some only on some servers (with GPU for Gpu* for example)

.. autoclass:: expetator.leverages.Dvfs

.. autoclass:: expetator.leverages.GpuClock

.. autoclass:: expetator.leverages.GpuPower

.. autoclass:: expetator.leverages.NeoSched

.. autoclass:: expetator.leverages.Nodeepsleep

.. autoclass:: expetator.leverages.Pct

.. autoclass:: expetator.leverages.Powercap

Example of use of an available leverages :

.. code-block:: python

    import expetator.experiment as experiment
    from expetator.benchmarks import SleepBench
    from expetator.leverages import Dvfs

    experiment.run_experiment("/tmp/dvfs_demo",
                              [ SleepBench(default_time=2) ],
			      leverages = [ Dvfs(baseline=True) ],
                             )

The result will be in a file **/tmp/dvfs_demo_${HOST}_${TIMESTAMP_START}**

	       
How to make your own leverage
-----------------------------

A leverages has an internal list of available state (obtained through the **available_states** member). A state can be a tuple

A classical template would be:

.. code-block:: python
		
    class Template:
        'Template for leverages'
        def __init__(self):
            'Initializes the internal variables using parameters'
            pass

        def build(self, executor):
            'Builds the executable and acquire data on the system'
            self.executor = executor
            pass
    
        def available_states(self):
            'Returns all the possible states as a list'
            return [None]

        def start(self, state):
            'Sets the right state on all hosts'
            pass
        
        def stop(self, output_file=None):
            'Reverts to the standard state on all nodes and saves some info in the right directory'
            pass
            
        def get_state(self):
            'Returns the current state'
            return None

        def state_to_str(self):
            '''Converts the current state in a string
	    If there are several values, they are separated by a white-space'''
            return 'None'

        def get_labels(self):
            'Returns the labels for the leverage as a tuple'
            return ('Template')

Example of leverage
-------------------

Here is an example of a simple leverage that will change the sound ouput level

.. code-block:: python
		
    import expetator.experiment as experiment
    from expetator.benchmarks import SleepBench

    class SoundLevel:

        def __init__(self, levels = [20, 70]):
            self.levels = levels

        def build(self, executor):
            'Builds the executable and acquire data on the system'
            self.executor = executor
            pass
    
        def available_states(self):
            'Returns all the possible states as a list'
            return self.levels

        def start(self, state):
            'Sets the right state on all hosts'
	    self.executor.hosts('pactl set-sink-volume @DEFAULT_SINK@ '+str(state)+'%')
	    self.state = state
            pass
        
        def stop(self, output_file=None):
            'Reverts to the standard state on all nodes and saves some info in the right directory'
            pass
            
        def get_state(self):
            'Returns the current state'
            return self.state

        def state_to_str(self):
            'Converts the current state in a string'
            return str(self.state)

        def get_labels(self):
            'Returns the labels for the leverage'
            return ('level')

    if __name__ == "__main__":
        experiment.run_experiment(
            "/tmp/sound_demo", [SleepBench(default_time=2)],
	    leverages=[SoundLevel()],
        )
