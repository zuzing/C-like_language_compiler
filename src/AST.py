from __future__ import annotations
from dataclasses import dataclass
import warnings


class Node(object):
    def accept(self, visitor):
        return visitor.visit(self)


@dataclass
class Program(Node):
    instructions: list


@dataclass
class Block(Program):
    instructions: list


class Instruction(Node):
    def __init__(self, instruction, *args):
        self.instruction = instruction
        self.args = args


class FunctionalInstruction(Instruction):
    def __init__(self, instruction, *args):
        super().__init__(instruction, *args)



class WhileInstruction(Instruction):
    def __init__(self, instruction, *args):
        super().__init__(instruction, *args)
        self.condition = args[0]
        self.body = args[1]


class ForLoopInstruction(Instruction):
    def __init__(self, instruction, *args):
        super().__init__(instruction, *args)
        self.id = args[0]
        self.range = args[1]
        self.body = args[2]


@dataclass
class Range(Node):
    start: int
    end: int


class FlowControlInstruction(Instruction):
    def __init__(self, instruction, *args):
        super().__init__(instruction, *args)


@dataclass
class Ifstatement(Node):
    condition: Node
    instruction: Node
    elsepart: Node


@dataclass
class Assignment(Node):
    op: str
    id: Variable | Reference
    expr: Node


@dataclass
class BinaryOperation(Node):
    op: str
    left: Node
    right: Node


@dataclass
class UnaryOperation(Node):
    op: str
    operand: Node


@dataclass
class Vector(Node):
    elements: list

    def shape(self) -> tuple | None:
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
                return  # dimensions match

            for element in subvector:
                if len(element) != shape[dimension]:
                    raise Exception(f"Vector dimensions do not match for vector: {self}")
                check_dimension(dimension + 1, element)

        find_shape(self)
        shape = tuple(shape)
        try:
            check_dimension(1, self)
        except Exception as e:
            warnings.warn(str(e))
            return None

        return shape

    def __len__(self):
        return len(self.elements)

    def __getitem__(self, index):
        return self.elements[index]


@dataclass
class Reference(Node):
    id: Variable
    index: Vector


@dataclass(frozen=True)
class Variable(Node):
    name: str


@dataclass
class Numeric(Node):
    value: int | float

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __eq__(self, other):
        if isinstance(other, Numeric):
            return self.value == other.value
        return self.value == other

    def __hash__(self):
        return hash(self.value)


class Integer(Numeric, int):
    def __init__(self, value):
        super().__init__(int(value))

class Float(Numeric, float):
    def __init__(self, value):
        super().__init__(float(value))


@dataclass
class String(Node):
    value: str


class Error(Node):
    pass
