import tython_compiler as tc
import time

IOTA = 1
class TestCaseError(Exception):
    '''Yet another error!'''
    ...

def test_case(func):
    '''Define some simple helpers for test_cases'''
    def wrapper(*args, **kwargs):
        global IOTA
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
    program = '''
    PROGRAM "test 1"
    if 1 == 1
    Disp "Hi"
    '''
    tokens = tc.Parser.lexical_analysis(program)
    tree = tc.Parser.syntax_analysis(tokens)
    print(tree)

    pass

@test_case
def test_case_2():
    program = '''
    PROGRAM "test 2"
    Implicit real32 x
    x -> (1 + 2) + 3 * 4
    y -> (4)
    if (5 + 6) > 7
    disp "Wat :|"
    if ((8 + 9 > 10) or (11 + 12 > 13)) or (14 == 15) then
    disp "Ok then..."
    disp "2"
    disp "3"
    end
    #EOF
    '''
    tokens = tc.Parser.lexical_analysis(program)
    tree = tc.Parser.syntax_analysis(tokens)
    print(tree)

@test_case
def test_case_3():
    '''Test Functions'''
    program = '''
    PROGRAM "test 3"
    x -> sin(1)
    #EOF
    '''
    tokens = tc.Parser.lexical_analysis(program)
    tree = tc.Parser.syntax_analysis(tokens)
    print(tree)


    pass


if __name__ == '__main__':
    tc.init(debug=True, tab_width=1)
    start_time = time.time()
    #test_case_1() 
    test_case_2()
    test_case_3()
    print(f"All test cases passed in {(time.time() - start_time):0.4f} seconds")