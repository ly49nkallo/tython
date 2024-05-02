"""Define AST->ASM Lowerer
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
from .error import LoweringError


class Lowerer():
    @classmethod
    def lower(cls, tree:Node) -> str:
        root_node:Node = tree
        assert root_node.token.type == TOKEN_TYPE.PROGRAM
        pass

    @classmethod
    def write_to_file(cls, filepath:typing.Union[typing.FilePath, str], assembly_string:str) -> None:
        assert isinstance(assembly_string, str)
        with open(filepath, 'w', encoding='utf-8') as file_handle:
            file_handle.write(assembly_string)