import AST


def addToClass(cls):

    def decorator(func):
        setattr(cls,func.__name__,func)
        return func
    return decorator


class TreePrinter:
    keyword_mapping = {
        'else': 'ELSE',
        'for': 'FOR',
        'while': 'WHILE',
        'print': 'PRINT',
        'break': 'BREAK',
        'continue': 'CONTINUE',
        'return': 'RETURN',
        'eye': 'EYE',
        'zeros': 'ZEROS',
        'ones': 'ONES',
        "'": 'TRANSPOSE',
    }

    @staticmethod
    def indent_text(text, indent):
        """Helper function to generate indented text."""
        return "|  " * indent + text

    @staticmethod
    def print(obj, indent_level):
        """Helper to print either a Node, content of a list (or tuple) or a literal value."""
        if isinstance(obj, AST.Node):
            obj.printTree(indent_level)
        elif isinstance(obj, list):
            for elem in obj:
                TreePrinter.print(elem, indent_level)
        else:  # literal value
            transformed_obj = TreePrinter.keyword_mapping.get(obj, obj)
            indented_text = TreePrinter.indent_text(f"{transformed_obj}", indent_level)
            print(indented_text)

    @addToClass(AST.Node)
    def printTree(self, indent=0):
        raise Exception("printTree not defined in class " + self.__class__.__name__)


    @addToClass(AST.Program)
    def printTree(self, indent=0):
        for instruction in self.instructions:
            TreePrinter.print(instruction, indent)

    @addToClass(AST.Instruction)
    def printTree(self, indent=0):
        TreePrinter.print(self.instruction, indent)
        if not isinstance(self.args, tuple):
            TreePrinter.print(self.args, indent+1)
        else:
            for arg in self.args:
                TreePrinter.print(arg, indent + 1)


    @addToClass(AST.Ifstatement)
    def printTree(self, indent=0):
        print(TreePrinter.indent_text("IF", indent))
        TreePrinter.print(self.condition, indent+1)
        print(TreePrinter.indent_text("THEN", indent))
        TreePrinter.print(self.instruction, indent+1)
        if self.elsepart:
            print(TreePrinter.indent_text("ELSE", indent))
            TreePrinter.print(self.elsepart, indent+1)


    @addToClass(AST.Range)
    def printTree(self, indent=0):
        print(TreePrinter.indent_text("RANGE", indent))
        TreePrinter.print(self.start, indent+1)
        TreePrinter.print(self.end, indent+1)


    @addToClass(AST.Assignment)
    def printTree(self, indent=0):
        print(TreePrinter.indent_text(f"{self.op}", indent))
        TreePrinter.print(self.id, indent + 1)
        TreePrinter.print(self.expr, indent + 1)

    @addToClass(AST.BinaryOperation)
    def printTree(self, indent=0):
        TreePrinter.print(self.op, indent)
        TreePrinter.print(self.left, indent+1)
        TreePrinter.print(self.right, indent+1)


    @addToClass(AST.UnaryOperation)
    def printTree(self, indent=0):
        TreePrinter.print(self.op, indent)
        TreePrinter.print(self.operand, indent+1)


    @addToClass(AST.Vector)
    def printTree(self, indent=0):
        print(TreePrinter.indent_text("VECTOR", indent))
        for element in self.elements:
            TreePrinter.print(element, indent+1)

    @addToClass(AST.Reference)
    def printTree(self, indent=0):
        print(TreePrinter.indent_text("REF", indent))
        TreePrinter.print(self.id, indent+1)
        try:
            TreePrinter.print(self.index.elements, indent+1)  # index is a Vector, by accessing its elements we can omit printing VECTOR, making AST more readable
        except AttributeError:
            raise Exception("Index can only be a 1D Vector")

    @addToClass(AST.Variable)
    def printTree(self, indent=0):
        print(TreePrinter.indent_text(f"{self.name}", indent))


    @addToClass(AST.Numeric)
    def printTree(self, indent=0):
        print(TreePrinter.indent_text(f"{self.value}", indent))


    @addToClass(AST.String)
    def printTree(self, indent=0):
        print(TreePrinter.indent_text(f"{self.value}", indent))

    @addToClass(AST.Error)
    def printTree(self, indent=0):
        print(TreePrinter.indent_text("ERROR", indent))

