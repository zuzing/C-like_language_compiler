from typing import Optional, get_args
import warnings

import AST
from SymbolTable import SymbolTable, VectorType, VariableSymbol, TYPE


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
		elif isinstance(node, list):
			for elem in node:
				self.visit(elem)


	def visit_VariableSymbol(self, node):
		return node.type

	def visit_Block(self, node):
		self.symbol_table = SymbolTable(parent_scope=self.symbol_table, name="block")
		self.visit(node.instructions)
		self.symbol_table = self.symbol_table.parent_scope


	def visit_FunctionalInstruction(self, node) -> TYPE:
		ALLOWED_ARGUMENT_TYPES = {
			'eye': [AST.Integer, Optional[AST.Integer]],
			'zeros': [AST.Integer, Optional[AST.Integer]],
			'ones': [AST.Integer, Optional[AST.Integer]],
			'print': ['*'],
		}
		FUNCTION_RETURN_TYPES = {
			'eye': lambda x, y=None: VectorType(shape=(x, y if y is not None else x)),
			'zeros': lambda x, y=None: VectorType(shape=(x, y if y is not None else x)),
			'ones': lambda x, y=None: VectorType(shape=(x, y if y is not None else x)),
			'print': lambda *args: None,
		}

		arg_types = [arg for arg in node.args]
		expected_types = ALLOWED_ARGUMENT_TYPES[node.instruction]

		if '*' in expected_types:
			return FUNCTION_RETURN_TYPES[node.instruction](*arg_types)

		for i, expected_type in enumerate(expected_types):
			if i >= len(arg_types):  # if fewer arguments than expected
				if Optional[AST.Integer] in expected_types[i:]:  # TODO: make more general
					continue
				else:
					warnings.warn(f"Missing required argument for instruction {node.instruction}")
					return
			if expected_type is Optional:
				expected_type = AST.Integer

			if not isinstance(arg_types[i], expected_type):
				warnings.warn(f"Invalid argument type for instruction {node.instruction}: expected {expected_type}, got {type(arg_types[i])}")

		if len(arg_types) > len(expected_types):
			warnings.warn(f"Too many arguments provided for instruction {node.instruction}")
			return

		return FUNCTION_RETURN_TYPES[node.instruction](*node.args)


	def visit_FlowControlInstruction(self, node) -> TYPE:
		if self.current_loop == 0:
			warnings.warn(f"Flow control instruction outside loop: {node.instruction}")
		else:
			if node.instruction == 'BREAK' or node.instruction == 'RETURN':
				self.current_loop -= 1
				self.symbol_table = self.symbol_table.parent_scope

		if node.instruction == 'RETURN':
			return self.visit(node.args[0])


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
			type_ = self.visit(node.expr)
			if var_symbol is None:
				self.symbol_table.put(VariableSymbol(name=var_name, type_=type_))
			else:
				var_symbol.type = type_
		else:
			if var_symbol is None:
				warnings.warn(f"Undefined variable: {var_name}")
			type_ = self.visit(AST.BinaryOperation(TRANSLATION_TABLE[node.op], AST.Variable(var_name), node.expr))
			self.symbol_table.get(var_name).type = type_



	def visit_BinaryOperation(self, node) -> TYPE:
		MATRIX_OPERATIONS = {
			('.+', VectorType, VectorType): VectorType,
			('.-', VectorType, VectorType): VectorType,
			('.*', VectorType, VectorType): VectorType,
			('./', VectorType, VectorType): VectorType,
			('+', VectorType, VectorType): VectorType,
			('-', VectorType, VectorType): VectorType,
			('*', VectorType, VectorType): VectorType,
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
			('*', AST.Numeric, VectorType): VectorType,
			('*', AST.Numeric, AST.String): AST.String,
			('*', AST.String, AST.Numeric): AST.String,
			**MATRIX_OPERATIONS,
		}

		def vector_shapes(op: str, left_vector: AST.Vector, right_vector: AST.Vector) -> VectorType:
			left_shape = left_vector.shape()
			right_shape = right_vector.shape()

			if op == '*':
				if len(left_shape) > 2 or len(right_shape) > 2:
					raise Exception(
						f"Matrix multiplication is only supported for 2D matrices: {left_shape} {right_shape}")
				if len(left_shape) != len(right_shape) or left_shape[1] != right_shape[0]:
					raise Exception(f"Vector dimensions must agree: {left_shape} != {right_shape}")
				return VectorType(shape=(left_shape[0], right_shape[1]))
			else:
				if left_shape != right_shape:
					raise Exception(f"Vector dimensions must agree: {left_shape} != {right_shape}")
				return VectorType(shape=left_shape)

		def get_ancestor(cls):
			# returns the first base class or None if no base exists
			return cls.__bases__[0] if hasattr(cls, '__bases__') and cls.__bases__ else None


		left_type = self.visit(node.left)
		right_type = self.visit(node.right)

		if left_type is AST.Integer or left_type is AST.Float:
			left_type = get_ancestor(left_type)

		if right_type is AST.Integer or right_type is AST.Float:
			right_type = get_ancestor(right_type)


		operation = (node.op, left_type, right_type)
		if operation in ALLOWED_OPERATIONS.keys():
			if operation in MATRIX_OPERATIONS.keys():
				return vector_shapes(node.op, node.left, node.right)
			return ALLOWED_OPERATIONS[operation]
		else:
			warnings.warn(f"Unsupported operation: {left_type} {node.op} {right_type} for {node.left} {node.op} {node.right}")

	def visit_UnaryOperation(self, node) -> TYPE:
		self.visit(node.operand)

		ALLOWED_OPERATIONS = {
			("'", VectorType): VectorType,
			('-', AST.Numeric): AST.Numeric,
			('-', VectorType): VectorType,
		}

		if isinstance(node.operand, AST.Variable):
			operand_type = self.symbol_table.get(node.operand.name).type
		else:
			operand_type = node.operand.__class__.__name__

		operation = (node.op, operand_type)

		if operation not in ALLOWED_OPERATIONS.keys():
			warnings.warn(
				f"Unsupported operation: {operand_type} {node.operand.__class__.__name__} for {node.op} {node.operand}")

		if ALLOWED_OPERATIONS[operation] is VectorType:
			if isinstance(node.operand, AST.Variable):
				return VectorType(shape=self.symbol_table.get(node.operand.name).type.shape())
			else:
				return VectorType(shape=node.operand.shape())
		else:
			return ALLOWED_OPERATIONS[operation]

	def visit_Reference(self, node) -> TYPE:
		id_type = self.visit(node.id)
		index_types = [i.accept(self) for i in node.index]  #TODO: recursive visits

		if isinstance(id_type, VectorType):
			if len(index_types) > len(id_type.shape):
				warnings.warn(f"Index out of bounds: {node.id} {node.index}")
				return
			for i in range(len(id_type.shape)):  # check if indexes are integers and within bounds
				if not isinstance(node.index[i], AST.Integer):
					warnings.warn(f"Indexes must be an integers: {node.id} {node.index} in {node}")
					return
				if node.index[i] < 0 or node.index[i] >= id_type.shape[i]:
					warnings.warn(f"Index out of bounds: {node.id} {node.index} in {node}")
					return

			if len(node.index) == len(id.shape):
				return AST.Numeric
			else:
				return VectorType(shape=id.shape[len(node.index):])
		else:
			warnings.warn(f"Variable is not a vector: {node.id} in {node} is type {id_type}")

	def visit_Vector(self, node) -> TYPE:
		return VectorType(shape=(node.shape()))

	def visit_Variable(self, node):
		if self.symbol_table.get(node.name) is None:
			warnings.warn(f"Variable referenced before assignment: {node.name}")
		return self.symbol_table.get(node.name).type

	def visit_Integer(self, node) -> TYPE:
		return AST.Integer

	def visit_Float(self, node) -> TYPE:
		return AST.Float

	def visit_String(self, node) -> TYPE:
		return AST.String
