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
import regex as re

from pprint import pprint

LOGFILE:pathlib.Path = pathlib.Path("./log.log")
COMMENT_DELIM = '#'

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
        # TRIG FUNCTIONS
        SIN = 'SIN'
        COS = 'COS'
        TAN = 'TAN'
        COT = 'COT'
        SEC = 'SEC'
        CSC = 'CSC'
        # ARRAY FUNCTIONS
        DIM = 'DIM'
        # STRUCTURE TOKENS
        COMMA = '\,'
        LINE_BREAK = 1
        EXPR = 2
        EOF = 3

REQUIRES_VALUE:set = {
        TOKEN_TYPE.STR_LIT, 
        TOKEN_TYPE.INT_LIT, 
        TOKEN_TYPE.FLOAT_LIT, 
        TOKEN_TYPE.HEX_LIT, 
        TOKEN_TYPE.BIN_LIT,
        TOKEN_TYPE.VAR,
        TOKEN_TYPE.ARRAY_VAR,
    }

class Token(object):
    '''A lexical unit of code correspinding to a certain, specific function.'''
    def __init__(self, type:TOKEN_TYPE, value:typing.Optional=None) -> None:
        assert isinstance(type, TOKEN_TYPE)
        self.type:TOKEN_TYPE = type
        self.value = value

    def __repr__(self) -> str:
        ret = str(self.type)
        if self.value: ret += f":{self.value}"
        return ret


class Parser(object):
    '''Responsible for taking raw text input and generating a list of tokens.'''

    @classmethod
    def lexical_analysis(cls, text:str) -> list:
        # buffers = list(filter(lambda x: x != '' and x != ' ', buffers))
        if DEBUG: print(text)
        buffers = []
        tokens = []
        buffer = ''
        i = 0
        in_str_lit:bool = False
        in_comment:bool = False
        while i < len(text):
            curr_char = text[i]
            next_char = text[i+1] if i+1<len(text) else None
            prev_char = text[i-1] if i-1>=0 else None
            buffer += curr_char
            if not in_comment:
                if curr_char == COMMENT_DELIM and not in_str_lit:
                    in_comment = True
                    if buffer[:-1] != '':
                        tokens.append(cls.analyze_buffer(buffer[:-1]))
                    
                elif curr_char == ' ' and not in_str_lit:
                    if buffer[:-1] != '':
                        tokens.append(cls.analyze_buffer(buffer[:-1]))
                    buffer = ''
                elif curr_char == '(':
                    if buffer[:-1] != '' and not in_str_lit:
                        tokens.append(cls.analyze_buffer(buffer[:-1]))
                    tokens.append(cls.analyze_buffer('('))
                    buffer = ''
                elif curr_char == ')':
                    if buffer[:-1] != '' and not in_str_lit:
                        tokens.append(cls.analyze_buffer(buffer[:-1]))
                    tokens.append(cls.analyze_buffer(')'))
                    buffer = ''
                elif curr_char == ',' and not in_str_lit:
                    if buffer[:-1] != '' and not in_str_lit:
                        tokens.append(cls.analyze_buffer(buffer[:-1]))
                    tokens.append(Token(TOKEN_TYPE.COMMA))
                    buffer = ''
                elif curr_char == '\"':
                    if not in_str_lit:
                        if buffer[:-1] != '':
                            tokens.append(cls.analyze_buffer(buffer[:-1]))
                        buffer = '\"'
                    else:
                        tokens.append(cls.analyze_buffer(buffer))
                        buffer = ''
                    in_str_lit = not in_str_lit
            if curr_char == '\n':
                print('new line')
                if buffer[:-1] != '' and not in_comment:
                    tokens.append(cls.analyze_buffer(buffer[:-1]))
                tokens.append(Token(TOKEN_TYPE.LINE_BREAK))
                buffer = ''
                in_str_lit = False
                in_comment = False
            elif i == len(text) - 1:
                if buffer != '':
                    tokens.append(cls.analyze_buffer(buffer))
            i += 1
        if DEBUG: pprint(buffers)
        for buffer in buffers:
            cls.analyze_buffer(buffer, tokens)
        tokens.append(Token(TOKEN_TYPE.EOF))
        if DEBUG: pprint(tokens)

    @classmethod
    def analyze_buffer(cls, buffer:str) -> Token:
        matched_token:typing.Optional[TOKEN_TYPE] = None
        for tt in TOKEN_TYPE:
            pattern = tt.value
            if isinstance(pattern, int): continue #ignore regular token types w/o pattern
            if re.fullmatch(pattern, buffer.upper()):
                matched_token = tt
                break
        if matched_token is None:
            raise RuntimeError(f"Unable to match token <{buffer}>")
        if tt in REQUIRES_VALUE:
            token = Token(matched_token, value=buffer)
        else:
            token = Token(matched_token)
        return token

    @classmethod
    def syntax_analysis(cls, tokens:list):
        class Node:
            def __init__(self, token:Token, children:list):
                self.token:Token = token
                self.children:list = children

            def is_leaf(self) -> bool:
                return (len(self.children) == 0)

            def __repr__(self):
                return f"Node({repr(self.token)})"
        
    
VERSION:tuple = (0, 1, 0)
def main() -> None:
    logger:logging.Logger = logging.getLogger()
    
    # Argument Parser
    parser = argparse.ArgumentParser(description=f'TYTHON Compiler {VERSION}')
    parser.add_argument('input_file')
    parser.add_argument('-o', '--output')
    parser.add_argument('-c', '--compile', action='store_true', default=False)
    parser.add_argument('-i', '--interpret', action='store_true', default=False)
    
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('-v', '--version', action='version', 
                        version=f'Tython {VERSION[0]}.{VERSION[1]}.{VERSION[2]}')
    args = parser.parse_args()
    filepath:pathlib.Path = pathlib.Path(args.input_file)

    # Configure Debug setting
    global DEBUG
    DEBUG = args.debug
    if DEBUG: print(f'{args.debug=}')

    # Configure compilation setting
    global COMPILE
    if args.compile and args.interpret: 
        raise SyntaxError("Cannot compile and interpret simultaneously")
    if not (args.compile or args.interpret):
        COMPILE = True
    if args.compile:
        COMPILE = True
    if args.interpret:
        COMPILE = False

    # Retrive file contents
    with open(filepath, 'r') as f:
        file_contents = f.read()

    # Initialize lexer
    tokens = Parser.lexical_analysis(file_contents)
    tree = Parser.syntax_analysis(tokens)
    pass

if __name__ == '__main__':
    main()
