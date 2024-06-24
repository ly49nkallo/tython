'''Helper functions to help visualize and debug'''
from .token_types import *
from .token import Token
from .node import Node

def print_plain_string(tokens:list) -> str:
    '''Take in a list of tokens and print them as a nice, human-readable string'''
    ret = ''
    omit_space_flag:bool = False
    for token in tokens:
        tt = token.type
        if tt == TOKEN_TYPE.INT_LIT: ret += f"{token.value}"
        elif tt == TOKEN_TYPE.STR_LIT: ret += f"{token.value}"
        elif tt == TOKEN_TYPE.CHAR_LIT: ret += f"{token.value}"
        # Mathematical Symbols
        elif tt == TOKEN_TYPE.L_PAREN: ret += "("
        elif tt == TOKEN_TYPE.R_PAREN: ret += ")"
        elif tt == TOKEN_TYPE.PLUS: ret += "+"
        elif tt == TOKEN_TYPE.MINUS: ret += "-"
        elif tt == TOKEN_TYPE.MUL: ret += "*"
        elif tt == TOKEN_TYPE.DIV: ret += "/"   
        # Boolean Operators
        elif tt == TOKEN_TYPE.EQUAL_TO: ret += "=="
        elif tt == TOKEN_TYPE.NOT_EQUAL_TO: ret += "!="
        elif tt == TOKEN_TYPE.LE_THAN: ret += "<="
        elif tt == TOKEN_TYPE.LESS_THAN: ret += "<"
        elif tt == TOKEN_TYPE.GE_THAN: ret += ">="
        elif tt == TOKEN_TYPE.GREATER_THAN: ret += ">"
        # Logical Operators
        elif tt == TOKEN_TYPE.LOGICAL_AND: ret += "AND"
        elif tt == TOKEN_TYPE.LOGICAL_OR: ret += "OR"
        elif tt == TOKEN_TYPE.LOGICAL_NOT: ret += "NOT"
        elif tt == TOKEN_TYPE.LOGICAL_NAND: ret += "NAND"
        elif tt == TOKEN_TYPE.LOGICAL_XOR: ret += "XOR"
        elif tt == TOKEN_TYPE.LOGICAL_NOR: ret += "NOR"
        # Mathematical Functions
        elif tt in MATH_FUNCTIONS:
            ret += tt.value
        elif tt == TOKEN_TYPE.ASSIGN: ret += "->"
        # Variables
        elif tt == TOKEN_TYPE.VAR: ret += f"{token.value}"
        elif tt == TOKEN_TYPE.ARRAY_VAR: ret += f"{token.value}"
        # Commands
        elif tt in {TOKEN_TYPE.IMPLICIT, TOKEN_TYPE.PROGRAM, 
                    TOKEN_TYPE.IF, TOKEN_TYPE.ELSE, TOKEN_TYPE.THEN, 
                    TOKEN_TYPE.END, TOKEN_TYPE.DISP, TOKEN_TYPE.CALL}:
            ret += tt.value
        # Datatype Declarators
        elif tt in DATA_TYPES:
            ret += tt.value
        # Structure Tokens
        elif tt == TOKEN_TYPE.LINE_BREAK: ret += '\n'
        elif tt == TOKEN_TYPE.EOF: pass
        else:
            raise NameError(f"Could not find representation of the token <{token}>")
        ret += ' '
    print(ret)
    return ret
