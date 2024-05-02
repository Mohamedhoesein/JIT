"""
This module contains functions shared between multiple LLVM benchmarks.
"""

import os
import subprocess
import shutil
import typing
import argparse

from .. import common
from .. import classes
from .. import default
from .. import files


def compiler() -> str:
    """
    Return the compiler as it can be used in the command line to use when compiling the source code.
    :return: The compiler to use.
    """
    return "clang-17"


def get_llvm_prefix() -> str:
    """
    Return the prefix used for the names of tests in the csv file.
    :return: The prefix used for the names of tests in the csv file.
    """
    return "llvm"


def filter_wrapper(filter_source_files: typing.Callable[[str], bool]) -> typing.Callable[[str], bool]:
    """
    Filter all files that should be compiled.
    :param filter_source_files: A callback for a filter specific to a benchmark.
    :return: A callback that returns True if a file should be included, and False otherwise.
    """
    return lambda name: (name.endswith(".c") or name.endswith(".h")) and filter_source_files(name)


def compile(
    sources: [str],
    base_directory: str,
    includes: [str],
    filter_source_files: typing.Callable[[str], bool],
    additional_steps: typing.Callable[[str, str, str, classes.Component], None],
    component: classes.Component
) -> None:
    """
    Compile in the source code in the given directories.
    :param sources: The folders containing the source code to be compiled, this must be relative to base_directory.
    :param base_directory: The base directory for the source code, and the output files for the JIT and
    reference implementation.
    :param includes: Any folders that should be included.
    :param filter_source_files: A callback to indicate what files should be included, return True if it should be
    included, and False otherwise.
    :param additional_steps: A callback for any steps that should be taken after compilation.
    :param component: If the source should be compiled for the JIT, or the reference implementation.
    """
    source_directory = files.get_source_directory(base_directory)
    reference_directory = files.get_reference_directory(base_directory)
    jit_directory = files.get_jit_directory(base_directory)
    if os.path.exists(reference_directory):
        shutil.rmtree(reference_directory)
    if os.path.exists(jit_directory):
        shutil.rmtree(jit_directory)
    for source in sorted(sources):
        target = source.replace("/", "_").replace("\\", "_")
        full_source = os.path.join(source_directory, source)
        print(f"started compiling {source}")
        source_files = files.get_all_source_files([full_source], filter_wrapper(filter_source_files))
        source_files += files.get_all_source_files(includes, filter_wrapper(filter_source_files))
        full_reference_target = os.path.join(reference_directory, target)
        if component == classes.Component.REFERENCE or component == classes.Component.BOTH:
            os.makedirs(full_reference_target)
            os.chdir(full_reference_target)
            subprocess.run(
                [compiler(), "-O3", "-lm"]
                + list(map(lambda x: "-I" + x, includes))
                + source_files
            )
        full_jit_target = os.path.join(jit_directory, target)
        if component == classes.Component.JIT or component == classes.Component.BOTH:
            os.makedirs(full_jit_target)
            os.chdir(full_jit_target)
            subprocess.run(
                [compiler(), "-S", "-emit-llvm", "-O", "-Xclang", "-disable-llvm-passes"]
                + list(map(lambda x: "-I" + x, includes))
                + source_files
            )
        additional_steps(full_source, full_reference_target, full_jit_target, component)
        print(f"finished compiling {source}")


def get_llvm_files(path: str) -> [str]:
    """
    List all LLVM IR files, those with an .ll.
    :param path: The directory for which to list the LLVM IR files.
    :return: The full paths for each LLVM IR file
    """
    if path == "":
        return []
    sources = []
    for path, subdirs, files in os.walk(path):
        for name in files:
            if name.endswith(".ll"):
                sources.append(os.path.join(path, name))
    return sources


def get_reference_file_name(path: str) -> [str]:
    """
    Get the full path for the reference implementation, this assumes that it is compiled with the compile method above,
    and that it is in the given path.
    :param path: The path of the reference implementation.
    :return: The full path for the reference implementation.
    """
    return [os.path.join(path, "a.out")]


def parse_compile_args() -> typing.Any:
    """
    Parse command line arguments for compiling. There is the `-e` to compile the reference implementation, and `-b` to
    compile the JIT. If neither is set the default is `-b`.
    :return: An object with the appropriate properties set.
    """
    parser = argparse.ArgumentParser(
        prog="compile",
        description="Compile the jit or reference."
    )
    parser.add_argument('-e', action="store_true", help="If some external reference implementation will be compiled.")
    parser.add_argument('-b', action="store_true", help="If the jit will be compiled.")
    args = parser.parse_args()
    if not args.e and not args.b:
        print("Defaulted to -b.")
        args.b = True
    return args


def run(
    path: str,
    jit: str,
    prefix: str,
    arguments: typing.Callable[[str], typing.List[str]],
    back_end_extraction: typing.Callable[[subprocess.CompletedProcess[bytes]], typing.List[str]],
    component: classes.Component,
    back_end: str
) -> None:
    """
    Run the benchmark in a specific folder.
    :param path: The path to the root of the benchmark.
    :param jit: The full path to the JIT implementation.
    :param prefix: The prefix to use in the name for each csv record.
    :param arguments: A callback to retrieve any additional arguments to the application.
    :param back_end_extraction: A callback to extract data for the back-end.
    :param component: If it is for the JIT, reference implementation, or both.
    :param back_end: The name of the back-end being used.
    """
    common.run(
        path,
        prefix,
        arguments,
        classes.ComponentData(
            component,
            [classes.Args("None", "")],
            common.back_end_args(back_end),
            default.default_front_end_data_extraction(1),
            back_end_extraction,
            default.none_data_extraction,
            jit,
            get_reference_file_name,
            get_llvm_files
        )
    )


def args_to_compile_array(args: typing.Any) -> [str]:
    """
    Convert the arguments object for parse_compile_args() to an array of strings to pass to the compilation command.
    :param args: The argument to convert.
    :return: An array of strings to pass to the compilation command
    """
    return (["-e"] if args.e else []) + (["-b"] if args.b is not None else [])


def compile_args_to_component(args: typing.Any) -> classes.Component:
    """
    Convert the compile arguments to a classes.Component.
    :param args: The arguments to convert.
    :return: The classes.Component that is associated with the arguments.
    """
    if args.b and args.e:
        return classes.Component.BOTH
    elif args.e:
        return classes.Component.REFERENCE
    else:
        return classes.Component.JIT


def default_filter_files(name: str) -> bool:
    """
    The default filter for files to include in the compilation. This includes every file in the compilation.
    :param name: The name of the file.
    :return: Always True to accept each file.
    """
    return True


def add_compile_file(path: str) -> str:
    """
    Add the name of the compile script to the path.
    :param path: The path that is the basis for the compile script.
    :return: The path to the compile script.
    """
    return os.path.join(path, "compile.py")
