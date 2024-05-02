"""
This is the main entry point to compile tacle-bench.
"""

import os
import typing

from .. import llvm_common
from ... import default
from ... import files


def main(args: typing.Any):
    """
    The main function for compiling tacle-bench.
    :param args: The arguments passed via the console, see llvm_common.parse_compile_args().
    """
    base_directory = os.path.dirname(__file__)
    source_directory = files.get_source_directory(base_directory)
    benchmarks = files.get_all_directories(source_directory)
    sources = []
    for benchmark in benchmarks:
        if not benchmark.endswith("doc"):
            temp_sources = files.get_all_directories(os.path.join(source_directory, benchmark))
            sources += list(map(lambda x: os.path.join(benchmark, x), temp_sources))
    llvm_common.compile(
        sources,
        base_directory,
        [],
        llvm_common.default_filter_files,
        default.default_additional_steps,
        llvm_common.compile_args_to_component(args)
    )


if __name__ == '__main__':
    main(llvm_common.parse_compile_args())
