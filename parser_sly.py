from sly import Parser
from scanner_sly import Scanner
import AST


class Mparser(Parser):
    tokens = Scanner.tokens
    debugfile = 'parser.out'

    precedence = (  # tokens are ordered from lowest to highest precedence
        ("left", 'ASSIGN'),
        ("left", 'LT', 'GT'),
        ("left", 'EQ', 'NE', 'GE', 'LE'),
        ("left", "+", "-"),
        ("left", 'MATRIX_PLUS', 'MATRIX_MINUS'),
        ("left", 'ADD', 'SUBTRACT'),
        ("left", "*", "/"),
        ("left",  'MATRIX_MUL', 'MATRIX_DIV'),
        ("left", 'MULTIPLY_BY', 'DIVIDE_BY'),
        ("left", 'UMINUS'),
    )

    @_('statements')
    def program(self, p):
        return p[0]

    @_('statement')
    @_('statement statements')
    @_('block')
    def statements(self, p):
        return p[0]

    @_('for_loop')
    @_('while_loop')
    @_('assignment ";"')
    @_('print_statement ";"')
    @_('keyword_statement ";"')
    @_('block')
    def instruction(self, p):
        return p[0]

    @_(" '{' statements '}'")
    def block(self, p):
        return p[0]

    @_('if_statement')
    @_('for_loop')
    @_('while_loop')
    @_('assignment ";"')
    @_('print_statement ";"')
    @_('keyword_statement ";"')
    def statement(self, p):
        return p[0]

    @_("IF '(' condition ')' instruction else_part")
    @_("IF '(' condition ')' instruction empty")
    @_("IF '(' condition ')' if_statement")  # nested if without {}, can't have else_part
    def if_statement(self, p):
        return p[0]

    @_("ELSE instruction")
    @_("ELSE if_statement")
    def else_part(self, p):
        return p[0]

    @_("")
    def empty(self, p):
        return None

    # @_('ID assign_operator expr')
    # @_("ID list assign_operator expr")
    @_('ID ADD expr')
    @_('ID SUBTRACT expr')
    @_('ID MULTIPLY_BY expr')
    @_('ID DIVIDE_BY expr')
    @_('ID ASSIGN expr')
    @_('ID list ADD expr')
    @_('ID list SUBTRACT expr')
    @_('ID list MULTIPLY_BY expr')
    @_('ID list DIVIDE_BY expr')
    @_('ID list ASSIGN expr')
    @_("ID '=' STRING")
    def assignment(self, p):
        return p[0]

    @_("FOR ID ASSIGN range_expr instruction")
    def for_loop(self, p):
        return p[0]

    @_('INTEGER RANGE INTEGER')
    @_("ID RANGE ID")
    @_("INTEGER RANGE ID")
    def range_expr(self, p):
        return p[0]

    @_("WHILE '(' condition ')' instruction")
    def while_loop(self, p):
        return p[0]

    @_("PRINT terms")
    @_("PRINT STRING")
    def print_statement(self, p):
        return AST.Instruction(p[0], p[1])

    @_("BREAK")
    @_("CONTINUE")
    @_("RETURN expr")
    def keyword_statement(self, p):
        return AST.Instruction(p[0], p[1] if len(p) > 1 else None)

    @_('expr EQ expr')
    @_('expr LE expr')
    @_('expr LT expr')
    @_('expr GE expr')
    @_('expr GT expr')
    @_('expr NE expr')
    @_("'(' condition ')'")
    def condition(self, p):
        return AST.Condition(p[1], p[0], p[2])

    @_('term')
    @_('arithmetic_expr')
    @_('matrix_expr')
    @_('"-" expr %prec UMINUS')
    @_("'(' expr ')'")
    def expr(self, p):
        return p[0]

    @_('expr "+" expr')
    @_('expr "-" expr')
    @_("expr '*' expr")
    @_("expr '/' expr")
    def arithmetic_expr(self, p):
        return AST.BinExpr(p[1], p[0], p[2])

    @_('expr MATRIX_PLUS expr')
    @_('expr MATRIX_MINUS expr')
    @_('expr MATRIX_MUL expr')
    @_('expr MATRIX_DIV expr')
    def matrix_expr(self, p):
        return AST.BinExpr(p[1], p[0], p[2])

    @_("EYE '(' INTEGER ')'")
    @_("ZEROS '(' INTEGER ')'")
    @_("ONES '(' INTEGER ')' ")
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


    @_('numeric')
    @_('list')
    @_('MATRIX')
    @_("ID TRANSPOSE")
    def term(self, p):
        return p[0]

    @_('ID list')
    def term(self, p):
        return AST.Adnotation(p[0], p[1])

    @_('ID')
    def term(self, p):
        return AST.Variable(p[0])

    @_('INTEGER')
    @_('FLOAT')
    def numeric(self, p):
        return AST.Numeric(p[0])

    # @_('ADD')
    # @_('SUBTRACT')
    # @_('MULTIPLY_BY')
    # @_('DIVIDE_BY')
    # @_('ASSIGN')
    # def assign_operator(self, p):
    #     return p[0]

    # @_('EQ')
    # @_('LE')
    # @_('LT')
    # @_('GE')
    # @_('GT')
    # @_('NE')
    # def relational_operator(self, p):
    #     return p[0]

    # @_('MATRIX_PLUS')
    # @_('MATRIX_MINUS')
    # @_('MATRIX_MUL')
    # @_('MATRIX_DIV')
    # def matrix_operator(self, p):
    #     return p[0]

