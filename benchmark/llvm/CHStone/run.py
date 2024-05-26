"""
This is the main entry point to run CHStone.
"""

import os
import typing

from .. import llvm_common
from ... import common
from ... import default
from ... import files


def main(args: typing.Any):
    """
    The main function for running CHStone.
    :param args: The arguments passed via the console, see common.parse_jit_args().
    """
    base_directory = os.path.dirname(__file__)
    source_directory = files.get_source_directory(base_directory)
    sources = files.get_all_directories(source_directory)
    files.remove_files([
        files.get_reference_directory(base_directory),
        files.get_jit_directory(base_directory)
    ])
    llvm_common.run(
        [],
        llvm_common.default_filter_files,
        default.default_additional_steps,
        sources,
        base_directory,
        args.j,
        llvm_common.get_llvm_prefix() + "/CHStone",
        default.default_arguments,
        common.back_end_parsing(args.b),
        common.args_to_component(args),
        args.b,
        args.s
    )


if __name__ == '__main__':
    main(common.parse_jit_args())
