'''Author: Ty Brennan'''
'''Tython compiler'''
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

COMMENT_DELIM = '#'

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
        if self.value: ret += f":{self.value}"
        return ret

class Lexer(object):
    '''Responsible for taking raw text input and generating a list of tokens.'''

    @classmethod
    def __call__(cls, text:str) -> list:
        lines = text.split('\n')
        # remove blank lines
        lines = list(filter(lambda x: x != '', lines))
        buffers = []
        for line in lines:
            buffer = ''
            i = 0
            in_str_lit:bool = False
            while i < len(line):
                curr_char = line[i]
                next_char = line[i+1] if i+1<len(line) else None
                prev_char = line[i-1] if i-1>=0 else None
                buffer += curr_char
                if curr_char == COMMENT_DELIM:
                    pass
                elif curr_char == ' ':
                    buffer = ''
                elif next_char == COMMENT_DELIM:
                    buffers.append(buffer)
                    buffer = ''
                    break
                elif next_char == ' ' and not in_str_lit:
                    buffers.append(buffer)
                    buffer = ''
                elif next_char == '\"':
                    buffers.append(buffer)
                    buffer = ''
                    in_str_lit = not in_str_lit
                i += 1
        # buffers = list(filter(lambda x: x != '' and x != ' ', buffers))
        pprint(buffers)
        pass

    @classmethod
    def tokenize_buffer(cls, buffer:str):
        pass

def main() -> None:
    logger:logging.Logger = logging.getLogger()
    if len(sys.argv) == 1: #bypass 
        filepath = pathlib.Path("./test_programs/hello.ty")
    else:
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

    lexer = Lexer()
    tokens = lexer(file_contents)

    pass

if __name__ == '__main__':
    main()
