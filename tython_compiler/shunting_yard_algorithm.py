# https://www.youtube.com/watch?v=unh6aK8WMwM
# This came out 2 days ago and conveniently provides a solution to a problem I had to overcome a month ago

from .token_types import *
from .token import Token

def shunting_yard(input_tokens:list) -> list:
    holding_stack = []
    output = []
    solve_stack = []
    for token in input_tokens:
        if token.type in NUMERALS:
            output.append(token)
        elif token.type in NUMERICAL_OPERATORS:
            ordinal = get_ordinal(token)
            while True:
                if len(holding_stack) > 0 and ordinal < get_ordinal(holding_stack[-1]):
                    output.append(holding_stack.pop())
                else: break
            holding_stack.append(token)
    if len(holding_stack) != 0:
        for token in holding_stack:
            output.append(token)
    return output

def get_ordinal(token:Token):
    assert token.type in NUMERICAL_OPERATORS
    ret = 1
    for level in reversed(ORDER_OF_OPERATIONS):
        if token.type in level:
            return ret
        ret += 1
