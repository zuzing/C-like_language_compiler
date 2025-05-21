import sys
from Scanner import Scanner
from Parser import Parser
from TreePrinter import TreePrinter
from NodeVisitor import NodeVisitor


if __name__ == '__main__':

    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "example.txt"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    text = file.read()
    lexer = Scanner()
    parser = Parser()

    ast = parser.parse(lexer.tokenize(text))
    ast.printTree()

    node_visitor = NodeVisitor()
    node_visitor.visit(ast)

    # ast.accept(Interpreter())
