"""
This is the main entry point to run MachSuite.
"""

import os
import typing

from .. import llvm_common
from ... import common


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
    llvm_common.run(
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
