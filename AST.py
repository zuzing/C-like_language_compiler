

class Node(object):
    pass


class Numeric(Node):
    def __init__(self, value):
        self.value = value


class Variable(Node):
    def __init__(self, name):
        self.name = name


class BinExpr(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class Adnotation(Node):
    def __init__(self, var, adnotation):
        self.id = var
        self.adnotation = adnotation


class Condition(Node):
    def __init__(self, sign, left, right):
        self.op = sign
        self.left = left
        self.right = right


class Instruction(Node):
    def __init__(self, instruction, args=None):
        self.instruction = instruction
        self.args = args



class Error(Node):
    def __init__(self):
        pass
      
