"""
This module is the main entry point to run benchmarks for LLVM.
"""

import os
import subprocess
import typing

from . import llvm_common
from .. import common
from .. import files


def main(args: typing.Any):
    """
    The main function for running LLVM benchmarks.
    :param args: The arguments passed via the console, see common.parse_jit_args().
    """
    base_directory = os.path.dirname(__file__)
    directories = files.get_all_concat_directories(base_directory)
    files.remove_data_files(base_directory)
    component = common.args_to_component(args)
    for directory in directories:
        print("started " + directory)
        compile_file = llvm_common.add_compile_file(directory)
        run_file = files.add_run_file(directory)
        if not os.path.isfile(compile_file) or not os.path.isfile(run_file):
            print("finished " + directory)
            continue
        os.chdir(os.path.join(os.path.dirname(base_directory), "../"))
        compile_module = os.path.relpath(compile_file).replace("/", ".")[:-3]
        run_module = os.path.relpath(run_file).replace("/", ".")[:-3]
        subprocess.run(["python3", "-m", compile_module] + llvm_common.args_to_compile_array(args), check=True)
        subprocess.run(["python3", "-m", run_module] + common.args_to_run_array(args), check=True)
        files.simple_copy_data_files(directory, base_directory, component)

        print("finished " + directory)


if __name__ == '__main__':
    main(common.parse_jit_args())
