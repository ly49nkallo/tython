import tython_compiler as tc
import time

IOTA = 1

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
    x = (1 + 2) + 3 * 4
    # y = 3 + 4
    # z = 5 * 6 + 7
    '''
    tokens = tc.Parser.lexical_analysis(program)
    tree = tc.Parser.syntax_analysis(tokens)
    print(tree)

if __name__ == '__main__':
    tc.set_debug()
    start_time = time.time()
    test_case_1() 
    print(f"All test cases passed in {(time.time() - start_time):0.4f} seconds")