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
        NOT_EQUAL_TO = '\!='
        # PROGRAM CONTROL
        PROGRAM = 'PROGRAM'
        VERSION = 'VERSION'
        IMPLICIT = 'IMPLICIT'
        CALL = 'CALL'
        # VARIABLE LITERALS
        CHAR_LIT = '\'.\''
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
        EOF = 2
        EXPR = 3
        PROG = 4
        BIN_EXPR = 5
        STMT = 6


REQUIRES_VALUE:set = {
        TOKEN_TYPE.CHAR_LIT,
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
    def __init__(self, type:TOKEN_TYPE, line_number:int, value=None):
        assert isinstance(type, TOKEN_TYPE)
        self.type:TOKEN_TYPE = type
        self.value = value
        self.line_number:int = line_number

    def __repr__(self) -> str:
        ret = str(self.type)
        if self.value: ret += f":{self.value}"
        if DEBUG: ret += f":line {self.line_number}"
        return ret

class Node(object):
    def __init__(self, token:Token, children:list, name:str=None):
        self.name:typing.Optional[str] = name
        self.token:Token = token
        self.children:list = children

    def is_leaf(self) -> bool:
        return (len(self.children) == 0)

    def append(self, other:'Node'):
        assert isinstance(other, Node)
        self.children.append(other)

    def _repr_helper(self, tabs:int):
        if self.name is not None: ret = self.name
        else: ret = repr(self.token)
        if len(self.children) != 0: ret += '\n'
        for c in self.children:
            assert isinstance(c, Node), str(type(c))
            ret += ' ' * (4*tabs) + c._repr_helper(tabs+1) + '\n'
        if len(self.children) != 0: ret += ' ' * (4*tabs)
        return ret

    def __repr__(self):
        return self._repr_helper(1)

class Parser(object):
    '''Parse code into AST'''
    @classmethod
    def lexical_analysis(cls, text:str) -> list:
        '''Responsible for taking raw text input and generating a list of tokens.'''
        # buffers = list(filter(lambda x: x != '' and x != ' ', buffers))
        if DEBUG: print(text)
        buffers = []
        tokens = []
        buffer = ''
        i = 0
        current_line_number = 1
        in_str_lit:bool = False
        in_comment:bool = False
        while i < len(text):
            curr_char = text[i]
            # next_char = text[i+1] if i+1<len(text) else None
            # prev_char = text[i-1] if i-1>=0 else None
            buffer += curr_char
            if not in_comment:
                if curr_char == COMMENT_DELIM and not in_str_lit:
                    in_comment = True
                    if buffer[:-1] != '':
                        tokens.append(cls.analyze_buffer(buffer[:-1], current_line_number))
                elif curr_char == ' ' and not in_str_lit:
                    if buffer[:-1] != '':
                        tokens.append(cls.analyze_buffer(buffer[:-1], current_line_number))
                    buffer = ''
                elif curr_char == '(':
                    if buffer[:-1] != '' and not in_str_lit:
                        tokens.append(cls.analyze_buffer(buffer[:-1], current_line_number))
                    tokens.append(cls.analyze_buffer('(', current_line_number))
                    buffer = ''
                elif curr_char == ')':
                    if buffer[:-1] != '' and not in_str_lit:
                        tokens.append(cls.analyze_buffer(buffer[:-1], current_line_number))
                    tokens.append(cls.analyze_buffer(')', current_line_number))
                    buffer = ''
                elif curr_char == ',' and not in_str_lit:
                    if buffer[:-1] != '' and not in_str_lit:
                        tokens.append(cls.analyze_buffer(buffer[:-1], current_line_number))
                    tokens.append(Token(TOKEN_TYPE.COMMA, current_line_number))
                    buffer = ''
                elif curr_char == '\"':
                    if not in_str_lit:
                        if buffer[:-1] != '':
                            tokens.append(cls.analyze_buffer(buffer[:-1], current_line_number))
                        buffer = '\"'
                    else:
                        tokens.append(cls.analyze_buffer(buffer, current_line_number))
                        buffer = ''
                    in_str_lit = not in_str_lit
            if curr_char == '\n':
                if buffer[:-1] != '' and not in_comment:
                    tokens.append(cls.analyze_buffer(buffer[:-1], current_line_number))
                tokens.append(Token(TOKEN_TYPE.LINE_BREAK, current_line_number))
                buffer = ''
                in_str_lit = False
                in_comment = False
                current_line_number += 1
            elif i == len(text) - 1:
                if buffer != '':
                    tokens.append(cls.analyze_buffer(buffer))
            i += 1
        if DEBUG: pprint(buffers)
        for buffer in buffers:
            cls.analyze_buffer(buffer, tokens)
        tokens.append(Token(TOKEN_TYPE.EOF, current_line_number))
        if DEBUG: pprint(tokens)
        return tokens

    @classmethod
    def analyze_buffer(cls, buffer:str, line_number:int) -> Token:
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
            token = Token(matched_token, line_number, value=buffer)
        else:
            token = Token(matched_token, line_number)
        return token

    @classmethod
    def syntax_analysis(cls, tokens:list):
        '''Take list of tokens and create a (potentially illegal) AST'''
        i = 0
        def handle_expr(tokens:list) -> Node:
            return

        if tokens[0].type is not TOKEN_TYPE.PROGRAM or tokens[1].type is not TOKEN_TYPE.STR_LIT:
            raise SyntaxError(f"Program must begin with a program name, got {tokens[0]} and {tokens[1]} instead")

        root_node = Node(TOKEN_TYPE.PROG, [])
        while i < len(tokens):
            nodes = [Node(t, []) for t in tokens]
            prev_prev = tokens[i-2] if i-2>=0 else None
            prev = tokens[i-1] if i-1>=0 else None
            curr = tokens[i]
            next = tokens[i+1] if i+1<len(tokens) else None
            next_next = tokens[i+2] if i+2<len(tokens) else None
            if False: pass
            # DATA TYPES
            # INT32 = 'INT32'
            elif curr.type == TOKEN_TYPE.INT32:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise SyntaxError(f"Token INT32 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR after INT32, got {next} instead")
                root_node.append(Node(curr, [Node(next, [])]))
            # INT64 = 'INT64'
            elif curr.type == TOKEN_TYPE.INT64:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise SyntaxError(f"Token INT64 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR after INT64, got {next} instead")
                root_node.append(Node(curr, [Node(next, [])]))
            # REAL32 = 'REAL32'
            elif curr.type == TOKEN_TYPE.REAL32:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise SyntaxError(f"Token REAL32 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR after REAL32, got {next} instead")
                root_node.append(Node(curr, [Node(next, [])]))
            # REAL64 = 'REAL64'
            elif curr.type == TOKEN_TYPE.REAL64:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise SyntaxError(f"Token REAL64 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR after REAL32, got {next} instead")
                root_node.append(Node(curr, [Node(next, [])]))
            # CHAR8 = 'CHAR8'
            elif curr.type == TOKEN_TYPE.CHAR8:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise SyntaxError(f"Token CHAR8 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR after CHAR8, got {next} instead")
                root_node.append(Node(curr, [Node(next, [])]))
            # # MATHEMATICAL OPERATORS
            # ASSIGN = '\='
            elif curr.type == TOKEN_TYPE.ASSIGN:
                if prev.type == TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR after ASSIGN, got {prev} instead")
                if next.type != TOKEN_TYPE.EXPR and next.type != TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR or EXPR after ASSIGN, got {next} instead")

            # PLUS = '\+':
            # MINUS = '\-'
            # MUL = '\*'
            # DIV = '\/'
            # L_PAREN = '\('
            # R_PAREN = '\)'
            # # CONDITIONALS
            # IF = 'IF'
            elif curr.type == TOKEN_TYPE.IF:
                i += 1
                # if tokens[i+1].type != @TODO
            # THEN = 'THEN'
            # ELSE = 'ELSE'
            # END = 'END'
            # # FLOW CONTROL
            # LABEL = 'LBL'
            elif curr.type == TOKEN_TYPE.LABEL:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise SyntaxError(f"Token LABEL must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR after LABEL, got {next} instead")
                root_node.append(Node(curr, [Node(next, [])]))
                i += 2
            # GOTO = 'GOTO'
            elif curr.type == TOKEN_TYPE.GOTO:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise SyntaxError(f"Token GOTO must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR after GOTO, got {next} instead")
                root_node.append(Node(curr, [Node(next, [])]))
                i += 2
            # # COMPARISON OPERATORS
            # GREATER_THAN = '\>'
            # LESS_THAN = '\<'
            # GE_THAN = '>='
            # LE_THAN = '<='
            # EQUAL_TO = '=='
            # NOT_EQUAL_TO = '\!='
            # # PROGRAM CONTROL
            # PROGRAM = 'PROGRAM'
            elif curr.type == TOKEN_TYPE.PROGRAM:
                if i != 0: raise SyntaxError("PROGRAM token must be first in program")
                if next.type != TOKEN_TYPE.STR_LIT:
                    raise SyntaxError(f"Expected STR_LIT, got {next.type}")
                root_node.append(Node(curr, [Node(next, [])]))
                i += 2 # digest next token
            # VERSION = 'VERSION'
            elif curr.type == TOKEN_TYPE.VERSION:
                if not all([tokens[j].type == TOKEN_TYPE.INT_LIT for j in range(i+1, i+4)]):
                    raise SyntaxError(f"Expected INT_LIT after VERSION token, got {[tokens[j].type for j in range(i+1, i+4)]}")
                root_node.append(Node(curr, [Node(tokens[j], []) for j in range(i+1, i+4)]))
                i += 4
            # IMPLICIT = 'IMPLICIT'
            # CALL = 'CALL'
            # # VARIABLE LITERALS
            # CHAR_LIT = '\'.\''
            # STR_LIT = '\\".*\\"'
            # INT_LIT = '\\d+'
            # FLOAT_LIT = '\\d+\.\\d*'
            # HEX_LIT = '0x[A-F0-9]+'
            # BIN_LIT = '0b[01]+'
            # # VARIABLES
            # VAR = '[A-Z]\\d?'
            # ARRAY_VAR = '@[A-Z]\\d?'
            # # COMMANDS
            # DISP = 'DISP'
            # DISP_STR = 'DISPSTR'
            # # TRIG FUNCTIONS
            # SIN = 'SIN'
            # COS = 'COS'
            # TAN = 'TAN'
            # COT = 'COT'
            # SEC = 'SEC'
            # CSC = 'CSC'
            # # ARRAY FUNCTIONS
            # DIM = 'DIM'
            # # STRUCTURE TOKENS
            # COMMA = '\,'
            # LINE_BREAK = 1
            # EOF = 2
            # EXPR = 3
            # PROG = 4
            # BIN_EXPR = 5
            # STMT = 6
            else:
                if DEBUG: print(f'failed to parse token {curr}.')
                i += 1

        return root_node

class Interpreter(object):
    def __init__(self):
        self.variables = dict()

    def assign(self, var:str, value):
        assert re.fullmatch('[A-Z]\\d?', var), f'Variable assign for invalid variable {var}'
        self.variables.update({var: value})

    pass

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
    print(tree)
    pass

if __name__ == '__main__':
    main()

