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
        ASSIGN = '\='
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
        # COMPARISON OPERATORS
        GREATER_THAN = '\>'
        LESS_THAN = '\<'
        GE_THAN = '>='
        LE_THAN = '<='
        EQUAL_TO = '=='
        NOT_EQUAL_TO = '\!='
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
        # ARRAY FUNCTIONS
        DIM = 'DIM'
        # STRUCTURE TOKENS
        COMMA = '\,'
        LINE_BREAK = 1
        EOF = 2
        EXPR = 3
        PROG = 4
        BIN_EXPR = 5
        STMT = 6
