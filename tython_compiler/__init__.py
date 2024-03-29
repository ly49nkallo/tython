from .token_types import TOKEN_TYPE, ORDER_OF_OPERATIONS, REQUIRES_VALUE, NUMERALS
from .parser import *
import token

def set_debug():
    '''Set debug flag in nessesary modules to \'True\''''
    parser.DEBUG = True
    token.DEBUG = True

