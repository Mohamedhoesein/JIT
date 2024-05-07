"""
This module contains general data structures used by other modules that are shared between multiple modules no matter
the front-end.
"""

import typing
import subprocess
from enum import Enum


class Data:
    """
    A class to represent the data extracted from a JIT.
    """
    def __init__(self, meta_data: str, data: str):
        """
        The constructor for the data extracted from a JIT.
        :param meta_data: The metadata for the current line, the expected structure is [DATA,time,type,part,tag], with
        DATA being a string liter, time being the time of the log, type being a description of how to handle the data
        see LogType, part indicates if it is from the front-end or back-end see LogPart, and tag is an indication of
        what data belongs together.
        :param data: The data that is logged.
        """
        split_meta_data = meta_data[1:-1].split(",")
        self.time = int(split_meta_data[1])
        self.type = LogType.from_string(split_meta_data[2])
        self.part = LogPart.from_string(split_meta_data[3])
        self.tag = split_meta_data[4]
        self.data = data


class LogType(Enum):
    """
    An enum for the way the logged data should be processed.
    """
    List = 1
    """
    If all values with the same tag should be listed one after the other.
    """
    Average = 2
    """
    If the average all the values with the same tag should be taken.
    """

    @staticmethod
    def from_string(name: str):
        """
        Convert a string to an element of LogType.
        :param name: The value to convert.
        :return: The element of LogType.
        """
        if name == "LIST":
            return LogType.List
        elif name == "AVERAGE":
            return LogType.Average


class LogPart(Enum):
    """
    The part of the JIT for which to log is created.
    """
    FrontEnd = 1
    """
    If it is for the front-end.
    """
    BackEnd = 2
    """
    If it is for the back-end.
    """
    Whole = 3
    """
    If it is for the whole jit.
    """

    @staticmethod
    def from_string(name: str):
        """
        Convert a string to an element of LogPart.
        :param name: The value to convert.
        :return: The element of LogPart.
        """
        if name == "FRONT-END":
            return LogPart.FrontEnd
        elif name == "BACK-END":
            return LogPart.BackEnd
        elif name == "WHOLE":
            return LogPart.Whole


class Component(Enum):
    """
    What should be run for the benchmark.
    """
    BOTH = 1
    """
    Both the JIT and reference implementation.
    """
    JIT = 2
    """
    Just the JIT.
    """
    REFERENCE = 3
    """
    Just the reference.
    """


class Args:
    """
    Arguments for either the front-end or back-end.
    """
    def __init__(self, name: str, args: str):
        """
        The constructor for the arguments.
        :param name: A nice name for the arguments for easier reference.
        :param args: The arguments to pass.
        """
        self.name = name
        self.args = args


class ComponentData:
    """
    Wrapping class for different data in regard to the JIT and reference implementation.
    """
    def __init__(
            self,
            component: Component,
            front_end_args: typing.List[Args],
            back_end_args: typing.List[Args],
            front_end_extraction: typing.Callable[[str, subprocess.CompletedProcess[bytes]], typing.List[str]],
            back_end_extraction: typing.Callable[[str, subprocess.CompletedProcess[bytes]], typing.List[str]],
            reference_data_extraction: typing.Callable[[str, subprocess.CompletedProcess[bytes]], typing.List[str]],
            jit: str,
            reference_command: typing.Callable[[str], typing.List[str]],
            jit_files: typing.Callable[[str], typing.List[str]],
    ):
        """
        The constructor for the data.
        :param component: If either the JIT, reference implementation or both should be run.
        :param front_end_args: Arguments for the front-end of the JIT.
        :param back_end_args: Arguments for the back-end of the JIT.
        :param front_end_extraction: A callback for data extraction from the front-end of the JIT.
        :param back_end_extraction: A callback for data extraction from the back-end of the JIT.
        :param reference_data_extraction: A callback for data extraction from the reference implementation.
        :param jit: The full path to the JIT.
        :param reference_command: A callback to get the command for the reference implementation.
        :param jit_files: A callback to get
        """
        self.component = component
        self.front_end_args = front_end_args
        self.back_end_args = back_end_args
        self.front_end_extraction = front_end_extraction
        self.back_end_extraction = back_end_extraction
        self.reference_data_extraction = reference_data_extraction
        self.jit = jit
        self.reference_command = reference_command
        self.jit_files = jit_files

    def for_reference(self):
        """
        If the reference should be executed.
        :return: True if only the reference implementation, or both the reference implementation
        and the JIT should be run, otherwise False.
        """
        return self.component == Component.REFERENCE or self.component == Component.BOTH

    def for_jit(self):
        """
        If the JIT should be executed.
        :return: True if only the JIT implementation, or both the reference implementation
        and the JIT should be run, otherwise False.
        """
        return self.component == Component.JIT or self.component == Component.BOTH
