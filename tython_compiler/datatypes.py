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
        return repr(self.__class__.__name__) + ':' + repr(self.data)

class Integer(DType):
    '''Base class handling operations on Integers'''
    def __init__(self, data, /, readonly:bool=False):
        if isinstance(data, self._type):
            self._data = data
        else:
            self._data = self._type(data)
        self.readonly = readonly

    @property
    def data(self):
        return self._data
    @data.setter
    def set_data(self, value):
        if self.readonly:
            raise InterpreterError('data is read-only')
        if not isinstance(value, self._type):
            raise InterpreterError(f"Data input to {self._meta_dtype} must be of type <ctypes.c_int32>, got %s" % type(value))
        self._data = value
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
        return self.__class__(self._add_function(self.data, other.data))
    def subtract(self, other:'Integer'):
        return self.__class__(self._sub_function(self.data, other.data))
    def multiply(self, other:'Integer'):
        return self.__class__(self._multiply_function(self.data, other.data))
    def devide(self, other:'Integer'):
        return self.__class__(self._divide_function(self.data, other.data))
    def negate(self):
        return self.__class__(self._negate_function(self.data))

    def __add__(self, other:'Integer'):
        return self.add(other)
    def __sub__(self, other:'Integer'):
        return self.subtract(other)
    def __mul__(self, other:'Integer'):
        return self.multiply(other)
    def __truediv__(self, other:'Integer'):
        return self.devide(other)
    def __neg__(self):
        return self.negate()

    @classmethod
    def static_add(cls, i1:'Integer', i2:'Integer'):
        return cls(cls._add_function(i1.data, i2.data))
    @classmethod
    def static_subtract(cls, i1:'Integer', i2:'Integer'):
        return cls(cls._subtract_function(i1.data, i2.data))
    @classmethod
    def static_multiply(cls, i1:'Integer', i2:'Integer'):
        return cls(cls._multiply_function(i1.data, i2.data))
    @classmethod
    def static_divide(cls, i1:'Integer', i2:'Integer'):
        return cls(cls._divide_function(i1.data, i2.data))
    @classmethod
    def static_negate(cls, i:'Integer'):
        return cls(cls._negate_function(i))

class Integer32(Integer):
    _size = 4
    _meta_dtype = Datatypes.INT32
    _type = ctypes.c_int32
    _cdll = ctypes.CDLL(os.path.join(os.path.dirname(__file__), 'c_dlls/integer_operators.so'))
    _add_function = _cdll.i32_add
    _add_function.argtypes = (ctypes.c_int32, ctypes.c_int32)
    _negate_function = _cdll.i32_negate
    _negate_function.argtypes = (ctypes.c_int32, ctypes.c_int32)
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
    _negate_function = _cdll.i64_negate
    _negate_function.argtypes = (ctypes.c_int64, ctypes.c_int64)
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
    def __init__(self, data, /, readonly:bool=False):
        if isinstance(data, self._type):
            self._data = data
        else:
            self._data = self._type(data)
        self.readonly = readonly

    @property
    def data(self):
        return self._data
    @data.setter
    def set_data(self, value):
        if self.readonly:
            raise InterpreterError('data is read-only')
        if not isinstance(value, self._type):
            raise InterpreterError(f"Data input to {self._meta_dtype} must be of type <ctypes.c_int32>, got %s" % type(value))
        self._data = value
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

    def add(self, other:'Float'):
        return self.__class__(self._add_function(self.data, other.data))
    def subtract(self, other:'Float'):
        return self.__class__(self._sub_function(self.data, other.data))
    def multiply(self, other:'Float'):
        return self.__class__(self._multiply_function(self.data, other.data))
    def devide(self, other:'Float'):
        return self.__class__(self._devide_function(self.data, other.data))
    def negate(self):
        return self.__class__(self._negate_function(self.data))

    def __add__(self, other:'Float'):
        return self.add(other)
    def __sub__(self, other:'Float'):
        return self.subtract(other)
    def __mul__(self, other:'Float'):
        return self.multiply(other)
    def __div__(self, other:'Float'):
        return self.devide(other)
    def __neg__(self):
        return self.negate()

    @classmethod
    def static_add(cls, f1:'Float', f2:'Float'):
        return cls(cls._add_function(f1.data, f2.data))
    @classmethod
    def static_subtract(cls, f1:'Float', f2:'Float'):
        return cls(cls._subtract_function(f1.data, f2.data))
    @classmethod
    def static_multiply(cls, f1:'Float', f2:'Float'):
        return cls(cls._multiply_function(f1.data, f2.data))
    @classmethod
    def static_divide(cls, f1:'Float', f2:'Float'):
        return cls(cls._divide_function(f1.data, f2.data))
    @classmethod
    def static_negate(cls, i:'Float'):
        return cls(cls._negate_function(i))

class Float32(Float):
    _size = 4
    _meta_dtype = Datatypes.REAL32
    _type = ctypes.c_float
    _cdll = ctypes.CDLL(os.path.join(os.path.dirname(__file__), 'c_dlls/float_operators.so'))
    _add_function = _cdll.f32_add
    _add_function.argtypes = (ctypes.c_float, ctypes.c_float)
    _negate_function = _cdll.f32_negate
    _negate_function.argtypes = (ctypes.c_float, ctypes.c_float)
    _subtract_function = _cdll.f32_subtract
    _subtract_function.argtypes = (ctypes.c_float, ctypes.c_float)
    _multiply_function = _cdll.f32_multiply
    _multiply_function.argtypes = (ctypes.c_float, ctypes.c_float)
    _divide_function = _cdll.f32_divide
    _divide_function.argtypes = (ctypes.c_float, ctypes.c_float)

    def __init__(self, data, /, readonly=False):
        super().__init__(data, readonly)
    

class Float64(Float):
    _size = 8
    _meta_dtype = Datatypes.REAL64
    _type = ctypes.c_double
    _cdll = ctypes.CDLL(os.path.join(os.path.dirname(__file__), 'c_dlls/float_operators.so'))
    _add_function = _cdll.f64_add
    _add_function.argtypes = (ctypes.c_double, ctypes.c_double)
    _negate_function = _cdll.f64_negate
    _negate_function.argtypes = (ctypes.c_double, ctypes.c_double)
    _subtract_function = _cdll.f64_subtract
    _subtract_function.argtypes = (ctypes.c_double, ctypes.c_double)
    _multiply_function = _cdll.f64_multiply
    _multiply_function.argtypes = (ctypes.c_double, ctypes.c_double)
    _divide_function = _cdll.f64_divide
    _divide_function.argtypes = (ctypes.c_float, ctypes.c_float)

    def __init__(self, data, /, readonly=False):
        super().__init__(data, readonly)

class Char8(DType):
    _size = 1
    _meta_dtype = Datatypes.CHAR8
    _type = int
    def __init__(self, data, /, readonly:bool=False):
        if isinstance(data, self._type):
            self._data = data
        else:
            self._data = self._type(data)
        self.readonly = readonly

    @property
    def data(self):
        return self._data
    @data.setter
    def set_data(self, value):
        if self.readonly:
            raise InterpreterError('data is read-only')
        if not isinstance(value, self._type):
            raise InterpreterError(f"Data input to {self._meta_dtype} must be of type <ctypes.c_int32>, got %s" % type(value))
        self._data = value
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