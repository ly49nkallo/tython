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

LOGFILE:pathlib.Path = pathlib.Path("./log.log")

class Interpreter(object):
    def __init__(self):
        self.variables = dict()

    def assign(self, var:str, value):
        assert re.fullmatch('[A-Z]\\d?', var), f'Variable assign for invalid variable {var}'
        self.variables.update({var: value})

    pass