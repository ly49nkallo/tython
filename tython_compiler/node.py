"Define Node Class"
import os, sys
import functools
import time
import enum
import typing
import re

from pprint import pprint
from .token_types import *
from .token import Token

TAB_WIDTH = 2
MAX_RECURSION_DEPTH = 100

class Node(object):
    def __init__(self, token:Token, children:list=None, name:str=None):
        if children is None: children = [] #AAAARRRRGGGGHHHHHHH!!!!!!!! I HATE THIS F*CKING PYTHON FEATURE (BUG) (singleton referenced default kw args)
        self.name:typing.Optional[str] = name
        self.token:Token = token
        self.children:list = children

    def is_leaf(self) -> bool:
        return (len(self.children) == 0)

    def append_child(self, other:'Node'):
        assert isinstance(other, Node), f"Expected Node, got {type(other)} instead"
        assert isinstance(self.children, list), f"Expected self.children to be a list, got {type(self.children)} instead"
        for c in other.children:
            assert c.token.type != self.token.type
        self.children.append(other)

    def _repr_helper(self, tabs:int):
        if tabs > MAX_RECURSION_DEPTH:
            raise NameError("Infinite Loop / Self-referential Node")
        if self.name is not None: ret = self.name
        else: ret = repr(self.token)
        if len(self.children) != 0: ret += '\n'
        for c in self.children:
            assert isinstance(c, Node), str(type(c))
            ret += ' ' * (TAB_WIDTH*tabs) + c._repr_helper(tabs+1) + '\n'
        if len(self.children) != 0: 
            ret = ret[:-1]
            #ret += ' ' * (4*tabs) # neater this way
        return ret

    def __repr__(self):
        return self._repr_helper(1)