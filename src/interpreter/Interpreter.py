import AST
import SymbolTable
from interpreter.Memory import *
from interpreter.Exceptions import  *
from interpreter.visit import *
import sys
import operator

sys.setrecursionlimit(10000)


class Interpreter(object):
    def __init__(self, memory_stack = None):
        if memory_stack is None:
            memory_stack = MemoryStack()
        self.memory_stack = memory_stack

    @on('node')
    def visit(self, node):
        pass

    @when(AST.Program)
    def visit(self, node):
        for instruction in node.instructions:
            instruction.accept(self)

    @when(AST.Block)
    def visit(self, node):
        self.memory_stack.push(Memory("Block"))
        for instruction in node.instructions:
            instruction.accept(self)
        self.memory_stack.pop()


    @when(AST.FunctionalInstruction)
    def visit(self, node):
        if node.instruction == 'print':
            # print(node.args.accept(self))
            # print(*[arg.accept(self) for arg in node.args])
            print(" ".join(str(arg.accept(self)) for arg in node.args))
        elif node.instruction == 'zeros':
            # n = []
            # for arg in node.args:
            #     val = arg.accept(self)
            #     n.append(val)
            n = [arg.accept(self) for arg in node.args]
            if len(n) == 1:
                n = (n[0], n[0])
            return [[0 for _ in range(n[0])] for _ in range(n[1])]
        elif node.instruction == 'ones':
            n = [arg.accept(self) for arg in node.args]
            if len(n) == 1:
                n = (n[0], n[0])
            return [[1 for _ in range(n[0])] for _ in range(n[1])]
        elif node.instruction == 'eye':
            return [[1 if i == j else 0 for j in range(node.args[0].accept(self))] for i in range(node.args[0].accept(self))]


    @when(AST.WhileInstruction)
    def visit(self, node):
        while node.condition.accept(self):
            try:
                node.body.accept(self)
            except BreakException:
                break
            except ContinueException:
                continue

    @when(AST.ForLoopInstruction)
    def visit(self, node):
        start = node.range.start.accept(self)
        end = node.range.end.accept(self)

        self.memory_stack.insert(node.id.name, start)

        for i in range(start, end):
            self.memory_stack.set(node.id.name, i)  # TODO: scope for loop variable
            try:
                node.body.accept(self)
            except BreakException:
                break
            except ContinueException:
                continue


    @when(AST.FlowControlInstruction)
    def visit(self, node):
        if node.instruction == 'break':
            raise BreakException()
        elif node.instruction == 'continue':
            raise ContinueException()

    @when(AST.Ifstatement)
    def visit(self, node):
        if node.condition.accept(self):
            node.instruction.accept(self)
        elif node.elsepart:
            node.elsepart.accept(self)

    @when(AST.Assignment)
    def visit(self, node):
        TRANSLATION_TABLE = {
            '+=': '+',
            '-=': '-',
            '*=': '*',
            '/=': '/'
        }
        if node.op in TRANSLATION_TABLE:
            op = TRANSLATION_TABLE[node.op]
            value = AST.BinaryOperation(op, node.id, node.expr).accept(self)
        else:
            value = node.expr.accept(self)

        if not isinstance(node.id, AST.Reference):
            self.memory_stack.set(node.id.name, value)
        else:
            base = self.memory_stack.get(node.id.id.name)
            index = node.id.index.accept(self)

            if isinstance(index, list):

                for j in range(len(index)): # needed to access elements
                    index[j] = index[j].accept(self)

                for i in index[:-1]:  # recursively accesses the nested lists
                    base = base[i]
            base[index[-1]] = value


    @when(AST.BinaryOperation)
    def visit(self, node):
        def elementwise_operation(op, matrix1, matrix2):
            if isinstance(matrix1[0], list):  # both matrices are 2D (checked in semantic analysis)
                return [[op(matrix1[i][j], matrix2[i][j]) for j in range(len(matrix1[0]))] for i in range(len(matrix1))]
            else: # both matrices are 1D
                return [op(matrix1[i], matrix2[i]) for i in range(len(matrix1))]


        left = node.left.accept(self)
        right = node.right.accept(self)
        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            return left / right
        elif node.op == '==':
            return left == right
        elif node.op == '!=':
            return left != right
        elif node.op == '>':
            return left > right
        elif node.op == '<':
            return left < right
        elif node.op == '>=':
            return left >= right
        elif node.op == '<=':
            return left <= right
        elif node.op == '.+':
            return elementwise_operation(operator.add, left, right)
        elif node.op == '.-':
            return elementwise_operation(operator.sub, left, right)
        elif node.op == '.*':
            return elementwise_operation(operator.mul, left, right)
        elif node.op == './':
            return elementwise_operation(operator.truediv, left, right)

    @when(AST.UnaryOperation)
    def visit(self, node):
        operand = node.operand.accept(self)
        if node.op == '-':
            return -operand
        elif node.op == "'":
            return [[node.operand[j][i] for j in range(len(node.operand))] for i in range(len(node.operand[0].accept(self)))]

    @when(AST.Vector)
    def visit(self, node):
        return node.elements

    @when(AST.Reference)
    def visit(self, node):
        base = self.memory_stack.get(node.id.name)
        index = node.index.accept(self)

        if isinstance(index, list):
            for i in index:
                i = i.accept(self)
                base = base[i]
        else:
            index = index.accept(self)
            base = base[index]
        return base

    @when(AST.Variable)
    def visit(self, node):
        return self.memory_stack.get(node.name)

    @when(AST.Integer)
    def visit(self, node):
        return node.value

    @when(AST.Float)
    def visit(self, node):
        return node.value

    @when(AST.String)
    def visit(self, node):
        return node.value




