'''Author: Ty Brennan'''
'''Tython compiler'''
import regex as re
import os, sys
import pathlib
import functools
import logging
import time
import argparse
import enum
import typing

from pprint import pprint

LOGFILE:pathlib.Path = pathlib.Path("./log.log")

class TOKEN_TYPE(enum.Enum):
        INT32 = enum.auto()
        INT64 = enum.auto()
        REAL32 = enum.auto()
        REAL64 = enum.auto()
        CHAR8 = enum.auto()
        PLUS = enum.auto()
        MINUS = enum.auto()
        MUL = enum.auto()
        DIV = enum.auto()
        L_PAREN = enum.auto()
        R_PAREN = enum.auto()

class Token(object):
    def __init__(self, type:TOKEN_TYPE, value):
        assert isinstance(type, TOKEN_TYPE)
        self.type:TOKEN_TYPE = type
        self.value = value

    def __repr__(self):
        ret = str(self.type)
        if self.value: ret += str(self.value)
        return ret

class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.current_char = None
        pass

    def advance(self):
        self.pos += 1
     
def main() -> None:
    logger:logging.Logger = logging.getLogger()
    parser = argparse.ArgumentParser(description='TYTHON Compiler')
    parser.add_argument('input_file')
    args = parser.parse_args() 
    filepath:pathlib.Path = pathlib.Path(args.input_file)
    with open(filepath, 'r') as f:
        #use 'os.linesep' if it doesn't work but python doesn't care for some reason
        file_contents = f.read().split('\n') 
    pprint(file_contents)

    pass

if __name__ == '__main__':
    main()