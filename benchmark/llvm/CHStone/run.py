"""
This is the main entry point to run CHStone.
"""

import os
import typing

from .. import llvm_common
from ... import common
from ... import default


def main(args: typing.Any):
    """
    The main function for running CHStone.
    :param args: The arguments passed via the console, see common.parse_jit_args().
    """
    base_directory = os.path.dirname(__file__)
    llvm_common.run(
        base_directory,
        args.j,
        llvm_common.get_llvm_prefix() + "/CHStone",
        default.default_arguments,
        common.back_end_parsing(args.b),
        common.args_to_component(args),
        args.b
    )


if __name__ == '__main__':
    main(common.parse_jit_args())
