import AST
from SymbolTable import SymbolTable, VectorVariableSymbol, VariableSymbol, Symbol, UNKNOWN

class NodeVisitor(object):
    def __init__(self):
        self.symbol_table = SymbolTable(parent_scope=None, name="global")
        self.current_loop = 0

    @staticmethod
    def _get_children(node):
        return [
            child for name, child in vars(node).items()
            if not name.startswith("_")
        ]

    def visit(self, node):
        """Visits a node by finding the appropriate visit method."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node.
        It depends on visit function to continue the traversal."""
        if isinstance(node, AST.Node):
            for child in self._get_children(node):
                if isinstance(child, AST.Node) or isinstance(child, list):
                    self.visit(child)
        elif hasattr(node, "__iter__"):
            for elem in node:
                self.visit(elem)


    def visit_Assignment(self, node):
        TRANSLATION_TABLE = {
            '+=': '+',
            '-=': '-',
            '*=': '*',
            '/=': '/',
        }

        var_name = node.id.name
        var_symbol = self.symbol_table.get(var_name)
        if node.op == '=':
            if var_symbol is None:
                self.symbol_table.put(VariableSymbol(name=var_name, type_=UNKNOWN))
            self.visit(node.expr)
        else:
            if var_symbol is None:
                raise Exception(f"Undefined variable: {var_name}")
            self.visit(node.expr)
            self.visit(AST.BinaryOperation(TRANSLATION_TABLE[node.op], AST.Variable(var_name), node.expr))


    def visit_Variable(self, node):
        if self.symbol_table.get(node.name) is None:
            raise Exception(f"Undefined variable: {node.name}")


    def visit_BinaryOperation(self, node):
        MATRIX_OPERATIONS = {
            ('.+', AST.Vector, AST.Vector): AST.Vector,
            ('.-', AST.Vector, AST.Vector): AST.Vector,
            ('.*', AST.Vector, AST.Vector): AST.Vector,
            ('./', AST.Vector, AST.Vector): AST.Vector,
            ('+', AST.Vector, AST.Vector): AST.Vector,
            ('-', AST.Vector, AST.Vector): AST.Vector,
            ('*', AST.Vector, AST.Vector): AST.Vector,
        }
        ALLOWED_OPERATIONS = {
             ('==', AST.Numeric, AST.Numeric): bool,
             ('<=', AST.Numeric, AST.Numeric): bool,
             ('<', AST.Numeric, AST.Numeric): bool,
             ('>=', AST.Numeric, AST.Numeric): bool,
             ('>', AST.Numeric, AST.Numeric): bool,
             ('!=', AST.Numeric, AST.Numeric): bool,
             ('+', AST.Numeric, AST.Numeric): AST.Numeric,
             ('-', AST.Numeric, AST.Numeric): AST.Numeric,
             ('*', AST.Numeric, AST.Numeric): AST.Numeric,
             ('/', AST.Numeric, AST.Numeric): AST.Numeric,
            ('*', AST.Numeric, AST.Vector): AST.Vector,
             **MATRIX_OPERATIONS,
        }

        def check_vector_shapes(op: str, left_vector: AST.Vector, right_vector: AST.Vector):
            left_shape = left_vector.shape()
            right_shape = right_vector.shape()

            if op == '*':
                if len(left_shape) > 2 or len(right_shape) > 2:
                    raise Exception(f"Matrix multiplication is only supported for 2D matrices: {left_shape} {right_shape}")
                if len(left_shape) != len(right_shape) or left_shape[-1] != right_shape[0]:
                    raise Exception(f"Vector dimensions must agree: {left_shape} != {right_shape}")
            else:
                if left_shape != right_shape:
                    raise Exception(f"Vector dimensions must agree: {left_shape} != {right_shape}")

        self.visit(node.left)
        self.visit(node.right)

        if isinstance(node.left, AST.Variable):
            left_type = self.symbol_table.get(node.left.name).type
        else:
            left_type = node.left.__class__.__name__

        if isinstance(node.right, AST.Variable):
            right_type = self.symbol_table.get(node.right.name).type
        else:
            right_type = node.right.__class__.__name__

        operation = (node.op, left_type, right_type)
        if operation in ALLOWED_OPERATIONS.keys():
            if operation in MATRIX_OPERATIONS.keys():
                check_vector_shapes(node.op, node.left, node.right)
        else:
            raise Exception(f"Unsupported operation: {left_type} {node.op} {right_type}")


    def visit_UnaryOperation(self, node):
        self.visit(node.operand)

        ALLOWED_OPERATIONS = {
            ("'", AST.Vector): AST.Vector,
            ('-', AST.Numeric): AST.Numeric,
            ('-', AST.Vector): AST.Vector,
        }

        if isinstance(node.operand, AST.Variable):
            operand_type = self.symbol_table.get(node.operand.name).type
        else:
            operand_type = node.operand.__class__.__name__

        operation = (node.op, operand_type)

        if operation not in ALLOWED_OPERATIONS.keys():
            raise Exception(f"Unsupported operation: {node.op} {node.operand.__class__.__name__}")


    def visit_Reference(self, node):
        self.visit(node.id)
        self.visit(node.index)

        id = self.symbol_table.get(node.id.name)

        if id.type is AST.Vector:
            if len(node.index) > len(id.shape):
                raise Exception(f"Index out of bounds: {node.id} {node.index}")
            for i in range(len(id.shape)):
                if not isinstance(node.index[i], int):
                    raise Exception(f"Indexes must be an integers: {node.id} {node.index}")
                if node.index[i] < 0 or node.index[i] >= id.shape[i]:
                    raise Exception(f"Index out of bounds: {node.id} {node.index}")
        else:
            raise Exception(f"Variable is not a vector: {node.id}")


    def visit_Instruction(self, node):
        ALLOWED_ARGUMENT_TYPES = {
            'EYE': [int],
            'ZEROS': [int],
            'ONES': [int],
        }
        SCOPE_CONTROL = {
            'BREAK',
            'CONTINUE',
            'RETURN',
        }

        LOOP_INSTRUCTIONS = {
            'FOR',
            'WHILE',
        }

        if node.instruction in SCOPE_CONTROL:
            if self.current_loop == 0:
                raise Exception(f"Flow control instruction outside loop: {node.instruction}")

        if node.instruction in ALLOWED_ARGUMENT_TYPES.keys():
            arg_types = [arg.__class__ for arg in node.args]
            if arg_types != ALLOWED_ARGUMENT_TYPES[node.instruction]:
                raise Exception(f"Invalid arguments for instruction {node.instruction}")

        if node.instruction in LOOP_INSTRUCTIONS:
            self.symbol_table = SymbolTable(parent_scope=self.symbol_table, name=node.instruction)
            self.current_loop += 1
            self.visit(node.args[0])
            self.symbol_table = self.symbol_table.parent_scope
            self.current_loop -= 1










    # def generic_visit(self, node):        # Called if no explicit visitor function exists for a node.
    #     if isinstance(node, list):
    #         for elem in node:
    #             self.visit(elem)
    #     else:
    #         for child in node.children:
    #             if isinstance(child, list):
    #                 for item in child:
    #                     if isinstance(item, AST.Node):
    #                         self.visit(item)
    #             elif isinstance(child, AST.Node):
    #                 self.visit(child)
