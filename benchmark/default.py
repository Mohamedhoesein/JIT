"""
This module contains different default callbacks that are shared between multiple modules no matter the front-end.
"""

import subprocess
import typing
from itertools import groupby

from . import classes


def default_additional_steps(full_source: str, full_reference_target: str, full_jit_target: str,
                             component: classes.Component) -> None:
    """
    The default for any additional steps to be taken.
    :param full_source: The full path to the source code.
    :param full_reference_target: The path to the target directory for the reference implementation.
    :param full_jit_target: The path to the target directory for the JIT implementation.
    :param component: The description of what implementation is used.
    """
    pass


def default_arguments(directory: str) -> [str]:
    """
    The default for the retrieval of any additional arguments to run a benchmark, always returns an empty array.
    :param directory: The directory of the executed code.
    :return: The additional arguments.
    """
    return []


def none_data_extraction(result: subprocess.CompletedProcess[bytes]) -> [str]:
    """
    The default for no data extraction, always returns an empty array.
    :param result: The result from the subprocess finished.
    :return: The results.
    """
    return []


def base_data_extraction(result: subprocess.CompletedProcess[bytes], part: classes.LogPart, expected_columns: int) -> [str]:
    """
    The default data extraction from the JIT, "[DATA,time,type,part,tag] data", with data being the data to process. The
    rest is described in classes.Data.
    :param result: The result from the subprocess finished.
    :param part: If it is for the front-end or back-end.
    :param expected_columns: How many columns there should be, will only be used if padding is needed.
    :return: The results for each tag.
    """
    lines = result.stdout.splitlines()
    data: [classes.Data] = []
    for line in lines:
        line = line.decode()
        if line.startswith("[DATA,"):
            parts = line.split(None, 1)
            data.append(classes.Data(parts[0], parts[1]))

    data = list(filter(lambda x: x.part == part, data))

    mapped = {}

    for k, g in groupby(data, lambda x: x.tag):
        group = []
        for e in g:
            group.append(e)
        type = group[0].type
        if any(x.type != type for x in group):
            print("Invalid type for log data.")
            exit(-1)
        group.sort(key=lambda x: x.time)
        if type == classes.LogType.List:
            mapped[k] = "" + ",".join(list(map(lambda x: x.data, group))) + ""
        elif type == classes.LogType.Average:
            if any(not x.isnumeric() for x in group):
                print("Got non numeric value for average log type.")
                exit(-1)
            numbers = list(map(lambda x: int(x.data), group))
            mapped[k] = str(sum(numbers) / len(numbers))

    result = []

    for k in sorted(mapped.keys()):
        result.append(f"{k}: {mapped[k]}")

    while len(result) < expected_columns:
        result.append("")
    return result


def default_back_end_data_extraction(expected_columns: int) -> typing.Callable[[subprocess.CompletedProcess[bytes]], typing.List[str]]:
    """
    The default data extraction from the JIT back-end.
    :param expected_columns: How many columns there should be, will only be used if padding is needed.
    :return: The results for each tag.
    """
    return lambda result: base_data_extraction(result, classes.LogPart.BackEnd, expected_columns)


def default_front_end_data_extraction(expected_columns: int) -> typing.Callable[[subprocess.CompletedProcess[bytes]], typing.List[str]]:
    """
    The default data extraction from the JIT front-end.
    :param expected_columns: How many columns there should be, will only be used if padding is needed.
    :return: The results for each tag.
    """
    return lambda result: base_data_extraction(result, classes.LogPart.FrontEnd, expected_columns)


def default_whole_data_extraction(result: subprocess.CompletedProcess[bytes]) -> typing.List[str]:
    """
    The default data extraction from the whole.
    :param result: The result from the subprocess finished.
    :return: The results for each tag.
    """
    return base_data_extraction(result, classes.LogPart.Whole, 2)