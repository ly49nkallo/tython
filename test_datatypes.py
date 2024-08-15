import tython_compiler as tc
from tython_compiler.interpreter import *
interpreter = Interpreter()
i1 = Integer32(0)
i2 = Integer32(0)
print(i1 + i2)
i1 = Integer32(2_147_483_647)
print(i1 + i2)
i3 = Integer64(1)
i4 = Integer64(1)
print(i3 + i4)
program = '''
            program "a"
            (1 + 1) / 2 * 7 / 2 -> i
            Disp i
        '''
tokens = tc.Parser.lexical_analysis(program)
print(tokens)
print(tree := tc.Parser.syntax_analysis(tokens))
interpreter.interpret(tree)
