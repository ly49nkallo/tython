"""Define AST Interpreter
Author: Ty Brennan
"""
import os, sys
import functools
import time
import enum
import typing
import re
import abc
import ctypes

from pprint import pprint
from .token_types import *
from .token import Token
from .node import Node
from .error import InterpreterError



class Interpreter():
    """Define an interpreter to handle code execution"""
    type_map = dict() # type_map["A0"] = Datatypes.[...]
    variables = dict() # variables["A0"] = [...]
    array_variables = dict() # array_variables["A0"] = [...]

    @classmethod
    def clear_variables(cls):
        '''Erase information relataing to all variables (including array variables)'''
        cls.type_map = dict()
        cls.variables = dict()
        cls.array_variables = dict()

    @classmethod
    def interpret(cls, tree:Node):
        '''Entry point for the interpreting loop. Wraps 'interpret_block' and handles program meta-data'''
        root_node = tree
        print("Begin interpreter")
        assert root_node.token.type == TOKEN_TYPE.PROG
        program_name:str = tree.children[0].children[0].token.value
        print(f'{program_name=}')
        cls.interpret_block(root_node)

    @classmethod
    def assign_datatype(cls, var:str, dtype:Datatypes):
        '''
        @Params
            var:str             The variable name to assign to the
            dtype:Datatypes     The datatype the variable will be assigned to
        '''
        assert isinstance(var, str) and isinstance(dtype, Datatypes), f"{var.type=}, {dtype.type=}"
        cls.type_map[var.upper()] = dtype
    
    @staticmethod
    def evaluate_expression(expression_root_node:Node) -> typing.Union[Integer32, Integer64, Float32, Float64]:
        '''
        @Param
            expression_root_node:Node       The node that lies at the root of the expression to be evaluated
        @Returns
            value:int | float               The value that the expression evaluates to
        '''
        # base case
        rtt = expression_root_node.token.type # root node token type
        if rtt == TOKEN_TYPE.EXPR:
            return Interpreter.evaluate_expression(expression_root_node)
        elif rtt in NUMERALS:
            if rtt == TOKEN_TYPE.INT32:
                ...
            elif rtt == TOKEN_TYPE.INT64:
                ...
            elif rtt == TOKEN_TYPE.REAL32:
                ...
            elif rtt == TOKEN_TYPE.REAL64:
                ...
                ...
        ...

    @classmethod
    def interpret_block(cls, root_node:Node):
        for node in root_node.children:
            assert isinstance(node, Node)
            token = node.token
            children = node.children
            if token.type == TOKEN_TYPE.IMPLICIT:
                dtype = match_token_to_datatype(children[0].token)
                var = children[1].token.value
                cls.assign_datatype(var, dtype)
                print(cls.type_map)
            elif token.type == TOKEN_TYPE.ASSIGN:
                var = children[0].token.value

