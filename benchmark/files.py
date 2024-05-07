"""
This module contains functions to handle files that is needed no matter the front-end.
"""

import os
import typing
import shutil
import time
import subprocess
from datetime import datetime

from . import classes


def add_run_file(path: str) -> str:
    """
    Add the name of the run script to the path.
    :param path: The path that is the basis for the compile script.
    :return: The path to the run script.
    """
    return os.path.join(path, "run.py")


def get_time_data_reference_file(path: str) -> str:
    """
    Add the name of the time data csv for the reference implementation to the path.
    :param path: The path that is the basis for the compile script.
    :return: The path to the csv file.
    """
    return os.path.join(path, "time_data_reference.csv")


def get_time_data_jit_file(path: str) -> str:
    """
    Add the name of the time data csv for the JIT to the path.
    :param path: The path that is the basis for the compile script.
    :return: The path to the csv file.
    """
    return os.path.join(path, "time_data_jit.csv")


def get_other_data_reference_file(path: str) -> str:
    """
    Add the name of the other data csv for the reference implementation to the path.
    :param path: The path that is the basis for the compile script.
    :return: The path to the csv file.
    """
    return os.path.join(path, "other_data_reference.csv")


def get_other_data_jit_file(path: str) -> str:
    """
    Add the name of the other data csv for the JIT to the path.
    :param path: The path that is the basis for the compile script.
    :return: The path to the csv file.
    """
    return os.path.join(path, "other_data_jit.csv")


def get_source_directory(path: str) -> str:
    """
    Add the name of the source directory to the path.
    :param path: The path that is the basis for the compile script.
    :return: The path to the source directory.
    """
    return os.path.join(path, "source")


def get_reference_directory(path: str) -> str:
    """
    Add the name of the directory of the reference implementation to the path.
    :param path: The path that is the basis for the compile script.
    :return: The path to the directory of the reference implementation.
    """
    return os.path.join(path, "reference")


def get_jit_directory(path: str) -> str:
    """
    Add the name of the directory of the JIT source file to the path.
    :param path: The path that is the basis for the compile script.
    :return: The path to the directory of the JIT source files.
    """
    return os.path.join(path, "jit")


def get_data_directory(path: str) -> str:
    """
    Add the name of the final data directory to the path.
    :param path: The path that is the basis for the compile script.
    :return: The path to the final data directory.
    """
    return os.path.join(path, "data")


def recreate_file(paths: typing.List[str]) -> None:
    """
    Delete and create the given file.
    :param paths: The file to create.
    """
    for path in paths:
        if os.path.exists(path):
            os.remove(path)
        f = open(path, "w+")
        f.close()


def get_source_files(path: str, filter: typing.Callable[[str], bool]) -> typing.List[str]:
    """
    Get all the source files in a directory.
    :param path: The path to the directory.
    :param filter: A callback to indicate if the file should be included or not. It returns True if the file should be
    included, and False otherwise.
    :return: The paths to the files to include.
    """
    if path == "":
        return []
    sources = []
    for path, subdirs, files in os.walk(path):
        for name in files:
            if filter(name):
                sources.append(os.path.join(path, name))
    return sources


def get_all_source_files(paths: typing.List[str], filter: typing.Callable[[str], bool]) -> typing.List[str]:
    """
    Get all the source files in each directory.
    :param paths: The paths to each of the directories to include.
    :param filter: A callback to indicate if the file should be included or not. It returns True if the file should be
    included, and False otherwise.
    :return: The paths to the files to include.
    """
    sources = []
    for path in paths:
        sources += get_source_files(path, filter)
    return sources


def get_all_directories(path: str) -> typing.List[str]:
    """
    Get all directories directly in a given directory.
    :param path: The directory for which to get the directories.
    :return: The names of the directories.
    """
    return [
        f
        for f in os.listdir(path)
        if os.path.isdir(os.path.join(path, f)) and f != "__pycache__"
    ]


def get_all_concat_directories(path: str) -> typing.List[str]:
    """
    Get all directories directly in a given directory.
    :param path: The directory for which to get the directories.
    :return: The names of the directories concatenated with the given path.
    """
    return list(map(lambda f: os.path.join(path, f), get_all_directories(path)))


