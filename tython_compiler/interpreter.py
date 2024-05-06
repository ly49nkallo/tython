"""Define AST Interpreter
Author: Ty Brennan
"""
import os, sys
import functools
import time
import enum
import typing
import re
import abc

from pprint import pprint
from .token_types import *
from .token import Token
from .node import Node
from .error import InterpreterEror


@enum.unique
class Datatypes(enum.Enum):
    INT32 = enum.auto()
    INT64 = enum.auto()
    REAL32 = enum.auto()
    REAL64 = enum.auto()
    CHAR8 = enum.auto()

class DType(abc.ABC):
    '''Abstract Data Type Base-Class'''
    @abc.abstractmethod
    def _get_data(self):
        ...

    @abc.abstractmethod
    def _set_data(self, value):
        ...

    @abc.abstractmethod
    def _del_data(self):
        raise NameError("Cannot delete intrinsic data value")
    data = property(_get_data, _set_data, _del_data)

class IntegerDType(DType):
    '''Base-Class for all Integer-like Datatypes'''
    ...

class Integer32(IntegerDType):
    ...

class Integer64(IntegerDType):
    ...

class FloatDType(DType):
    '''Base-Class for all Float-like Datatypes'''
    ...

class Float32(FloatDType):
    ...

class Float64(FloatDType):
    ...

class CharDType(DType):
    '''Base-Class for all Char-like Datatypes'''
    ...

class Char8(CharDType):
    ...

class Interpreter():
    """Define an interpreter to handle code execution"""
    type_map = dict() # type_map["A0"] = Datatypes.[...]
    variables = dict() # variables["A0"] = [...]
    array_variables = dict() # array_variables["A0"] = [...]

    @classmethod
    def clear_variables(cls):
        cls.type_map = dict()
        cls.variables = dict()
        cls.array_variables = dict()

    @classmethod
    def interpret(cls, tree:Node):
        root_node = tree
        print("Begin interpreter")
        assert root_node.token.type == TOKEN_TYPE.PROG
        program_name:str = tree.children[0].children[0].token.value
        print(f'{program_name=}')