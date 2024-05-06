from .token_types import TOKEN_TYPE

DEBUG = False

class Token(object):
    '''A lexical unit of code correspinding to a certain, specific function.'''
    def __init__(self, type:TOKEN_TYPE, line_number:int, value=None):
        assert isinstance(type, TOKEN_TYPE)
        self.type:TOKEN_TYPE = type
        self.value = value
        self.line_number:int = line_number

    def __repr__(self) -> str:
        ret = str(self.type)[len("TOKEN_TYPE")+1:]
        if self.value is not None: ret += f":{self.value}"
        if DEBUG: ret += f":line {self.line_number}"
        return ret