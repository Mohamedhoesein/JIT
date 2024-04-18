import subprocess
from itertools import groupby

from . import classes


def default_filter_files(name: str) -> bool:
    return True


def default_additional_steps(full_source: str, full_reference_target: str, full_jit_target: str,
                             component: classes.Component) -> None:
    pass


def default_arguments(directory: str) -> [str]:
    return []


def none_data_extraction(result: subprocess.CompletedProcess[bytes]) -> [str]:
    return []


def base_data_extraction(result: subprocess.CompletedProcess[bytes], part: classes.LogPart) -> [str]:
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
        result.append(mapped[k])
    return result


def default_back_end_data_extraction(result: subprocess.CompletedProcess[bytes]) -> [str]:
    return base_data_extraction(result, classes.LogPart.BackEnd)


def default_front_end_data_extraction(result: subprocess.CompletedProcess[bytes]) -> [str]:
    return base_data_extraction(result, classes.LogPart.FrontEnd)
