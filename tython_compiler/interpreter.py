"""Define AST Interpreter
Author: Ty Brennan
"""

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
from .token_types import *
from .token import Token
from .node import Node
from .error import InterpreterEror

DEBUG:bool = False

class Interpreter():
    """Define an interpreter to handle code execution"""
    @classmethod
    def interpret(cls, tree:Node):
        pass