# Download libraries
Use `configure.sh` to install llvm, specify the build type cmake should use for LLVM as the first argument, and the
number of jobs as the second argument.
# JIT
There are 2 main components for the JIT compiler, the front-end and back-end. The code for these components are in the
folder with the same name. Besides this we have some share code in the `util` folder, and some code for handling
reoptimization in the `reOptimize` folder which is taken from [sunho](https://gist.github.com/sunho/bbbf7c415ea4e16d37bec5cea8adce5a).
## Front-End
When adding a new front-end one should create a new class which inherits from `BaseFrontEnd`. The initialization of the
new class should be added to `BaseFrontEnd::create` with a guard based on a macro being defined. There must  also be a
function in the new class which can load a new module, which must be  added to `BaseFrontend::requestModule` with a guard
based on a macro being defined this must be the same as the one used in `BaseFrontEnd::create`. When adding a new
front-end it is useful to also make sure there is a benchmark available for said front-end, see [General Structure](#general-structure)
and [New Front-End](#new-front-end) for more information on what should be added to benchmarking when adding a new front-end.
## Back-End
When adding a new front-end one should create a new class which inherits from `BaseJIT`. The initialization of the new
class should be added to `BaseJIT::create` with a guard based on a macro being defined. When adding a new back-end, make
sure there is a setup for handling the arguments and data extraction from the back-end, see [New Back-End](#new-back-end)
for more information on what should be  added to benchmarking when adding a new back-end
# Benchmark
In the `benchmark` folder, we have the code to run some benchmarks. At the root level we have `run.py` which can be used
to run a benchmark, which should be run as a module. When in the root folder of the project use
```bash
python3 -m benchmark.run
```
with the appropriate arguments. Which can be seen by using the `-h` flag. There are two types of benchmarks that can be
run. Either the benchmark within the JIT, or some external reference implementation if the benchmark can also be run in
some external setting.
## General Structure
The general structure of the benchmarking, is that in the `benchmark` folder we have those python script that contains
the logic to start a benchmark, and any shared code between all front-ends. Within this folder we have a folder for each
front-end, which must contain a `run.py` script which is used to start the benchmarks, for which there is a subfolder
within the folder for each front-end.
## Data
For the data that is given by the benchmarks for each front-end make sure that they are put in csv files in the root folder
of the front-end. There are two sets of files that can be given depending on if the results are for the JIT or reference
implementation. These are named `other_data_{x}.csv`, and `time_data_{x}.csv`, where `{x}` can be either `jit` or
`reference` depending on what version was run. `time_data_{x}.csv` will contain data that can be gathered from the `time`
command and is thus easily  shared between each front-end and back-end combination, while `other_data_{x}.csv` will contain
any data specific to the front-end and back-end. Each row will contain the results of each individual run of each possible
configuration. Where a configuration is a specific combination front-end, back-end, front-end arguments, and back-end
arguments. The `run.py` script in the `benchmark` folder will copy the data files over to `benchmark/data/` with a name
based on the current time, front-end and back-end.
## New Front-End
When adding a benchmark for a new front-end, add a folder for it with a `run.py` script, alongside this there must be an
`__init__.py` file so that it can be run as a module. The `run.py` script should accept the same arguments as specified
in the `parse_jit_args` function in `benchmark/common.py`. There is a general function available to run a benchmark, see
the `run` function in `benchmark/common.py`. There are options to run a reference implementation, if this is not possible
return an error code.
## New Back-End
When a new back-end is added, make sure there is a valid mapping available for a name for the back-end to how to parse
performance data given by the back-end, alongside a set of arguments which should be tested. For the former look at the
`back_end_parsing_map` function in `benchmark/common.py`, for the latter look at the `back_end_args_map` function in the
same file.