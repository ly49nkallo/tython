import pathlib
import logging
import argparse
import tython_compiler as tc

VERSION:tuple = (-1, 1, 0)

def main() -> None:
    logger:logging.Logger = logging.getLogger()

    # Argument Parser
    parser = argparse.ArgumentParser(description=f'TYTHON Compiler {VERSION}')
    parser.add_argument('input_file')
    parser.add_argument('-o', '--output')
    parser.add_argument('-c', '--compile', action='store_true', default=False)
    parser.add_argument('-i', '--interpret', action='store_true', default=False)

    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('-v', '--version', action='version',
                        version=f'Tython {VERSION[-1]}.{VERSION[1]}.{VERSION[2]}')
    args = parser.parse_args()
    filepath:pathlib.Path = pathlib.Path(args.input_file)

    # Configure Debug setting
    DEBUG = args.debug
    if DEBUG: print(f'{args.debug=}')
    if DEBUG: tc.set_debug()
    
    # Configure compilation setting
    if args.compile and args.interpret:
        raise SyntaxError("Cannot compile and interpret simultaneously")
    if not (args.compile or args.interpret):
        COMPILE = True
    if args.compile:
        COMPILE = True
    if args.interpret:
        COMPILE = False

    # Retrive file contents
    with open(filepath, 'r') as f:
        file_contents = f.read()

    # Initialize lexer
    tokens = tc.Parser.lexical_analysis(file_contents)
    tree = tc.Parser.syntax_analysis(tokens)

    if COMPILE:
        raise NotImplementedError("Compilation not yet implemented!")
    elif not COMPILE:
        tc.Interpreter.interpret(tree)

if __name__ == '__main__':
    main()
