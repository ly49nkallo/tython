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
import regex as re

from pprint import pprint

LOGFILE:pathlib.Path = pathlib.Path("./log.log")
VERSION:str = "0.1.0"

COMMENT_DELIM = '#'

@enum.unique
class TOKEN_TYPE(enum.Enum):
        # DATA TYPES
        INT32 = 'INT32'
        INT64 = 'INT64'
        REAL32 = 'REAL32'
        REAL64 = 'REAL64'
        CHAR8 = 'CHAR8'
        # MATHEMATICAL OPERATORS
        ASSIGN = '\='
        PLUS = '\+'
        MINUS = '\-'
        MUL = '\*'
        DIV = '\/'
        L_PAREN = '\('
        R_PAREN = '\)'
        # CONDITIONALS
        IF = 'IF'
        THEN = 'THEN'
        ELSE = 'ELSE'
        END = 'END'
        # FLOW CONTROL
        LABEL = 'LBL'
        GOTO = 'GOTO'
        # COMPARISON OPERATORS
        GREATER_THAN = '\>'
        LESS_THAN = '\<'
        GE_THAN = '>='
        LE_THAN = '<='
        EQUAL_TO = '=='
        # PROGRAM CONTROL
        PROGRAM = 'PROGRAM'
        IMPLICIT = 'IMPLICIT'
        CALL = 'CALL'
        # VARIABLE LITERALS
        STR_LIT = '\\".*\\"'
        INT_LIT = '\\d+'
        FLOAT_LIT = '\\d+\.\\d*'
        HEX_LIT = '0x[A-F0-9]+'
        BIN_LIT = '0b[01]+'
        # VARIABLES
        VAR = '[A-Z]\\d?'
        ARRAY_VAR = '@[A-Z]\\d?'
        # COMMANDS
        DISP = 'DISP'
        DISP_STR = 'DISPSTR'
        # STRUCTURE TOKENS
        EXPR = enum.auto()
        LINE_BREAK = enum.auto()


class Token(object):
    '''A lexical unit of code correspinding to a certain, specific function.'''
    def __init__(self, type:TOKEN_TYPE, value) -> None:
        assert isinstance(type, TOKEN_TYPE)
        self.type:TOKEN_TYPE = type
        self.value = value

    def __repr__(self) -> str:
        ret = str(self.type)
        if self.value: ret += f":{self.value}"
        return ret

class Lexer(object):
    '''Responsible for taking raw text input and generating a list of tokens.'''

    @classmethod
    def __call__(cls, text:str) -> list:
        # buffers = list(filter(lambda x: x != '' and x != ' ', buffers))
        cls.lexical_analysis(text)
        pass

    @classmethod
    def lexical_analysis(cls, text:str)->list:
        lines = text.split('\n')
        # remove blank lines
        lines = [l.strip() for l in lines if l != '']
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
                if curr_char == COMMENT_DELIM and not in_str_lit:
                    if buffer[:-1] != '':
                        buffers.append(buffer[:-1]) 
                    break
                elif curr_char == ' ' and not in_str_lit:
                    if buffer[:-1] != '':
                        buffers.append(buffer[:-1])
                    buffer = ''
                elif curr_char == '\"':
                    if not in_str_lit:
                        if buffer[:-1] != '':
                            buffers.append(buffer[:-1])
                        buffer = '\"'
                    else:
                        buffers.append(buffer)
                        buffer = ''
                    in_str_lit = not in_str_lit
                    print(f"set {in_str_lit=}")
                elif i == len(line) - 1:
                    buffers.append(buffer)
                i += 1
        pprint(buffers) 
        tokens = []
        for buffer in buffers:
            matched_pattern:typing.Optional[TOKEN_TYPE] = None
            for tt in TOKEN_TYPE:
                pattern = tt.value
                if pattern in list(range(10)): continue #ignore regular token types w/o pattern
                if re.fullmatch(pattern, buffer.upper()):
                    matched_pattern = pattern
                    break
            if matched_pattern is None:
                raise RuntimeError(f"Unable to match token {buffer}")
            tokens.append(Token(tt, buffer))

        pprint(tokens)

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
