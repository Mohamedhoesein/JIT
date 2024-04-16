import os
import subprocess
import shutil
import typing
import argparse

from .. import common


def get_llvm_prefix() -> str:
    return "llvm"


def compile(
    sources: [str],
    base_directory: str,
    includes: [str],
    filter: typing.Callable[[str], bool],
    additional_steps: typing.Callable[[str, str, str, common.Component], None],
    component: common.Component
) -> None:
    source_directory = common.get_source_directory(base_directory)
    reference_directory = common.get_reference_directory(base_directory)
    jit_directory = common.get_jit_directory(base_directory)
    if os.path.exists(reference_directory):
        shutil.rmtree(reference_directory)
    if os.path.exists(jit_directory):
        shutil.rmtree(jit_directory)
    for source in sources:
        target = source.replace("/", "_").replace("\\", "_")
        full_source = os.path.join(source_directory, source)
        print(f"started compiling {source}")
        source_files = common.get_source_files(full_source, filter)
        source_files += common.get_recursive_source_files(includes, filter)
        full_reference_target = os.path.join(reference_directory, target)
        if component == common.Component.REFERENCE or component == common.Component.BOTH:
            os.makedirs(full_reference_target)
            os.chdir(full_reference_target)
            subprocess.run(
                ["clang-17", "-O3", "-lm"]
                + list(map(lambda x: "-I" + x, includes))
                + source_files
            )
        full_jit_target = os.path.join(jit_directory, target)
        if component == common.Component.JIT or component == common.Component.BOTH:
            os.makedirs(full_jit_target)
            os.chdir(full_jit_target)
            subprocess.run(
                ["clang-17", "-S", "-emit-llvm", "-O", "-Xclang", "-disable-llvm-passes"]
                + list(map(lambda x: "-I" + x, includes))
                + source_files
            )
        additional_steps(full_source, full_reference_target, full_jit_target, component)
        print(f"finished compiling {source}")


def get_llvm_files(path: str) -> [str]:
    if path == "":
        return []
    sources = []
    for path, subdirs, files in os.walk(path):
        for name in files:
            if name.endswith(".ll"):
                sources.append(os.path.join(path, name))
    return sources


def get_reference_file_name(path: str) -> [str]:
    return [os.path.join(path, "a.out")]


def parse_compile_args() -> typing.Any:
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
    jit_data_extraction: typing.Callable[[subprocess.CompletedProcess[bytes]], typing.List[str]],
    component: common.Component,
    back_end: str
) -> None:
    common.run(
        path,
        jit,
        prefix,
        arguments,
        get_reference_file_name,
        get_llvm_files,
        common.ComponentData(
            component,
            "",
            common.back_end_args(back_end),
            jit_data_extraction,
            common.default_data_extraction
        )
    )


def args_to_compile_array(args: typing.Any) -> [str]:
    return (["-e"] if args.e else []) + (["-b"] if args.b is not None else [])
