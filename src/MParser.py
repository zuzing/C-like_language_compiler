from sly import Parser
from Scanner import Scanner
import AST


class Mparser(Parser):
    tokens = Scanner.tokens

    debugfile = None

    @classmethod
    def debug(cls, debugfile: str):
        cls.debugfile = debugfile
        if hasattr(cls, '_grammar') and hasattr(cls, '_lrtable'):
            cls._apply_debugfile()

    @classmethod
    def _apply_debugfile(cls):
        if cls.debugfile:
            with open(cls.debugfile, 'w') as f:
                f.write(str(cls._grammar))
                f.write('\n')
                f.write(str(cls._lrtable))
            cls.log.info('Parser debugging for %s written to %s', cls.__qualname__, cls.debugfile)



    precedence = (  # tokens are ordered from lowest to highest precedence
        ("left", 'LT', 'GT'),
        ("left", 'EQ', 'NE', 'GE', 'LE'),
        ("left", "+", "-"),
        ("left", 'MATRIX_PLUS', 'MATRIX_MINUS'),
        ("left", "*", "/"),
        ("left",  'MATRIX_MUL', 'MATRIX_DIV'),
        ("left", 'UMINUS'),
        ("nonassoc", 'IFX'),
        ("nonassoc", 'ELSE')
    )

    @_('statements')
    def program(self, p):
        return AST.Program(p[0])

    @_('statement')
    @_('statement statements')
    def statements(self, p):
        return p[0] if len(p) == 1 else ([p[0]] + p[1] if isinstance(p[1], list) else [p[0], p[1]])

    @_('if_statement')
    @_('for_loop')
    @_('while_loop')
    @_('assignment ";"')
    @_('print_statement ";"')
    @_('keyword_statement ";"')
    @_('block')
    def statement(self, p):
        return p[0]

    @_(" '{' statements '}'")
    def block(self, p):
        return p[1]

    @_("IF '(' condition ')' statement %prec IFX")
    @_("IF '(' condition ')' statement ELSE statement")
    def if_statement(self, p):
        return AST.Ifstatement(p[2], p[4], p[6] if len(p) > 5 else None)


    @_('ID ADD expr')
    @_('ID SUBTRACT expr')
    @_('ID MULTIPLY_BY expr')
    @_('ID DIVIDE_BY expr')
    @_('ID ASSIGN expr')
    @_('reference ADD expr')
    @_('reference SUBTRACT expr')
    @_('reference MULTIPLY_BY expr')
    @_('reference DIVIDE_BY expr')
    @_('reference ASSIGN expr')
    @_('ID ASSIGN string')
    def assignment(self, p):
        return AST.Assignment(p[0], p[1], p[2])



    @_("FOR ID ASSIGN range_expr statement")
    def for_loop(self, p):
        return AST.Instruction(p[0], (p[1], p[3], p[4]))

    @_('INTEGER RANGE INTEGER')
    @_("ID RANGE ID")
    @_("INTEGER RANGE ID")
    def range_expr(self, p):
        return AST.Range(p[0], p[2])

    @_("WHILE '(' condition ')' statement")
    def while_loop(self, p):
        return AST.Instruction(p[0], (p[2], p[4]))

    @_("PRINT terms")
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
    def condition(self, p):
        return AST.BinaryOperation(p[1], p[0], p[2])

    @_('term')
    @_('arithmetic_expr')
    @_('matrix_expr')
    def expr(self, p):
        return p[0]

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return AST.UnaryOperation(p[0], p[1])

    @_("'(' expr ')'")
    def expr(self, p):
        return p[1]

    @_('expr "+" expr')
    @_('expr "-" expr')
    @_("expr '*' expr")
    @_("expr '/' expr")
    def arithmetic_expr(self, p):
        return AST.BinaryOperation(p[1], p[0], p[2])

    @_('expr MATRIX_PLUS expr')
    @_('expr MATRIX_MINUS expr')
    @_('expr MATRIX_MUL expr')
    @_('expr MATRIX_DIV expr')
    def matrix_expr(self, p):
        return AST.BinaryOperation(p[1], p[0], p[2])

    @_("EYE '(' INTEGER ')'")
    @_("ZEROS '(' INTEGER ')'")
    @_("ONES '(' INTEGER ')' ")
    def MATRIX(self, p):
        return AST.Instruction(p[0], p[2])

    @_('MATRIX TRANSPOSE')
    def MATRIX(self, p):
        return AST.UnaryOperation(p[1], p[0])

    @_(" '[' terms ']' ")
    def list(self, p):
        return AST.Vector(p[1])

    @_("term")
    @_("term ',' terms")
    def terms(self, p):
        return p[0] if len(p) == 1 else ([p[0]] + p[2] if isinstance(p[2], list) else [p[0], p[2]])

    @_('reference')
    @_('numeric')
    @_('list')
    @_('MATRIX')
    def term(self, p):
        return p[0]

    @_("ID TRANSPOSE")
    def term(self, p):
        return AST.UnaryOperation(p[1], AST.Variable(p[0]))

    @_('ID')
    def term(self, p):
        return AST.Variable(p[0])

    @_('ID list')
    def reference(self, p):
        return AST.Reference(p[0], p[1])

    @_('INTEGER')
    @_('FLOAT')
    def numeric(self, p):
        return AST.Numeric(p[0])

    @_('STRING')
    def string(self, p):
        return AST.String(p[0])

    def error(self, p):
        if p is not None:
            raise Exception(
                f"Syntax error at line {p.lineno}: Unexpected token '{p.value}'")
        else:
            raise Exception(
                f"Syntax error at end of input")