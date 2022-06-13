Benchmarks
==========

Available benchmarks
--------------------

.. autoclass:: expetator.benchmarks.CpuBench

.. autoclass:: expetator.benchmarks.GenericBench

.. autoclass:: expetator.benchmarks.GpuCpuBench

.. autoclass:: expetator.benchmarks.GpuMemBench

.. autoclass:: expetator.benchmarks.GromacsBench

.. autoclass:: expetator.benchmarks.MemBench

.. autoclass:: expetator.benchmarks.MpiBench

.. autoclass:: expetator.benchmarks.NpbBench

.. autoclass:: expetator.benchmarks.PercentageBench

.. autoclass:: expetator.benchmarks.SleepBench

.. autoclass:: expetator.benchmarks.WaterMark

Example of use of an available benchmark :

.. code-block:: python

    import expetator.experiment as experiment
    from expetator.benchmarks import SleepBench

    experiment.run_experiment("/tmp/sleep_demo",
                              [ SleepBench(default_time=2) ]
                             )

The result will be in a file **/tmp/sleep_demo_${HOST}_${TIMESTAMP_START}**

	       
How to make your own benchmark
------------------------------

A benchmark is an object with the following properties
 * The constructor takes some parameters to configure the particular instance of the benchmark. It can be a duration, an amount of work, an internal parameter. It can also be several of each. It can be a list of duration for example.
 * The only required members is **self.names**
   * **self.names** is the name of the benchmark. If the object provides several benchmarks, they are provided here
 * The builder (**build** method) must build the benchmark, download necessary files, install packages, ... All the shared elements must be put in */tmp/bin* which will be copied on all nodes. To do so it can use **executor** which provides tools to run applications on the main node or on all nodes, and provides informations such as number of cores. It must also return the list of parameters.
 * The benchmark itself must return *EXIT_SUCCESS*
 * The **run** method will take the name of a benchmark, a parameter and will run it. It must return a couple with the performance and the name of this particular benchmark and this parameter.

The workflow will be the following:
  * First the benchmark is build using **build** method which returns the *parameters*
  * Then, it is run:
    
    * For each name in **names**
      
      * For each parameter associated with the name in the dictionary returned by **build**

	* The method **run** is called with the corresponding parameters
	* Each run will create a new line in the output file including the value returned by **run** which should be a couple *(performance, benchmark_name and parameters)*


Example:
  If **bench.names = {'b1', 'b2'}** and builds returns **{'b1':[1], 'b2':[4,8]}** then expetator will call one after the other:

  * bench.run('b1', 1, executor)
  * bench.run('b2', 4, executor)
  * bench.run('b2', 8, executor)

**executor** is used to run the benchmark on the main node, on all nodes, ...

Example of benchmark
--------------------

A benchmark is an object providing methods to be built and executed.

Here is an example of a simple benchmark in a file **demo_bench.py**

.. code-block:: python

    import expetator.experiment as experiment

    class DemoBench:
        """Demo benchmark. To run,
        python3 bench_exemple.py
        with the file demo.c in the same directory"""

        def __init__(self, params=[30]):
            self.names = {"demo"}
            self.params = params

        def build(self, executor):
            """Builds the demo benchmark in /tmp/bin/ and
            returns the parameters used during execution
            as a dictionary linking elements from self.names
            with a list of parameters to pass during execution.
            Returns a couple (performance, unique_name).
            unique_name will be the part identifying the
            execution and is usually composed of the benchmark
            name and the parameters"""

            executor.local("gcc demo.c -o /tmp/bin/demo")

            params = {"demo": self.params}
            return params

        def run(self, bench, param, executor):
            """Runs the cpu benchmark. bench comes from
            self.names and params comes from self.param
            The application must return EXIT_SUCCESS"""

            output = executor.local("/tmp/bin/demo %s" % (param))
            return output.strip(), "demo-%s" % (param)

    if __name__ == "__main__":
        experiment.run_experiment(
            "/tmp/demo", [DemoBench()],
	    leverages=[], monitors=[], times=1
        )

With the following benchmark code in a file **demo.c** in the same directory

.. code-block:: C

    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>

    int main(int argc, char**argv) {
        int duration = atoi(argv[1]);
        sleep(duration);
        printf("%d\n", duration);
        return 0;
    }

And the following command to actually run the benchmark

.. code-block:: bash

    pip3 install expetator
    python3 demo_bench.py

The results will be saved in a file called */tmp/demo_${HOST}_${TIMESTAMP_START}*
