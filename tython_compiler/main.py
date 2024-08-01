'''Tython compiler'''
'''Author: Ty Brennan'''

import os, sys
import pathlib
import functools
import logging
import time
import argparse
import enum
import typing
import re

from pprint import pprint
from .token_types import TOKEN_TYPE
from .token import Token
from .node import Node

LOGFILE:pathlib.Path = pathlib.Path("./log.log")

class Interpreter(object):
    """ Handles correct code execution and code state given a compiled AST without lowering """
    def __init__(self):
        self.variables = dict()
        self.array_variables = dict()

    def execute_program(self, program_root:Node):
        assert isinstance(program_root, Node) and program_root.token.type == TOKEN_TYPE.PROG, f'Program root node must be of type TT.PROG, got {program_root.token.type} instead'
        raise NotImplementedError

    def execute_node(self, node:Node):
        raise NotImplementedError

    def assign(self, var:str, value):
        assert re.fullmatch('[A-Z]\\d?', var), f'Variable assign for invalid variable {var}'
        self.variables.update({var: value})

    def array_assign(self, a_var:str, value):
        assert re.fullmatch('\@[A-Z]\\d?', var), f'Array variable assign for invalid variable {var}'
        raise NotImplementedError

    def evaluate_expr(self, expr:Node) -> typing.Union[int, float]:
        assert isinstance(expr, Node) and expr.token.type == TOKEN_TYPE.EXPR< f'Root of expression node must have expr type, got \n {repr(expr)} instead'

    pass
