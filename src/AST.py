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


class Vector(Node, list):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def shape(self) -> tuple:
        shape = [len(self.elements)]

        def find_shape(subvector):
            """
            Recursively finds the length of the subvectors.
            """
            nonlocal shape

            first_element = subvector[0]
            if isinstance(first_element, Vector) or isinstance(first_element, list):
                shape.append(len(first_element))
                find_shape(first_element)


        def check_dimension(dimension: int, subvector):
            """
            Checks if the dimensions of the subvectors agree.
            """
            if dimension == len(shape):
                return

            for element in subvector:
                if len(element) != shape[dimension]:
                    raise Exception(f"Vector dimensions do not agree for vector: {self}")
                check_dimension(dimension + 1, element)

        find_shape(self)
        shape = tuple(shape)
        check_dimension(1, self)

        return shape


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
      
