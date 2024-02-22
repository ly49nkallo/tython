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
VERSION:str = "0.1.0"

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
    '''A lexical unit of code correspinding to a certain, specific function.'''
    def __init__(self, type:TOKEN_TYPE, value):
        assert isinstance(type, TOKEN_TYPE)
        self.type:TOKEN_TYPE = type
        self.value = value

    def __repr__(self):
        ret = str(self.type)
        if self.value: ret += str(self.value)
        return ret

class Lexer(object):
    '''Responsible for taking raw text input and generating a list of tokens.'''
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.current_char = None
        pass
    
    def __call__(self):
        pass
    
    def advance(self):
        self.pos += 1
    
    def digest(self, line):
        pass
    
def main() -> None:
    logger:logging.Logger = logging.getLogger()
    parser = argparse.ArgumentParser(description=f'TYTHON Compiler {VERSION}')
    parser.add_argument('input_file')
    parser.add_argument('-o', '--output')
    parser.add_argument('-c', '--compile', action='store_true')
    parser.add_argument('-i', '--interpret', action='store_true')
    parser.add_argument('-v', '--version', action='version', version=f'Tython {VERSION}')
    args = parser.parse_args() 
    filepath:pathlib.Path = pathlib.Path(args.input_file)
    with open(filepath, 'r') as f:
        file_contents = f.read()
    print(file_contents)

    exit(0)
    
    lexer = Lexer()
    tokens = lexer(file_contents)

    pass

if __name__ == '__main__':
    main()