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
    def size(self) -> int:
        ...
    @property
    @abc.abstractmethod
    def data(self):
        ...
    @property
    @abc.abstractmethod
    def meta_dtype(self):
        ...
    @property
    @abc.abstractmethod
    def type(self):
        ...
    def __repr__(self):
        return repr(self.data)

class Integer(DType):
    '''Base class handling operations on Integers'''
    def __init__(self, data, /, readonly:bool=False):
        if isinstance(data, self._type):
            self._data = data
        else:
            self._data = self._type(data)
        self.readonly = readonly
        print(type(self.data))

    @property
    def data(self) -> ctypes.c_int32:
        return self._data
    @data.setter
    def set_data(self, value):
        if not isinstance(value, self._type):
            raise InterpreterError(f"Data input to {self._meta_dtype} must be of type <ctypes.c_int32>, got %s" % type(value))
        self._data = value
        print(type(self.data))
    @data.getter
    def get_data(self):
        return self._data
    @property
    def size(self):
        return self._size
    @property
    def meta_dtype(self):
        return self._meta_dtype
    @property
    def type(self):
        return self._type

    def add(self, other:'Integer'):
        return self._add_function(self.data, other.data)
    def subtract(self, other:'Integer'):
        return self._sub_function(self.data, other.data)
    def multiply(self, other:'Integer'):
        return self._multiply_function(self.data, other.data)
    def devide(self, other:'Integer'):
        return self._devide_function(self.data, other.data)
    def __add__(self, other:'Integer'):
        return self.add(other)
    def __sub__(self, other:'Integer'):
        return self.subtract(other)
    def __mul__(self, other:'Integer'):
        return self.multiply(other)
    def __div__(self, other:'Integer'):
        return self.devide(other)

    @classmethod
    def static_add(cls, i1:'Integer', i2:'Integer'):
        return cls._add_function(i1.data, i2.data)
    @classmethod
    def static_subtract(cls, i1:'Integer', i2:'Integer'):
        return cls._subtract_function(i1.data, i2.data)
    @classmethod
    def static_multiply(cls, i1:'Integer', i2:'Integer'):
        return cls._multiply_function(i1.data, i2.data)
    @classmethod
    def static_divide(cls, i1:'Integer', i2:'Integer'):
        return cls._divide_function(i1.data, i2.data)

class Integer32(Integer):
    _size = 4
    _meta_dtype = Datatypes.INT32
    _type = ctypes.c_int32
    _cdll = ctypes.CDLL(os.path.join(os.path.dirname(__file__), 'c_dlls/integer_operators.so'))
    _add_function = _cdll.i32_add
    _add_function.argtypes = (ctypes.c_int32, ctypes.c_int32)
    _subtract_function = _cdll.i32_subtract
    _subtract_function.argtypes = (ctypes.c_int32, ctypes.c_int32)
    _multiply_function = _cdll.i32_multiply
    _multiply_function.argtypes = (ctypes.c_int32, ctypes.c_int32)
    _divide_function = _cdll.i32_divide
    _divide_function.argtypes = (ctypes.c_int32, ctypes.c_int32)

    def __init__(self, data, /, readonly=False):
        super().__init__(data, readonly)


class Integer64(Integer):
    _size = 8
    _meta_dtype = Datatypes.INT64
    _type = ctypes.c_int64
    _cdll = ctypes.CDLL(os.path.join(os.path.dirname(__file__), 'c_dlls/integer_operators.so'))
    _add_function = _cdll.i64_add
    _add_function.argtypes = (ctypes.c_int64, ctypes.c_int64)
    _subtract_function = _cdll.i64_subtract
    _subtract_function.argtypes = (ctypes.c_int64, ctypes.c_int64)
    _multiply_function = _cdll.i64_multiply
    _multiply_function.argtypes = (ctypes.c_int64, ctypes.c_int64)
    _divide_function = _cdll.i64_divide
    _divide_function.argtypes = (ctypes.c_int64, ctypes.c_int64)

    def __init__(self, data, /, readonly=False):
        super().__init__(data, readonly)

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

