'''Helper functions to help visualize and debug'''
from .token_types import *
from .token import Token
from .node import Node

def print_plain_string(tokens:list) -> str:
    '''Take in a list of tokens and print them as a nice, human-readable string'''
    ret = ''
    for token in tokens:
        tt = token.type
        if tt == TOKEN_TYPE.INT_LIT: ret += f"{token.value}"
        elif tt == TOKEN_TYPE.STR_LIT: ret += f"{token.value}"
        elif tt == TOKEN_TYPE.CHAR_LIT: ret += f"{token.value}"
        elif tt == TOKEN_TYPE.L_PAREN: ret += "("
        elif tt == TOKEN_TYPE.R_PAREN: ret += ")"
        elif tt == TOKEN_TYPE.PLUS: ret += "+"
        elif tt == TOKEN_TYPE.MINUS: ret += "-"
        elif tt == TOKEN_TYPE.MUL: ret += "*"
        elif tt == TOKEN_TYPE.DIV: ret += "/"
        elif tt in MATH_FUNCTIONS:
            ret += tt
        elif tt == TOKEN_TYPE.ASSIGN: ret += "->"
        elif tt == TOKEN_TYPE.VAR: ret += f"{token.value}"
        elif tt == TOKEN_TYPE.ARRAY_VAR: ret += f"{token.value}"
        elif tt == TOKEN_TYPE.PROGRAM: ret += "PROGRAM"
        else:
            raise NameError(f"Could not find representation of the token <{token}>")
        ret += ' '
    print(ret)
    return ret
