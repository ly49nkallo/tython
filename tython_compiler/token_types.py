'''Enum containing a list of the Token Types'''
'''Author: Ty Brennan'''

import enum

@enum.unique
class TOKEN_TYPE(enum.Enum):
        # DATA TYPES
        INT32 = 'INT32'
        INT64 = 'INT64'
        REAL32 = 'REAL32'
        REAL64 = 'REAL64'
        CHAR8 = 'CHAR8'
        # MATHEMATICAL OPERATORS
        ASSIGN = '\-\>'
        PLUS = '\+'
        MINUS = '\-'
        MUL = '\*'
        DIV = '\/'
        L_PAREN = '\('
        R_PAREN = '\)'
        # CONDITIONALS
        IF = 'IF'
        THEN = 'THEN'
        ELSE = 'ELSE'
        END = 'END'
        # FLOW CONTROL
        LABEL = 'LBL'
        GOTO = 'GOTO'
        # BOOLEAN OPERATORS
        GREATER_THAN = '\>'
        LESS_THAN = '\<'
        GE_THAN = '>='
        LE_THAN = '<='
        EQUAL_TO = '=='
        NOT_EQUAL_TO = '\!='
        # LOGICAL OPERATORS
        LOGICAL_AND = 'AND'
        LOGICAL_OR = 'OR'
        LOGICAL_NOT = 'NOT'
        LOGICAL_NAND = 'NAND'
        LOGICAL_XOR = 'XOR'
        LOGICAL_NOR = 'NOR'
        # PROGRAM CONTROL
        PROGRAM = 'PROGRAM'
        VERSION = 'VERSION'
        IMPLICIT = 'IMPLICIT'
        CALL = 'CALL'
        # VARIABLE LITERALS
        CHAR_LIT = '\'.\''
        STR_LIT = '\\".*\\"'
        INT_LIT = '\\d+'
        FLOAT_LIT = '\\d+\.\\d*'
        HEX_LIT = '0x[A-F0-9]+'
        BIN_LIT = '0b[01]+'
        # VARIABLES
        VAR = '[A-Z]\\d?'
        ARRAY_VAR = '@[A-Z]\\d?'
        # COMMANDS
        DISP = 'DISP'
        DISP_STR = 'DISPSTR'
        # TRIG FUNCTIONS
        SIN = 'SIN'
        COS = 'COS'
        TAN = 'TAN'
        COT = 'COT'
        SEC = 'SEC'
        CSC = 'CSC'
        # INVERSE TRIG FUNCTIONS
        ARCSIN = 'ARCSIN'
        ARCCOS = 'ARCCOS'
        ARCTAN = 'ARCTAN'
        ARCCOT = 'ARCCOT'
        ARCSEC = 'ARCSEC'
        ARCCSC = 'ARCCSC'
        # ARRAY FUNCTIONS
        DIM = 'DIM'
        # STRUCTURE TOKENS
        COMMA = '\,'
        LINE_BREAK = 1
        EOF = 2
        EXPR = 3
        PROG = 4
        BOOL_EXPR = 5
        LOGIC_EXPR = 6
        BLOCK = 7
        
        # STMT = 6

"""====> CATEGORIES <===="""

REQUIRES_VALUE:set = {
    TOKEN_TYPE.CHAR_LIT,
    TOKEN_TYPE.STR_LIT,
    TOKEN_TYPE.INT_LIT,
    TOKEN_TYPE.FLOAT_LIT,
    TOKEN_TYPE.HEX_LIT,
    TOKEN_TYPE.BIN_LIT,
    TOKEN_TYPE.VAR,
    TOKEN_TYPE.ARRAY_VAR,
}
NUMERALS:set = {
    TOKEN_TYPE.INT_LIT,
    TOKEN_TYPE.FLOAT_LIT
}
NUMERICAL_OPERATORS:set = {
    TOKEN_TYPE.PLUS,
    TOKEN_TYPE.MINUS,
    TOKEN_TYPE.MUL,
    TOKEN_TYPE.DIV,
}
BOOLEAN_OPERATORS:set = {
    TOKEN_TYPE.EQUAL_TO,
    TOKEN_TYPE.NOT_EQUAL_TO,
    TOKEN_TYPE.LE_THAN,
    TOKEN_TYPE.LESS_THAN,
    TOKEN_TYPE.GE_THAN,
    TOKEN_TYPE.GREATER_THAN,
}
LOGICAL_OPERATORS:set = {
    TOKEN_TYPE.LOGICAL_AND,
    TOKEN_TYPE.LOGICAL_OR,
    TOKEN_TYPE.LOGICAL_NOT,
    TOKEN_TYPE.LOGICAL_NAND,
    TOKEN_TYPE.LOGICAL_XOR,
    TOKEN_TYPE.LOGICAL_NOR
}
ORDER_OF_OPERATIONS:list = [
    (TOKEN_TYPE.MUL, TOKEN_TYPE.DIV),
    (TOKEN_TYPE.PLUS, TOKEN_TYPE.MINUS),
]
DATA_TYPES:set = {
    TOKEN_TYPE.INT32,
    TOKEN_TYPE.INT64,
    TOKEN_TYPE.REAL32,
    TOKEN_TYPE.REAL64,
    TOKEN_TYPE.CHAR8
}
MATH_FUNCTIONS:set = {
    TOKEN_TYPE.SIN,
    TOKEN_TYPE.COS,
    TOKEN_TYPE.TAN,
    TOKEN_TYPE.COT,
    TOKEN_TYPE.SEC,
    TOKEN_TYPE.CSC,
    TOKEN_TYPE.ARCSIN,
    TOKEN_TYPE.ARCCOS,
    TOKEN_TYPE.ARCTAN,
    TOKEN_TYPE.ARCCOT,
    TOKEN_TYPE.ARCSEC,
    TOKEN_TYPE.ARCCSC,
}
def is_expr_type(type): 
    return type in NUMERALS \
        or type in MATH_FUNCTIONS \
        or type == TOKEN_TYPE.L_PAREN \
        or type == TOKEN_TYPE.R_PAREN \
        or type in NUMERICAL_OPERATORS \
        or type == TOKEN_TYPE.VAR