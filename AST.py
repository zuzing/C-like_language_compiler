class Node(object):
    pass


class Program(Node):
    def __init__(self, instructions):
        self.instructions = instructions


class Instruction(Node):
    def __init__(self, instruction, *args):
        self.instruction = instruction
        self.args = args


class Ifstatement(Node):
    def __init__(self, condition, instruction, elsepart):
        self.condition = condition
        self.instruction = instruction
        self.elsepart = elsepart


class Range(Node):
    def __init__(self, start, end):
        self.start = start
        self.end = end

class Assignment(Node):
    def __init__(self, var, symbol, expr):
        self.id = var
        self.symbol = symbol
        self.expr = expr


class BinaryOperation(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class UnaryOperation(Node):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand


class Vector(Node):
    def __init__(self, elements):
        self.elements = elements


class Reference(Node):
    def __init__(self, name, index):
        self.name = name
        self.index = index


class Variable(Node):
    def __init__(self, name):
        self.name = name


class Numeric(Node):
    def __init__(self, value):
        self.value = value


class Error(Node):
    def __init__(self):
        pass
      
