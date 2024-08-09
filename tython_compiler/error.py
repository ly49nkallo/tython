"Errors used during compilation"


class ParsingError(Exception):
    ...

class LoweringError(Exception):
    ...

class InterpreterError(Exception):
    ...