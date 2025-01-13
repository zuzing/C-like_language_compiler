import sys
from sly import Lexer


class Scanner(Lexer):
    def __init__(self):
        self.lineno = 0

    MATRIX_OPERATORS = ['MATRIX_PLUS', 'MATRIX_MINUS', 'MATRIX_MUL', 'MATRIX_DIV']
    ASSIGNMENT_OPERATORS = ['ADD', 'SUBTRACT', 'MULTIPLY_BY', 'DIVIDE_BY', 'ASSIGN']
    RELATIONAL_OPERATORS = ['EQ','LE', 'LT', 'GE', 'GT', 'NE']
    KEYWORDS = ['IF', 'ELSE', 'FOR', 'WHILE', 'PRINT', 'BREAK', 'CONTINUE', 'RETURN', 'EYE', 'ZEROS', 'ONES']


    tokens = {*MATRIX_OPERATORS, *ASSIGNMENT_OPERATORS, *RELATIONAL_OPERATORS, 'RANGE', 'TRANSPOSE', 'ID', *KEYWORDS,
          'INTEGER', 'FLOAT', 'STRING'}
    literals = {'+', '-', '*', '/', '(', ')', '[', ']', '{', '}', ',', ';'}

    MATRIX_PLUS = r'\.\+'
    MATRIX_MINUS = r'\.\-'
    MATRIX_MUL = r'\.\*'
    MATRIX_DIV = r'\.\/'

    EQ = r'=='
    LE = r'<='
    LT = r'<'
    GE = r'>='
    GT = r'>'
    NE = r'!='

    ADD = r'\+='
    SUBTRACT = r'\-='
    MULTIPLY_BY = r'\*='
    DIVIDE_BY = r'\/='
    ASSIGN = r'\='

    FLOAT = r'(\.[0-9]+|[0-9]+\.[0-9]*)([eE][+-]?[0-9]+)?' # optional sign, integer, and fraction; if the integer part is omitted, the fraction is mandatory; exponent is optional
    INTEGER = r'[0-9]+'
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['if'] = 'IF'
    ID['else'] = 'ELSE'
    ID['for'] = 'FOR'
    ID['while'] = 'WHILE'
    ID['print'] = 'PRINT'
    ID['break'] = 'BREAK'
    ID['continue'] = 'CONTINUE'
    ID['return'] = 'RETURN'
    ID['eye'] = 'EYE'
    ID['zeros'] = 'ZEROS'
    ID['ones'] = 'ONES'

    STRING = r'\".*?\"|\'.*?\''

    RANGE = r'\:'
    TRANSPOSE = r"\'"

    ignore_whitespace = r' '
    ignore_comment = r'\#.*'
    ignore_newline = r'\n+'
    ignore_tab = r'\t+'

    def ignore_newline(self, t):
        self.lineno += len(t.value)


if __name__ == '__main__':

    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "./scanner_example/example.txt"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    text = file.read()
    lexer = Scanner()


    for tok in lexer.tokenize(text):
        print(tok)

