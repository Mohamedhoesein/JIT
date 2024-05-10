"""
This is the main entry point to run MachSuite.
"""

import os
import typing

from .. import llvm_common
from ... import common
from ... import files
from ... import classes


def filter_source_files(name: str) -> bool:
    """
    Indicate if the file should be included in the compilation.
    :param name: The name of the file to check.
    :return: True is returned if the file should be included, and False otherwise.
    """
    return not name.endswith("generate.c") and not name.endswith("test_support.c") and not name.endswith("test.c")


def additional_steps(full_source: str, full_reference_target: str, full_jit_target: str, component: classes.Component) -> None:
    """
    Copy input.data and check.data for each individual benchmark.
    :param full_source: The path to the source code, where the data files should be present.
    :param full_reference_target: The path to the target directory for the reference implementation.
    :param full_jit_target: The path to the target directory for the JIT implementation.
    :param component: The description of what implementation is used.
    """
    if component == classes.Component.REFERENCE or component == classes.Component.BOTH:
        files.copy_file(full_source, full_reference_target, "input.data")
        files.copy_file(full_source, full_reference_target, "check.data")
    if component == classes.Component.JIT or component == classes.Component.BOTH:
        files.copy_file(full_source, full_jit_target, "input.data")
        files.copy_file(full_source, full_jit_target, "check.data")


def arguments(directory: str) -> typing.List[str]:
    """
    Get the arguments needed to run a benchmark.
    :param directory: The directory of the executed code.
    :return: The additional arguments.
    """
    return [os.path.join(directory, "input.data"), os.path.join(directory, "check.data")]


def main(args: typing.Any):
    """
    The main function for running MachSuite.
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
        if not benchmark.endswith("common"):
            temp_sources = files.get_all_directories(os.path.join(source_directory, benchmark))
            sources += list(map(lambda x: os.path.join(benchmark, x), temp_sources))
    common_directory = os.path.join(source_directory, "common")
    llvm_common.run(
        [common_directory],
        filter_source_files,
        additional_steps,
        sources,
        base_directory,
        args.j,
        llvm_common.get_llvm_prefix() + "/MachSuite",
        arguments,
        common.back_end_parsing(args.b),
        common.args_to_component(args),
        args.b
    )


if __name__ == '__main__':
    main(common.parse_jit_args())
