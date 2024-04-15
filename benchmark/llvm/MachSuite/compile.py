import os
import typing

from .. import llvm_common
from ... import common


def filter(name: str) -> bool:
    return not name.endswith("generate.c") and not name.endswith("test_support.c") and not name.endswith("test.c")


def additional_steps(full_source: str, full_reference_target: str, full_jit_target: str, component: common.Component) -> None:
    if component == common.Component.REFERENCE or component == common.Component.BOTH:
        common.copy_file(full_source, full_reference_target, "input.data")
        common.copy_file(full_source, full_reference_target, "check.data")
    if component == common.Component.JIT or component == common.Component.BOTH:
        common.copy_file(full_source, full_jit_target, "input.data")
        common.copy_file(full_source, full_jit_target, "check.data")


def main(args: typing.Any):
    base_directory = os.path.dirname(__file__)
    source_directory = common.get_source_directory(base_directory)
    benchmarks = common.get_all_directories(source_directory)
    sources = []
    for benchmark in benchmarks:
        if not benchmark.endswith("common"):
            temp_sources = common.get_all_directories(os.path.join(source_directory, benchmark))
            sources += list(map(lambda x: os.path.join(benchmark, x), temp_sources))
    common_directory = os.path.join(source_directory, "common")
    llvm_common.compile(
        sources,
        base_directory,
        [common_directory],
        filter,
        additional_steps,
        common.compile_args_to_component(args)
    )


if __name__ == '__main__':
    main(llvm_common.parse_compile_args())
