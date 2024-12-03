import AST
from SymbolTable import SymbolTable


class NodeVisitor(object):
    def __init__(self):
        self.symbol_table = None
        self.current_loop = 0

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        if isinstance(node, list):
            for elem in node:
                self.generic_visit(elem)
        elif isinstance(node, AST.Node):
            for child in node.children:
                    self.visit(child)
        else:
            raise Exception("Error: NodeVisitor: generic_visit: node is not a list or AST.Node")

    def visit_Program(self, node):
        self.symbol_table = SymbolTable(parent=None, name="global")
        self.visit(node.instructions)




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
