import os
import typing

from .. import llvm_common
from ... import common
from ... import default
from ... import files


def main(args: typing.Any):
    base_directory = os.path.dirname(__file__)
    source_directory = files.get_source_directory(base_directory)
    benchmarks = files.get_all_directories(source_directory)
    sources = []
    for benchmark in benchmarks:
        temp_sources = files.get_all_directories(os.path.join(source_directory, benchmark))
        sources += list(map(lambda x: os.path.join(benchmark, x), temp_sources))
    llvm_common.compile(
        sources,
        base_directory,
        [],
        default.default_filter_files,
        default.default_additional_steps,
        common.compile_args_to_component(args)
    )


if __name__ == '__main__':
    main(llvm_common.parse_compile_args())