def remove_if_exists(path: str) -> None:
    """
    Remove an item if it exists.
    :param path: The path to the item to delete.
    """
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def remove_files(paths: typing.List[str]) -> None:
    """
    Remove multiple items if they exist.
    :param paths: The paths to the items to delete.
    """
    for path in paths:
        remove_if_exists(path)


def remove_data_files(directory: str) -> None:
    """
    Remove the data files in a specific directory.
    :param directory: The directory that contains the data files.
    """
    remove_files([
        get_time_data_reference_file(directory),
        get_time_data_jit_file(directory),
        get_other_data_reference_file(directory),
        get_other_data_jit_file(directory)
    ])


def append_file(source: str, target: str) -> None:
    """
    Append the contents of one file to another.
    :param source: The source file of the data.
    :param target: The file to which to add the data.
    """
    while not os.path.exists(source):
        time.sleep(1)
    subprocess.run(["cat " + source + " >> " + target], shell=True, check=True)


def persist_data_files(path: str, frontend: str, back_end: str) -> None:
    """
    Persist a data file by copying it to the data directory.
    :param path: The path to the data file.
    :param frontend: The front-end for which the data was created.
    :param back_end: The back-end for which the data was created.
    :return:
    """
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
    """
    Copy the data from the data files one level up, appending the source to the target and persisting it if needed.
    :param source: The source data.
    :param target: The target data.
    :param frontend: The front-end for which the data was created.
    :param back_end: The back-end for which the data was created.
    :param persist: If the new target data should be persisted.
    """
    append_file(source, target)
    if persist:
        persist_data_files(target, frontend, back_end)


def simple_copy_data_files(source: str, target: str, component: classes.Component) -> None:
    """
    Copy the data from the files from one directory to another.
    :param source: The directory from which to copy the files.
    :param target: The directory to which to copy the files.
    :param component: If it is for the JIT, reference implementation, or both.
    """
    copy_data_files(source, target, component, "", "", False)


def copy_data_files(
        source: str,
        target: str,
        component: classes.Component,
        frontend: str,
        back_end: str,
        persist: bool = True
) -> None:
    """
    Copy the data from the data files.
    :param source: The directory from which to copy the files.
    :param target: The directory to which to copy the files.
    :param component: If it is for the JIT, reference implementation, or both.
    :param frontend: The front-end for which the data was created.
    :param back_end: The back-end for which the data was created.
    :param persist: If the new target data should be persisted.
    :return:
    """
    if component == classes.Component.REFERENCE or component == classes.Component.BOTH:
        benchmark_reference = get_time_data_reference_file(source)
        base_benchmark_reference = get_time_data_reference_file(target)
        copy_data(benchmark_reference, base_benchmark_reference, frontend, back_end, persist)

        other_reference = get_other_data_reference_file(source)
        base_other_reference = get_other_data_reference_file(target)
        copy_data(other_reference, base_other_reference, frontend, back_end, persist)

    if component == classes.Component.JIT or component == classes.Component.BOTH:
        benchmark_jit = get_time_data_jit_file(source)
        base_benchmark_jit = get_time_data_jit_file(target)
        copy_data(benchmark_jit, base_benchmark_jit, frontend, back_end, persist)

        other_jit = get_other_data_jit_file(source)
        base_other_jit = get_other_data_jit_file(target)
        copy_data(other_jit, base_other_jit, frontend, back_end, persist)


def copy_file(full_source: str, directory: str, file: str) -> None:
    """
    Copy a file fully from one place to another.
    :param full_source: The directory from where to copy.
    :param directory: The directory where to place the file.
    :param file: The name of the file to copy.
    """
    source_input = os.path.join(full_source, file)
    target_input = os.path.join(directory, file)
    shutil.copyfile(source_input, target_input)


def search_and_replace(file_path: str, search_word: str, replace_word: str) -> None:
    """
    Search for a string in a file and replace it with another.
    This is taken from: https://www.tutorialspoint.com/How-to-search-and-replace-text-in-a-file-using-Python
    :param file_path: The file to do the search and replace in
    :param search_word: The word to search for.
    :param replace_word: The word to replace the searched for word with.
    :return:
    """
    with open(file_path, 'r') as file:
        file_contents = file.read()
        updated_contents = file_contents.replace(search_word, replace_word)
    with open(file_path, 'w') as file:
        file.write(updated_contents)
