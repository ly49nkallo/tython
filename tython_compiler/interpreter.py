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
from .datatypes import *

class Interpreter():
    """Define an interpreter to handle code execution"""
    type_map = dict() # type_map["A0"] = Datatypes.[...]
    variables = dict() # variables["A0"] = [...]
    array_variables = dict() # array_variables["A0"] = [...]

    def clear_variables(self):
        '''Erase information relataing to all variables (including array variables)'''
        self.type_map = dict()
        self.variables = dict()
        self.array_variables = dict()

    def interpret(self, tree:Node):
        '''Entry point for the interpreting loop. Wraps 'interpret_block' and handles program meta-data'''
        root_node = tree
        print("Begin interpreter")
        assert root_node.token.type == TOKEN_TYPE.PROG
        program_name:str = tree.children[0].children[0].token.value
        print(f'{program_name=}')
        self.interpret_block(root_node)

    def assign_datatype(self, var:str, dtype:Datatypes):
        '''
        @Params
            var:str             The variable name to assign to the
            dtype:Datatypes     The datatype the variable will be assigned to
        '''
        assert isinstance(var, str) and isinstance(dtype, Datatypes), f"{var.type=}, {dtype.type=}"
        self.type_map[var.upper()] = dtype
    
    def evaluate_expression(self, expression_root_node:Node) -> typing.Union[Integer32, Integer64, Float32, Float64]:
        '''
        @Param
            expression_root_node:Node       The node that lies at the root of the expression to be evaluated
        @Returns
            value:int | float               The value that the expression evaluates to
        '''
        # base case
        rtt = expression_root_node.token.type # root node token type
        if rtt == TOKEN_TYPE.EXPR:
            return self.evaluate_expression(expression_root_node.children[0])
        elif rtt in NUMERALS: 
            if rtt == TOKEN_TYPE.INT_LIT:
                return Integer32(int(expression_root_node.token.value))
            elif rtt == TOKEN_TYPE.FLOAT_LIT:
                return Float32(float(expression_root_node.token.value))
                
            else:
                raise InterpreterError(f"Numeral literal type not found: {rtt}")
        elif rtt in NUMERICAL_OPERATORS:
            if rtt == TOKEN_TYPE.PLUS:
                return self.evaluate_expression(expression_root_node.children[0]) + self.evaluate_expression(expression_root_node.children[1])
            elif rtt == TOKEN_TYPE.MINUS:
                return self.evaluate_expression(expression_root_node.children[0]) - self.evaluate_expression(expression_root_node.children[1])
            elif rtt == TOKEN_TYPE.MUL:
                return self.evaluate_expression(expression_root_node.children[0]) * self.evaluate_expression(expression_root_node.children[1])
            elif rtt == TOKEN_TYPE.DIV:
                return self.evaluate_expression(expression_root_node.children[0]) / self.evaluate_expression(expression_root_node.children[1])
        else:
            raise InterpreterError(f"Could not evaluate expression node {expression_root_node}")

    def interpret_block(self, root_node:Node):
        for node in root_node.children:
            assert isinstance(node, Node)
            token = node.token
            children = node.children
            if token.type == TOKEN_TYPE.IMPLICIT:
                dtype = match_token_to_datatype(children[0].token)
                var = children[1].token.value
                self.assign_datatype(var, dtype)
                print(self.type_map)
            elif token.type == TOKEN_TYPE.ASSIGN:
                self.variables = children[0].token.value

