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

@enum.unique
class Datatypes(enum.Enum):
    INT32 = enum.auto()
    INT64 = enum.auto()
    REAL32 = enum.auto()
    REAL64 = enum.auto()
    CHAR8 = enum.auto()

def match_token_to_datatype(token) -> Datatypes:
    '''
    @Params
        token:Token
            A token to match
    @Returns
        Datatypes
            The corresponding Datatyles enum of the token type
    '''
    assert isinstance(token, Token)
    t = token.type
    if t == TOKEN_TYPE.INT32:
        return Datatypes.INT32
    elif t == TOKEN_TYPE.INT64:
        return Datatypes.INT64
    elif t == TOKEN_TYPE.REAL32:
        return Datatypes.REAL32
    elif t == TOKEN_TYPE.REAL64:
        return Datatypes.REAL64
    elif t == TOKEN_TYPE.CHAR8:
        return Datatypes.CHAR8
    else:
        raise ValueError("Token is not matched to interpreter datatype")
    
def get_default_type(var:str) -> Datatypes:
    assert isinstance(var, str)
    letter = var[0].upper()
    assert letter.isalpha()
    if letter in 'IJKLMN':
        return Datatypes.INT32
    else:
        return Datatypes.REAL32

class DType(abc.ABC):
    '''Abstract Data Type Base-Class'''
    @property
    @abc.abstractmethod
    def _size() -> int:
        ...
    @property
    @abc.abstractmethod
    def _data():
        ...
    @property
    @abc.abstractmethod
    def _meta_dtype():
        ...

class Integer(DType):
    '''Base class handling operations on Integers'''
    @property
    @abc.abstractmethod
    def _add_function():
        ...
    @property
    @abc.abstractmethod
    def _subtract_function():
        ...
    @property
    @abc.abstractmethod
    def _negate_function():
        ...
    @property
    @abc.abstractmethod
    def _multiply_function():
        ...
    @property
    @abc.abstractmethod
    def _devide_function():
        ...
    @abc.abstractmethod
    def add(self, other:'Integer'):
        ...
    @abc.abstractmethod
    def subtract(self, other:'Integer'):
        ...
    @abc.abstractmethod
    def negate(self):
        ...
    @abc.abstractmethod
    def multiply(self, other:'Integer'):
        ...
    @abc.abstractmethod
    def devide(self, other:'Integer'):
        ...

class Integer32(Integer):
    _size = 4
    _meta_dtype = Datatypes.INT32
    _cdll = ctypes.CDLL(os.path.join(os.path.dirname(__file__), 'c_dlls/integer_operators.so'))
    _add_function = _cdll.i32_add
    _add_function.argtypes = (ctypes.c_int32, ctypes.c_int32)

    def __init__(self, data:int, /, readonly:bool=False):
        self.data = ctypes.c_int32(data)
    @property
    def data(self) -> ctypes.c_int32:
        return self._data
    @property.setter
    def data(self, value):
        if not isinstance(value, ctypes.c_int32):
            raise InterpreterError
        self._data = value
    @staticmethod
    def static_add(i1:'Integer32', i2:'Integer32'):
        return Integer32._add_function(ctypes.c_int32(i1), ctypes.c_int32(i2))


class Integer64(Integer):
    _size = 8
    _data = bytearray(_size)
    ...

class Float(DType):
    '''Base class handling operations on Floats'''
    @abc.abstractmethod
    def add(self, other:'Float'):
        ... # Maybe use ctypes to impl IEEE std.
    @abc.abstractmethod
    def subtract(self, other:'Float'):
        ...
    @abc.abstractmethod
    def negate(self):
        ...
    @abc.abstractmethod
    def multiply(self, other:'Float'):
        ...
    @abc.abstractmethod
    def devide(self, other:'Float'):
        ...

class Float32(Float):
    _size = 4
    _data = bytearray(_size)
    

class Float64(Float):
    _size = 8
    _data = bytearray(_size)


class Char8(DType):
    _size = 1
    _data = bytearray(_size)

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

