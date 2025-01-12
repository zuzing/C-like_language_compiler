from __future__ import annotations
from dataclasses import dataclass


class Node(object):
    pass


@dataclass
class Program(Node):
    instructions: list


@dataclass
class Instruction(Node):
    instruction: str
    args: tuple


@dataclass
class Ifstatement(Node):
    condition: Node
    instruction: Node
    elsepart: Node


@dataclass
class Range(Node):
    start: int
    end: int


@dataclass
class Assignment(Node):
    id: str | Node
    op: str
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


@dataclass
class Reference(Node):
    name: str
    index: Vector


@dataclass
class Variable(Node):
    name: str


@dataclass
class Numeric(Node):
    value: int | float

    def __eq__(self, other):
        if isinstance(other, Numeric):
            return self.value == other.value
        return self.value == other


@dataclass
class String(Node):
    value: str


class Error(Node):
    pass
