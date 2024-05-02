"""Define AST Interpreter
Author: Ty Brennan
"""
import os, sys
import functools
import time
import enum
import typing
import re

from pprint import pprint
from .token_types import *
from .token import Token
from .node import Node
from .error import InterpreterEror

DEBUG:bool = False

@enum.unique
class Datatypes(enum.Enum):
    INT32 = 1
    INT64 = 2
    REAL32 = 3
    REAL64 = 4
    CHAR8 = 5

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
        pass