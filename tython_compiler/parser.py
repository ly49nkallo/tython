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

COMMENT_DELIM = '#'
DEBUG = False

class Node(object):
    def __init__(self, token:Token, children:list=[], /, name:str=None):
        self.name:typing.Optional[str] = name
        self.token:Token = token
        self.children:list = children

    def is_leaf(self) -> bool:
        return (len(self.children) == 0)

    def append(self, other:'Node'):
        assert isinstance(other, Node), f"Expected Node, got {type(other)} instead"
        self.children.append(other)

    def _repr_helper(self, tabs:int):
        if self.name is not None: ret = self.name
        else: ret = repr(self.token)[len("TOKEN_TYPE")+1:]
        if len(self.children) != 0: ret += '\n'
        for c in self.children:
            assert isinstance(c, Node), str(type(c))
            ret += ' ' * (4*tabs) + c._repr_helper(tabs+1) + '\n' #RECURSION >:(
        if len(self.children) != 0: 
            ret = ret[:-1]
            #ret += ' ' * (4*tabs) # neater this way
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
        # digest leading newlines
        i = 0
        for token in tokens:
            if token.type == TOKEN_TYPE.LINE_BREAK:
                i += 1
            else: break
        tokens = tokens[i:]
        # digest trailing newlines
        i = 0
        for token in reversed(tokens):
            if token.type == TOKEN_TYPE.LINE_BREAK:
                i += 1
            else: break
        tokens = tokens[:-i]
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
        class StackFrame:
            def __init__(self, content, pointer):
                self.content = content
                self.pointer = pointer

        def handle_expr(tokens:list) -> Node:
            '''
            MUL -> (NUM|EXPR) * (NUM|EXPR)
            ADD -> (NUM|EXPR) + (NUM|EXPR)
            EXPR -> \( .* )
            NUM -> (0-9)+
            '''
            # Steps
            # 1. Recursively evaluate parentheses
            # 2. In reverse order of operation precedence, find all operations and combine left to right,
            #    calling this function recursively to generate the node below
            # Only this function can create EXPR nodes
            root_node = Node(Token(TOKEN_TYPE.EXPR, tokens[0].line_number))
            nodes = [Node(token) for token in tokens]
            new_nodes = []
            scan = []
            depth = 0
            for node in nodes:
                if node.token.type == TOKEN_TYPE.L_PAREN:
                    depth += 1
                elif node.token.type == TOKEN_TYPE.R_PAREN:
                    depth -= 1
                    if depth < 0:
                        raise SyntaxError("Too many right parentheses")
                    if depth == 0:
                        scan.append(node)
                if depth == 0:
                    if node.token.type != TOKEN_TYPE.R_PAREN:
                        new_nodes.append(node)
                    if len(scan) > 0:
                        new_node = handle_expr([s.token for s in scan][1:-1])
                        scan = []
                        new_nodes.append(new_node)
                elif depth > 0:
                        scan.append(node)
            if depth != 0:
                raise SyntaxError("Not all parentheses closed")
            nodes = new_nodes
            new_nodes = nodes.copy()
            for op_level in reversed(ORDER_OF_OPERATIONS):
                for op in op_level:
                    i = 0
                    while i < len(new_nodes):
                        node = new_nodes[i]
                        if node.token.type == op and len(node.children) == 0:
                            try: # @BUG nodes doesnt contain the correct information
                                lhs = new_nodes[i-1]
                                rhs = new_nodes[i+1]
                                assert i-1 >= 0
                            except:
                                raise SyntaxError("Structure of expression invalid")
                            if not (lhs.token.type in NUMERALS or lhs.token.type == TOKEN_TYPE.EXPR) and len(lhs.children) == 0:
                                raise SyntaxError(f"Structure of expression invalid, got {lhs.token.type} instead")
                            if not (rhs.token.type in NUMERALS or rhs.token.type == TOKEN_TYPE.EXPR) and len(lhs.children) == 0:
                                raise SyntaxError(f"Structure of expression invalid, got {rhs.token.type} instead")
                            new_node = node
                            new_node.children = [lhs, rhs]
                            new_nodes = new_nodes[0:i-1] + new_nodes[i+2:]
                            new_nodes.insert(i-1, new_node)
                            i -= 3
                        i += 1

            root_node.children = new_nodes
            return root_node
            
            


        if tokens[0].type is not TOKEN_TYPE.PROGRAM or tokens[1].type is not TOKEN_TYPE.STR_LIT:
            raise SyntaxError(f"Program must begin with a program name, got {tokens[0]} and {tokens[1]} instead")

        root_node = Node(Token(TOKEN_TYPE.PROG, 0), [])
        while i < len(tokens):
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
                i += 2
            # INT64 = 'INT64'
            elif curr.type == TOKEN_TYPE.INT64:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise SyntaxError(f"Token INT64 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR after INT64, got {next} instead")
                root_node.append(Node(curr, [Node(next, [])]))
                i += 2
            # REAL32 = 'REAL32'
            elif curr.type == TOKEN_TYPE.REAL32:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise SyntaxError(f"Token REAL32 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR after REAL32, got {next} instead")
                root_node.append(Node(curr, [Node(next, [])]))
                i += 2
            # REAL64 = 'REAL64'
            elif curr.type == TOKEN_TYPE.REAL64:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise SyntaxError(f"Token REAL64 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR after REAL32, got {next} instead")
                root_node.append(Node(curr, [Node(next, [])]))
                i += 2
            # CHAR8 = 'CHAR8'
            elif curr.type == TOKEN_TYPE.CHAR8:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise SyntaxError(f"Token CHAR8 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR after CHAR8, got {next} instead")
                root_node.append(Node(curr, [Node(next, [])]))
                i += 2
            # # MATHEMATICAL OPERATORS
            # ASSIGN = '\='
            elif curr.type == TOKEN_TYPE.ASSIGN:
                if prev.type != TOKEN_TYPE.VAR: raise SyntaxError(f"Expected VAR before ASSIGN, got {prev} instead")
                j = i+1
                scan = []
                while tokens[j].type != TOKEN_TYPE.LINE_BREAK and tokens[j].type != TOKEN_TYPE.EOF and j < len(tokens):
                    scan.append(tokens[j])
                    j += 1
                expr_node = handle_expr(scan)
                root_node.append(Node(curr, [Node(prev), expr_node]))
                i += 1


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
            if DEBUG: print(i)
        return root_node