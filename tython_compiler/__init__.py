from .token_types import TOKEN_TYPE, ORDER_OF_OPERATIONS, REQUIRES_VALUE, NUMERALS
from .parser import *
import token
import interpreter
# import node # BUG

def init(debug=False, tab_width=3):
    '''Set debug flag in nessesary modules to \'True\''''
    if debug:
        parser.DEBUG = True
        token.DEBUG = True
        interpreter.DEBUG = True
    #n.TAB_WIDTH = tab_width

