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
from .error import CompilationError

COMMENT_DELIM = '#'
DEBUG = False


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
                if not in_comment:
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
    def handle_parenthesis(cls, tokens:list, mode:str) -> list:
        '''
        Args:
            tokens (list) : the stream of tokens that will be searched for parenthesis
            mode (str) : a string specifying how the function will handle parentheses
                "EXPR" : Compile as mathematical expression
                "LOGIC" : Compile as logical expression
        '''

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
                    raise CompilationError("Too many right parentheses")
                if depth == 0:
                    scan.append(node)
            if depth == 0:
                if node.token.type != TOKEN_TYPE.R_PAREN:
                    new_nodes.append(node)
                if len(scan) > 0:
                    if mode == "EXPR":
                        new_node = cls.handle_expr([s.token for s in scan][1:-1])
                    elif mode == "LOGIC":
                        new_node = cls.handle_logical_expr([s.token for s in scan][1:-1])
                    else:
                        raise NameError(f'mode {mode} not supported')
                    scan = []
                    new_nodes.append(new_node)
            elif depth > 0:
                    scan.append(node)

        if depth != 0:
            raise CompilationError("Not all parentheses closed")
        return new_nodes

    @classmethod
    def handle_expr(cls, tokens:list) -> Node:
        '''Handles the creation of mathematical EXPR nodes'''
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

        # quick return for lone number
        if len(tokens) == 1:
            if tokens[0].type in NUMERALS:
                return Node(tokens[0])

        root_node = Node(Token(TOKEN_TYPE.EXPR, tokens[0].line_number))
        new_nodes = cls.handle_parenthesis(tokens, mode="EXPR")
        # Smushes together operation nodes in order of operations
        for op_level in reversed(ORDER_OF_OPERATIONS):
            for op in op_level:
                i = 0
                while i < len(new_nodes):
                    node:Node = new_nodes[i]
                    if node.token.type == op and node.is_leaf():
                        try: #nodes doesnt contain the correct information
                            lhs:Node = new_nodes[i-1]
                            rhs:Node = new_nodes[i+1]
                            assert i-1 >= 0
                        except:
                            raise CompilationError("Structure of expression invalid")
                        if not (lhs.token.type in NUMERALS or lhs.token.type == TOKEN_TYPE.EXPR) and len(lhs.children) == 0:
                            raise CompilationError(f"Structure of expression invalid, got {lhs.token.type} instead")
                        if not (rhs.token.type in NUMERALS or rhs.token.type == TOKEN_TYPE.EXPR) and len(lhs.children) == 0:
                            raise CompilationError(f"Structure of expression invalid, got {rhs.token.type} instead")
                        new_node = node
                        new_node.children = [lhs, rhs]
                        new_nodes = new_nodes[0:i-1] + new_nodes[i+2:]
                        new_nodes.insert(i-1, new_node)
                        i -= 3
                    i += 1
        # Attempt to assign expressions to functions
        i = 0
        while i < len(new_nodes):
            node:Node = new_nodes[i]
            if node.token.type in MATH_FUNCTIONS:
                if i == len(new_nodes)-1:
                    raise CompilationError(f"Function is last node in expression: {new_nodes}")
                next_node:Node = new_nodes[i+1]
                if next_node.token.type not in NUMERALS and next_node.token.type != TOKEN_TYPE.EXPR:
                    raise CompilationError(f"Expected some input parameter to {node}, but got {next_node} instead")

                new_node:Node = node
                new_node.children = [next_node]
                new_nodes = new_nodes[0:i] + new_nodes[i+2:]
                new_nodes.insert(i, new_node)
            i += 1
        # make sure there arnt any orphaned numbers left
        if len([n for n in new_nodes if n.token.type in NUMERALS]) != 1:
            for node in new_nodes:
                if node.token.type in NUMERALS:
                    raise CompilationError(f"Orphaned numeral token {node.token} from nodes while processing {tokens}")
        root_node.children = new_nodes
        return root_node

    @classmethod
    def handle_bool_expr(cls, tokens:list) -> Node:
        '''
        Handles a boolean expr (BOOL_EXPR) Nodes of the form
        EXPR ("<", "<=", ">", ">=", "!=", "==") EXPR
        and returns a node BOOL_EXPR
        '''
        root_node = Node(Token(TOKEN_TYPE.BOOL_EXPR, line_number=tokens[0].line_number))
        # ensure there is exactly one boolean operator in the token stream
        c = 0
        for idx, token in enumerate(tokens):
            if token.type in BOOLEAN_OPERATORS:
                c += 1
                op_idx = idx
        if c == 0:
            raise CompilationError(f"Bool expr expects at least one boolean operator. Got tokens {tokens}.")
        elif c > 1:
            raise CompilationError(f"Expected at most one boolean operator. Got tokens {tokens}.")
        lhs = cls.handle_expr(tokens[:op_idx])
        rhs = cls.handle_expr(tokens[op_idx+1:])
        op = tokens[op_idx]
        root_node.append_child(Node(op, [lhs, rhs])) #@TODO: Why is node.append a bug?? Circular reference?
        return root_node

    @classmethod 
    def handle_logical_expr(cls, tokens:list) -> Node:
        '''
        Handles a logical expr (LOGIC_EXPR) Nodes of the form
        (BOOL_EXPR | LOGIC_EXPR) ("AND", "OR", "NOT", "NOR", "XOR", "NAND") (BOOL_EXPR | LOGIC_EXPR)
        and returns a node LOGIC_EXPR or a BOOL_EXPR (depending on conciceness)
        '''
        # fast return for statements with no logical tokens
        if not any([token.type in LOGICAL_OPERATORS for token in tokens]):
            return cls.handle_bool_expr(tokens)

        root_node = Node(Token(TOKEN_TYPE.LOGIC_EXPR, line_number=tokens[0].line_number))
        new_nodes = cls.handle_parenthesis(tokens, "LOGIC")
        c = 0
        for idx, node in enumerate(new_nodes):
            if node.token.type in LOGICAL_OPERATORS:
                c += 1
                op_idx = idx
        if c == 0:
            raise CompilationError(f"Logical Expr expects at least one logical operator, got tokens {tokens}")
        if c > 1:
            raise CompilationError(f"Logical Expr expects at most one logical operator, got tokens {tokens}")
        #CODE
        new_node:Node = new_nodes[op_idx]
        new_node.children = new_nodes[:op_idx] + new_nodes[op_idx+1:]
        root_node.children = [new_node]
        return root_node

    @classmethod
    def syntax_analysis(cls, tokens:list):
        '''Take list of tokens and create a (potentially illegal) AST'''

        if tokens[0].type is not TOKEN_TYPE.PROGRAM or tokens[1].type is not TOKEN_TYPE.STR_LIT:
            raise CompilationError(f"Program must begin with a program name, got {tokens[0]} and {tokens[1]} instead")

        root_node = Node(Token(TOKEN_TYPE.PROG, 0), [])
        cls.analyze_block(tokens, root_node)
        return root_node


    @classmethod
    def analyze_block(cls, tokens:list, root_node:Node):
        '''Perform the iterative analysis of the list of tokens, returning a single root node specified by the parameter'''
        i = 0
        while i < len(tokens):
            prev_prev:Token = tokens[i-2] if i-2>=0 else None
            prev:Token = tokens[i-1] if i-1>=0 else None
            curr:Token = tokens[i]
            next:Token = tokens[i+1] if i+1<len(tokens) else None
            next_next:Token = tokens[i+2] if i+2<len(tokens) else None
            if False: pass
            # DATA TYPES
            # INT32 = 'INT32'
            elif curr.type == TOKEN_TYPE.INT32:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise CompilationError(f"Token INT32 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise CompilationError(f"Expected VAR after INT32, got {next} instead")
                root_node.append_child(Node(curr, [Node(next, [])]))
                i += 2
            # INT64 = 'INT64'
            elif curr.type == TOKEN_TYPE.INT64:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise CompilationError(f"Token INT64 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise CompilationError(f"Expected VAR after INT64, got {next} instead")
                root_node.append_child(Node(curr, [Node(next, [])]))
                i += 2
            # REAL32 = 'REAL32'
            elif curr.type == TOKEN_TYPE.REAL32:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise CompilationError(f"Token REAL32 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise CompilationError(f"Expected VAR after REAL32, got {next} instead")
                root_node.append_child(Node(curr, [Node(next, [])]))
                i += 2
            # REAL64 = 'REAL64'
            elif curr.type == TOKEN_TYPE.REAL64:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise CompilationError(f"Token REAL64 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise CompilationError(f"Expected VAR after REAL32, got {next} instead")
                root_node.append_child(Node(curr, [Node(next, [])]))
                i += 2
            # CHAR8 = 'CHAR8'
            elif curr.type == TOKEN_TYPE.CHAR8:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise CompilationError(f"Token CHAR8 must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise CompilationError(f"Expected VAR after CHAR8, got {next} instead")
                root_node.append_child(Node(curr, [Node(next, [])]))
                i += 2
            # # MATHEMATICAL OPERATORS
            # ASSIGN = '\='
            elif curr.type == TOKEN_TYPE.VAR:
                if next.type == TOKEN_TYPE.ASSIGN:
                    j = i+2
                    scan = []
                    while tokens[j].type != TOKEN_TYPE.LINE_BREAK and tokens[j].type != TOKEN_TYPE.EOF and j < len(tokens):
                        scan.append(tokens[j])
                        j += 1
                    expr_node = cls.handle_expr(scan)
                    root_node.append_child(Node(curr, [Node(prev), expr_node]))
                    i = j+1
                else:
                    raise CompilationError("Expected expression after variable instance")
            # PLUS = '\+':
            # MINUS = '\-'
            # MUL = '\*'
            # DIV = '\/'
            # L_PAREN = '\('
            # R_PAREN = '\)'
            # # CONDITIONALS
            # IF = 'IF'
            elif curr.type == TOKEN_TYPE.IF:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise CompilationError(f"Token IF must be first token in line")
                # Scan rest of line
                j = i+1
                scan = []
                while tokens[j].type not in {TOKEN_TYPE.LINE_BREAK, TOKEN_TYPE.EOF, TOKEN_TYPE.THEN} and j < len(tokens):
                    scan.append(tokens[j])
                    j += 1
                expr_node = cls.handle_logical_expr(scan)
                # detect if in 'if then ... end clause'
                if tokens[j].type == TOKEN_TYPE.THEN:
                    block_node = Node(Token(TOKEN_TYPE.BLOCK, -1))
                    scan = []
                    while tokens[j].type != TOKEN_TYPE.END:
                        if tokens[j].type == TOKEN_TYPE.EOF:
                            raise CompilationError("IF-THEN clause not closed with END token")
                        scan.append(tokens[j])
                        j += 1
                    if DEBUG: print(f"{scan=}")
                    cls.analyze_block(scan, block_node)
                else:
                    block_node = Node(Token(TOKEN_TYPE.BLOCK, -1))
                    scan = []
                    if tokens[j].type != TOKEN_TYPE.LINE_BREAK: #BUG
                        raise CompilationError(f"IF statement must close with LINE_BREAK or THEN, got {tokens[j]}")
                    j += 1
                    while tokens[j].type not in {TOKEN_TYPE.EOF, TOKEN_TYPE.LINE_BREAK}:
                        scan.append(tokens[j])
                        j += 1
                    if DEBUG: print(f"{scan=}")
                    cls.analyze_block(scan, block_node)
                if len(block_node.children) == 0:
                    raise CompilationError("IF statement must be followed by code")
                root_node.append_child(Node(curr, [expr_node, block_node]))

                    
                i = j+1

            # THEN = 'THEN'
            # ELSE = 'ELSE'
            # END = 'END'
            # # FLOW CONTROL
            # LABEL = 'LBL'
            elif curr.type == TOKEN_TYPE.LABEL:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise CompilationError(f"Token LABEL must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise CompilationError(f"Expected VAR after LABEL, got {next} instead")
                root_node.append_child(Node(curr, [Node(next, [])]))
                i += 2
            # GOTO = 'GOTO'
            elif curr.type == TOKEN_TYPE.GOTO:
                if prev.type != TOKEN_TYPE.LINE_BREAK: raise CompilationError(f"Token GOTO must be first token in line")
                if next.type != TOKEN_TYPE.VAR: raise CompilationError(f"Expected VAR after GOTO, got {next} instead")
                root_node.append_child(Node(curr, [Node(next, [])]))
                i += 2
            # # PROGRAM CONTROL
            # PROGRAM = 'PROGRAM'
            elif curr.type == TOKEN_TYPE.PROGRAM:
                if i != 0: raise CompilationError("PROGRAM token must be first in program")
                if next.type != TOKEN_TYPE.STR_LIT:
                    raise CompilationError(f"Expected STR_LIT, got {next.type}")
                root_node.append_child(Node(curr, [Node(next, [])]))
                i += 2 # digest next token
            # VERSION = 'VERSION'
            elif curr.type == TOKEN_TYPE.VERSION:
                if not all([tokens[j].type == TOKEN_TYPE.INT_LIT for j in range(i+1, i+4)]):
                    raise CompilationError(f"Expected INT_LIT after VERSION token, got {[tokens[j].type for j in range(i+1, i+4)]}")
                root_node.append_child(Node(curr, [Node(tokens[j], []) for j in range(i+1, i+4)]))
                i += 4
            # IMPLICIT = 'IMPLICIT'
            elif curr.type == TOKEN_TYPE.IMPLICIT:
                if next.type not in DATA_TYPES:
                    raise CompilationError(f"Expected DATA_TYPE after IMPLICIT, got {next.type} instead")
                if next_next.type != TOKEN_TYPE.VAR:
                    raise CompilationError(f"Expected VAR in IMPLICIT statement, got {next_next.type} instead")
                root_node.append_child(Node(curr, [Node(next), Node(next_next)]))
                i += 3
            # CALL = 'CALL'
            elif curr.type == TOKEN_TYPE.CALL:
                raise NotImplementedError()
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
            elif curr.type == TOKEN_TYPE.DISP:
                if next.type != TOKEN_TYPE.VAR and next.type not in REQUIRES_VALUE:
                    raise CompilationError(f"Display command expects variable or literal after, got {next} instead")
                root_node.append_child(Node(curr, [Node(next, [])])) #BUG Causes a circular reference curr->next->curr->next &c.
                i += 2
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
            elif curr.type == TOKEN_TYPE.LINE_BREAK:
                i += 1
            # EOF = 2
            elif curr.type == TOKEN_TYPE.EOF:
                assert i == len(tokens) - 1 # last token
                i += 1
            # EXPR = 3
            # PROG = 4
            # BIN_EXPR = 5
            # STMT = 6
            # BLOCK = 7
            else:
                if DEBUG: print(f'failed to parse token {curr}.')
                i += 1
        return root_node
