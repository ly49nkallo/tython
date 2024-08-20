import tython_compiler as tc
import time

IOTA = 1
class TestCaseError(Exception):
    '''Yet another error!'''
    ...

def test_case(func):
    '''Wrapper defining some simple helpers for test_cases'''
    def wrapper(*args, **kwargs):
        global IOTA
        print("="*20)
        print(f"Start test {IOTA}")
        start_time = time.time()
        func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"Test case {IOTA} passed in {elapsed_time:.4f} seconds")
        IOTA += 1
    return wrapper

'''TESTS'''
@test_case
def test_case_1():
    parser = tc.Parser()
    program = '''
    PROGRAM "test 1"
    if 1 == 1
    Disp "Hello, World!"
    '''
    interpreter = tc.Interpreter()
    tokens = parser.lexical_analysis(program)
    tree = parser.syntax_analysis(tokens)
    print(tree)
    interpreter.interpret(tree)
    pass

@test_case
def test_case_2():
    parser = tc.Parser()
    interpreter = tc.Interpreter()
    program = '''
    PROGRAM "test 2"
    Implicit real32 x
    (1 + 2) + 3 * 4 -> x
    (4) -> y
    if (5 + 6) > 7
    disp "Wat :|"
    if ((8 + 9 > 10) or (11 + 12 <= 13)) or (14 == 15) then
    disp "Ok then..."
    disp "2"
    disp "3"
    end
    #EOF
    '''
    tokens = parser.lexical_analysis(program)
    tree = parser.syntax_analysis(tokens)
    print(tree)

@test_case
def test_case_3():
    parser = tc.Parser()
    '''Test Functions'''
    program = '''
    PROGRAM "test 3"
    call "PROGRAM_THREE"
    implicit real32 x
    sin(x) -> y
    #EOF
    '''
    tokens = parser.lexical_analysis(program)
    tree = parser.syntax_analysis(tokens)
    print(tree)

@test_case
def test_shunting_yard_algorithm():
    input_tokens = []
    for i in range(7):
        if i % 2 == 0:
            input_tokens.append(tc.Token(tc.TOKEN_TYPE.INT_LIT, 0, i))
        elif i % 4 == 1:
            input_tokens.append(tc.Token(tc.TOKEN_TYPE.PLUS, 0))
        elif i % 4 == 3:
            input_tokens.append(tc.Token(tc.TOKEN_TYPE.MUL, 0))
    tc.utils.print_plain_string(input_tokens)
    tc.utils.print_plain_string(tc.shunting_yard_algorithm.shunting_yard(input_tokens))

if __name__ == '__main__':
    tc.init(debug=False, tab_width=1)
    start_time = time.time()
    test_case_1() 
    test_case_2()
    test_case_3()
    # test_shunting_yard_algorithm()
    print(f"All test cases passed in {(time.time() - start_time):0.4f} seconds")
