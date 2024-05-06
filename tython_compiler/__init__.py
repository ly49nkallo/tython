from .token_types import TOKEN_TYPE, ORDER_OF_OPERATIONS, REQUIRES_VALUE, NUMERALS
from .parser import *
import token
from .interpreter import Interpreter
from .shunting_yard_algorithm import *
from .utils import *
# import node # BUG

def init(debug=False, tab_width=3):
    '''Set debug flag in nessesary modules to \'True\''''
    if debug:
        parser.DEBUG = True
        token.DEBUG = True
        interpreter.DEBUG = True
    #n.TAB_WIDTH = tab_width

