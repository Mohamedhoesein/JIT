import os
import typing
import shutil
import time
import subprocess
from datetime import datetime

from . import default
from . import classes


def add_compile_file(path: str) -> str:
    return os.path.join(path, "compile.py")


def add_run_file(path: str) -> str:
    return os.path.join(path, "run.py")


def get_time_data_reference_file(path: str) -> str:
    return os.path.join(path, "time_data_reference.csv")


def get_time_data_jit_file(path: str) -> str:
    return os.path.join(path, "time_data_jit.csv")


def get_other_data_reference_file(path: str) -> str:
    return os.path.join(path, "other_data_reference.csv")


def get_other_data_jit_file(path: str) -> str:
    return os.path.join(path, "other_data_jit.csv")


def get_source_directory(path: str) -> str:
    return os.path.join(path, "source")


def get_reference_directory(path: str) -> str:
    return os.path.join(path, "reference")


def get_jit_directory(path: str) -> str:
    return os.path.join(path, "jit")


def get_data_directory(path: str) -> str:
    return os.path.join(path, "data")


def recreate_file(paths: [str]) -> None:
    for path in paths:
        if os.path.exists(path):
            os.remove(path)
        f = open(path, "w+")
        f.close()


def get_source_files(path: str, filter: typing.Callable[[str], bool]) -> [str]:
    if path == "":
        return []
    sources = []
    for path, subdirs, files in os.walk(path):
        for name in files:
            if (name.endswith(".c") or name.endswith(".h")) and filter(name):
                sources.append(os.path.join(path, name))
    return sources


def get_recursive_source_files(paths: [str], filter: typing.Callable[[str], bool]) -> [str]:
    sources = []
    for path in paths:
        sources += get_source_files(path, filter)
    return sources


def get_all_directories(path: str) -> [str]:
    return [
        f
        for f in os.listdir(path)
        if os.path.isdir(os.path.join(path, f)) and f != "__pycache__"
    ]


def get_all_concat_directories(path: str) -> [str]:
    return list(map(lambda f: os.path.join(path, f), get_all_directories(path)))


def remove_if_exists(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def remove_files(paths: [str]) -> None:
    for path in paths:
        remove_if_exists(path)


def remove_data_files(directory: str) -> None:
    remove_files([
        get_time_data_reference_file(directory),
        get_time_data_jit_file(directory),
        get_other_data_reference_file(directory),
        get_other_data_jit_file(directory)
    ])


def append_file(source: str, target: str) -> None:
    while not os.path.exists(source):
        time.sleep(1)
    subprocess.run(["cat " + source + " >> " + target], shell=True, check=True)


def add_new_line(file: str) -> None:
    with open(file, "a") as f:
        f.write("\n")


def persist_data_files(path: str, frontend: str, back_end: str) -> None:
    data_directory = get_data_directory(os.path.dirname(__file__))
    if not os.path.isdir(data_directory):
        os.makedirs(data_directory)
    basename = os.path.basename(path)
    basename = datetime.now().strftime("%Y.%m.%d.%H.%M.%S") + "." + frontend + (
        "." + back_end if back_end is not None else "") + "." + basename
    target = os.path.join(data_directory, basename)

    subprocess.run(["cat " + path + " >> " + target], shell=True, check=True)
    remove_if_exists(path)


def copy_data(source: str, target: str, frontend: str, back_end: str, persist: bool) -> None:
    append_file(source, target)
    if persist:
        persist_data_files(target, frontend, back_end)


def simple_copy_data_files(subdirectory: str, base_directory: str, component: classes.Component) -> None:
    copy_data_files(subdirectory, base_directory, component, "", "", False)


def copy_data_files(
        subdirectory: str,
        base_directory: str,
        component: classes.Component,
        frontend: str,
        back_end: str,
        persist: bool = True
) -> None:
    if component == classes.Component.REFERENCE or component == classes.Component.BOTH:
        benchmark_reference = get_time_data_reference_file(subdirectory)
        base_benchmark_reference = get_time_data_reference_file(base_directory)
        copy_data(benchmark_reference, base_benchmark_reference, frontend, back_end, persist)

        other_reference = get_other_data_reference_file(subdirectory)
        base_other_reference = get_other_data_reference_file(base_directory)
        copy_data(other_reference, base_other_reference, frontend, back_end, persist)

    if component == classes.Component.JIT or component == classes.Component.BOTH:
        benchmark_jit = get_time_data_jit_file(subdirectory)
        base_benchmark_jit = get_time_data_jit_file(base_directory)
        copy_data(benchmark_jit, base_benchmark_jit, frontend, back_end, persist)

        other_jit = get_other_data_jit_file(subdirectory)
        base_other_jit = get_other_data_jit_file(base_directory)
        copy_data(other_jit, base_other_jit, frontend, back_end, persist)


def copy_file(full_source: str, directory: str, file: str) -> None:
    source_input = os.path.join(full_source, file)
    target_input = os.path.join(directory, file)
    shutil.copyfile(source_input, target_input)


# https://www.tutorialspoint.com/How-to-search-and-replace-text-in-a-file-using-Python
def search_and_replace(file_path: str, search_word: str, replace_word: str) -> None:
    with open(file_path, 'r') as file:
        file_contents = file.read()
        updated_contents = file_contents.replace(search_word, replace_word)
    with open(file_path, 'w') as file:
        file.write(updated_contents)
