from sly import Parser
from scanner_sly import Scanner



class Mparser(Parser):
    tokens = Scanner.tokens
    debugfile = 'parser.out'

    precedence = (  # tokens are ordered from lowest to highest precedence
        ("left", 'EQ', 'NE', 'LE', 'LT', 'GE', 'GT'),
        ("left", 'ASSIGN', 'ADD', 'SUBTRACT'),
        ("left", 'MULTIPLY_BY', 'DIVIDE_BY'),
        ("left", "+", "-"), # add option for unary negation
        ("left", 'MATRIX_PLUS', 'MATRIX_MINUS'),
        ("left", "*", "/"),
        ("left",  'MATRIX_MUL', 'MATRIX_DIV'),
        ("left", 'TRANSPOSE'),
        ("left", "(", ")", "[", "]"),
        ("left", "{", "}"),
    )

    @_('statements')
    def program(self, p):
        return p[0]

    @_('statement')
    @_('statement statements')
    @_('block')
    def statements(self, p):
        return p[0]

    @_('statement')
    @_('block')
    def instruction(self, p):
        return p[0]

    @_(" '{' statements '}'")
    def block(self, p):
        return p[0]

    @_('assignment ";"')
    @_('if_statement')
    @_('for_loop')
    @_('while_loop')
    @_('print_statement ";"')
    @_('keyword_statement ";"')
    def statement(self, p):
        return p[0]

    @_('ID assign_operator expr')
    @_("ID '=' STRING")
    @_("ID list assign_operator expr")
    def assignment(self, p):
        return p[0]


    @_("IF '(' condition ')' instruction")
    @_("IF '(' condition ')' instruction ELSE instruction")
    @_("IF '(' condition ')' instruction ELSE IF '(' condition ')' instruction ELSE instruction")
    def if_statement(self, p):
        return p[0]

    @_("FOR ID ASSIGN INTEGER RANGE INTEGER instruction")
    @_("FOR ID ASSIGN INTEGER RANGE ID instruction")
    @_("FOR ID ASSIGN ID RANGE ID instruction")
    def for_loop(self, p):
        return p[0]

    @_("WHILE '(' condition ')' instruction")
    def while_loop(self, p):
        return p[0]

    @_("PRINT terms")
    @_("PRINT STRING")
    def print_statement(self, p):
        return p[0]

    @_("BREAK")
    @_("CONTINUE")
    @_("RETURN expr")
    def keyword_statement(self, p):
        return p[0]

    @_('expr relational_operator expr')
    @_("'(' condition ')'")
    def condition(self, p):
        return p[0]

    @_('term')
    @_("expr '+' expr")
    @_("expr '-' expr")
    @_("expr '*' expr")
    @_("expr '/' expr")
    @_(" '-' expr")
    @_('expr matrix_operator expr')
    @_("'(' expr ')'")
    def expr(self, p):
        return p[0]

    @_("EYE '(' INTEGER ')'")
    @_("ZEROS '(' INTEGER ')'")
    @_("ONES '(' INTEGER ')' ")
    @_('list')
    @_('MATRIX TRANSPOSE')
    def MATRIX(self, p):
        return p[0]

    @_(" '[' terms ']' ")
    def list(self, p):
        return p[0]

    @_("term")
    @_("terms ',' term")
    def terms(self, p):
        return p[0]

    @_('ID')
    @_('numeric')
    @_('list')
    @_('ID list')
    @_('MATRIX')
    @_("ID TRANSPOSE")
    def term(self, p):
        return p[0]

    @_('INTEGER')
    @_('FLOAT')
    def numeric(self, p):
        return p[0]

    @_('ADD')
    @_('SUBTRACT')
    @_('MULTIPLY_BY')
    @_('DIVIDE_BY')
    @_('ASSIGN')
    def assign_operator(self, p):
        return p[0]

    @_('EQ')
    @_('LE')
    @_('LT')
    @_('GE')
    @_('GT')
    @_('NE')
    def relational_operator(self, p):
        return p[0]

    @_('MATRIX_PLUS')
    @_('MATRIX_MINUS')
    @_('MATRIX_MUL')
    @_('MATRIX_DIV')
    def matrix_operator(self, p):
        return p[0]

