"""
This is the main entry point to compile CHStone.
"""

import os
import typing

from .. import llvm_common
from ... import default
from ... import files


def main(args: typing.Any):
    """
    The main function for compiling CHStone.
    :param args: The arguments passed via the console, see llvm_common.parse_compile_args().
    """
    base_directory = os.path.dirname(__file__)
    source_directory = files.get_source_directory(base_directory)
    sources = files.get_all_directories(source_directory)
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
