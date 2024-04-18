import typing
import subprocess
from enum import Enum


class Data:
    def __init__(self, meta_data: str, data: str):
        split_meta_data = meta_data[1:-1].split(",")
        self.time = int(split_meta_data[1])
        self.type = LogType.from_string(split_meta_data[2])
        self.part = LogPart.from_string(split_meta_data[3])
        self.tag = split_meta_data[4]
        self.data = data


class LogType(Enum):
    List = 1
    Average = 2

    @staticmethod
    def from_string(name: str):
        if name == "LIST":
            return LogType.List
        elif name == "AVERAGE":
            return LogType.Average


class LogPart(Enum):
    FrontEnd = 1
    BackEnd = 2

    @staticmethod
    def from_string(name: str):
        if name == "FRONT-END":
            return LogPart.FrontEnd
        elif name == "BACK-END":
            return LogPart.BackEnd


class Component(Enum):
    BOTH = 1
    JIT = 2
    REFERENCE = 3


class Args:
    def __init__(self, name: str, args: [str]):
        self.name = name
        self.args = args


class ComponentData:
    def __init__(
            self,
            component: Component,
            front_end_args: str,
            back_end: typing.List[Args],
            front_end_extraction: typing.Callable[[subprocess.CompletedProcess[bytes]], typing.List[str]],
            back_end_extraction: typing.Callable[[subprocess.CompletedProcess[bytes]], typing.List[str]],
            reference_data_extraction: typing.Callable[[subprocess.CompletedProcess[bytes]], typing.List[str]]
    ):
        self.component = component
        self.front_end_args = front_end_args
        self.back_end = back_end
        self.front_end_extraction = front_end_extraction
        self.back_end_extraction = back_end_extraction
        self.reference_data_extraction = reference_data_extraction

    def for_reference(self):
        return self.component == Component.REFERENCE or self.component == Component.BOTH

    def for_jit(self):
        return self.component == Component.JIT or self.component == Component.BOTH