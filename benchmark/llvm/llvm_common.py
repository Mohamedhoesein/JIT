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
    Create a callback to filter all files that should be compiled.
    :param filter_source_files: A callback to filter source files of a benchmark.
    :return: A callback that returns True if a file should be included, and False otherwise.
    """
    return lambda name: (name.endswith(".c") or name.endswith(".h")) and filter_source_files(name)


def compile(
        includes: typing.List[str],
        filter_source_files: typing.Callable[[str], bool],
        additional_steps: typing.Callable[[str, str, str, classes.Component], None]
) -> typing.Callable[[str, str, bool, int], None]:
    """
    Create a callback to compile a benchmark.
    :param includes: The folders to include.
    :param filter_source_files: A callback to filter source files of a benchmark.
    :param additional_steps: A callback for any additional steps to take.
    :return: A callback to compile a benchmark.
    """
    include_sources = files.get_all_source_files(includes, filter_wrapper(filter_source_files))

    def __temp__(benchmark_root: str, benchmark: str, jit: bool, i: int, last: bool):
        """
        Compile a benchmark.
        :param benchmark_root: The root directory of the benchmark.
        :param benchmark: The benchmark to run.
        :param jit: If it is for a JIT.
        :param i: The run number.
        """
        print(f"started compiling {benchmark} for run {i + 1}")
        source_directory = files.get_source_directory(benchmark_root)
        source_files = files.get_all_source_files([os.path.join(source_directory, benchmark)], filter_wrapper(filter_source_files))
        reference_directory = files.get_reference_directory(benchmark_root)
        full_reference_target = os.path.join(reference_directory, benchmark.replace("/", "_"))
        jit_directory = files.get_jit_directory(benchmark_root)
        full_jit_target = os.path.join(jit_directory, benchmark.replace("/", "_"))
        if jit:
            if os.path.exists(full_jit_target):
                shutil.rmtree(full_jit_target)
            os.makedirs(full_jit_target)
            os.chdir(full_jit_target)
            full_command = " ".join(["time", compiler(), "-S", "-emit-llvm", "-O", "-Xclang", "-disable-llvm-passes"] + list(map(lambda x: "-I" + x, includes)) + source_files + include_sources)
            full_command = f"/bin/bash -c \"{full_command}\""
            result = subprocess.run(
                [full_command],
                capture_output=True,
                shell=True
            )
            while len(os.listdir(full_jit_target)) == 0:
                pass
            time = common.get_time(result.stderr)
            with open(add_jit_time_compile_file(benchmark_root), "a+") as f:
                if i == 0:
                    f.write(benchmark)
                f.write(f",{time}")
                if last:
                    f.write("\n")
        else:
            if os.path.exists(full_reference_target):
                shutil.rmtree(full_reference_target)
            os.makedirs(full_reference_target)
            os.chdir(full_reference_target)
            full_command = " ".join(["time", compiler(), "-O3", "-lm"] + list(map(lambda x: "-I" + x, includes)) + source_files + include_sources)
            full_command = f"/bin/bash -c \"{full_command}\""
            result = subprocess.run(
                [full_command],
                capture_output=True,
                shell=True
            )
            while len(os.listdir(full_reference_target)) == 0:
                pass
            time = common.get_time(result.stderr)
            with open(add_reference_time_compile_file(benchmark_root), "a+") as f:
                if i == 0:
                    f.write(benchmark)
                f.write(f",{time}")
                if last:
                    f.write("\n")

        additional_steps(os.path.join(source_directory, benchmark), full_reference_target, full_jit_target, classes.Component.JIT if jit else classes.Component.REFERENCE)
        print(f"finished compiling {benchmark} for run {i + 1}")
    return __temp__


def get_llvm_files(path: str) -> typing.List[str]:
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


def get_reference_file_name(path: str) -> typing.List[str]:
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


def read_compile_data(path: str) -> typing.Callable[[str, bool, int], str]:
    """
    Create a callback that reads the time taken to compile a benchmark.
    :param path: The path of the benchmark.
    :return: A function that reads the time taken to compile a benchmark.
    """
    def __temp__(name: str, jit: bool, i: int) -> str:
        """
        Read the time taken to compile a benchmark.
        :param name: The name of the benchmark.
        :param jit: If it is for a JIT.
        :param i: The run number.
        :return: The time it took to compile, with "PreCompile: " as a prefix
        """
        if jit:
            full_path = add_jit_time_compile_file(path)
        else:
            full_path = add_reference_time_compile_file(path)
        with open(full_path, "r+") as f:
            lines = f.readlines()
            lines.reverse()
            for line in lines:
                components = line.split(",", 1)
                if name.startswith(components[0]):
                    return "PreCompile: " + components[1].split(",")[i].strip()
        return "PreCompile: -1"
    return __temp__


def run(
        includes: typing.List[str],
        filter_source_files: typing.Callable[[str], bool],
        additional_steps: typing.Callable[[str, str, str, classes.Component], None],
        sources: typing.List[str],
        path: str,
        jit: str,
        prefix: str,
        arguments: typing.Callable[[str], typing.List[str]],
        back_end_extraction: typing.Callable[[str, subprocess.CompletedProcess[bytes]], typing.List[str]],
        component: classes.Component,
        back_end: str,
        single
) -> None:
    """
    Run the benchmark in a specific folder.
    :param includes: The folders to include when compiling.
    :param filter_source_files: A callback to filter source files of a benchmark.
    :param additional_steps: A callback for any additional steps to take after compiling.
    :param sources: The benchmarks to run.
    :param path: The path to the root of the benchmark.
    :param jit: The full path to the JIT implementation.
    :param prefix: The prefix to use in the name for each csv record.
    :param arguments: A callback to retrieve any additional arguments to the application.
    :param back_end_extraction: A callback to extract data for the back-end.
    :param component: If it is for the JIT, reference implementation, or both.
    :param back_end: The name of the back-end being used.
    :param single: If a single iteration should happen within a compilation.
    """
    temp_jit = add_jit_time_compile_file(path)
    temp_reference = add_reference_time_compile_file(path)
    files.remove_files([temp_jit, temp_reference])
    common.run(
        path,
        prefix,
        compile(includes, filter_source_files, additional_steps),
        sources,
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
        ),
        read_compile_data(path),
        single
    )


def args_to_compile_array(args: typing.Any) -> typing.List[str]:
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


def add_reference_time_compile_file(path: str) -> str:
    """
    Add the name of the file where the temporary results from the compilation are stored.
    :param path: The path that is the basis for the temporary results.
    :return: The path to the temporary results.
    """
    return os.path.join(path, "temp_reference_compile_data.csv")


def add_jit_time_compile_file(path: str) -> str:
    """
    Add the name of the file where the temporary results from the compilation are stored.
    :param path: The path that is the basis for the temporary results.
    :return: The path to the temporary results.
    """
    return os.path.join(path, "temp_jit_compile_data.csv")
