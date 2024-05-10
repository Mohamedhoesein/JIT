"""
This is the main entry point to run tacle-bench.
"""

import os
import typing

from .. import llvm_common
from ... import common
from ... import default
from ... import files


def filter_source_files(name: str) -> bool:
    """
    Indicate if the file should be included in the compilation.
    :param name: The name of the file to check.
    :return: True is returned if the file should be included, and False otherwise.
    """
    return not name.endswith("template-for-new-benchmark.c") and not name.endswith("template-for-new-benchmark.h") and (name.endswith(".c") or name.endswith(".h"))


def main(args: typing.Any):
    """
    The main function for running polybench.
    :param args: The arguments passed via the console, see common.parse_jit_args().
    """
    base_directory = os.path.dirname(__file__)
    source_directory = files.get_source_directory(base_directory)
    benchmarks = files.get_all_directories(source_directory)
    files.remove_files([
        files.get_reference_directory(base_directory),
        files.get_jit_directory(base_directory)
    ])
    sources = []
    for benchmark in benchmarks:
        temp_sources = files.get_all_directories(os.path.join(source_directory, benchmark))
        sources += list(map(lambda x: os.path.join(benchmark, x), temp_sources))
    common_directory = os.path.join(source_directory, "utilities")
    llvm_common.run(
        [common_directory],
        filter_source_files,
        default.default_additional_steps,
        sources,
        base_directory,
        args.j,
        llvm_common.get_llvm_prefix() + "/polybench",
        default.default_arguments,
        common.back_end_parsing(args.b),
        common.args_to_component(args),
        args.b
    )


if __name__ == '__main__':
    main(common.parse_jit_args())
