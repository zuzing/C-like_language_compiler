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

	def visit_Assignment(self, node):
		TRANSLATION_TABLE = {
			'+=': '+',
			'-=': '-',
			'*=': '*',
			'/=': '/',
		}

		var_name = node.id.id
		var_symbol = self.symbol_table.get(var_name)
		if node.op == '=':
			type_ = self.visit(node.expr)
			if var_symbol is None:
				self.symbol_table.put(VariableSymbol(name=var_name, type_=type_))
			else:
				if var_symbol.type != type_:
					print(f"Type mismatch: {var_symbol.type} != {type_} for {var_name}")
		else:
			if var_symbol is None:
				print(f"Undefined variable: {var_name}")
			type_ = self.visit(AST.BinaryOperation(TRANSLATION_TABLE[node.op], AST.Variable(var_name), node.expr))
			self.symbol_table.get(var_name).type = type_

	def visit_Variable(self, node):
		if self.symbol_table.get(node.id) is None:
			raise Exception(f"Undefined variable: {node.id}")
		return self.symbol_table.get(node.id).type

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

		left_type = self.visit(node.left)
		right_type = self.visit(node.right)

		# if isinstance(node.left, AST.Variable):
		#     left_type = self.symbol_table.get(node.left.name).type
		# else:
		#     left_type = node.left.__class__.__name__
		#
		# if isinstance(node.right, AST.Variable):
		#     right_type = self.symbol_table.get(node.right.name).type
		# else:
		#     right_type = node.right.__class__.__name__

		operation = (node.op, left_type, right_type)
		if operation in ALLOWED_OPERATIONS.keys():
			if operation in MATRIX_OPERATIONS.keys():
				return vector_shapes(node.op, node.left, node.right)
			return ALLOWED_OPERATIONS[operation]
		else:
			print(f"Unsupported operation: {left_type} {node.op} {right_type} for {node.left} {node.op} {node.right}")

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
			print(
				f"Unsupported operation: {operand_type} {node.operand.__class__.__name__} for {node.op} {node.operand}")

		if ALLOWED_OPERATIONS[operation] is VectorType:
			if isinstance(node.operand, AST.Variable):
				return VectorType(shape=self.symbol_table.get(node.operand.name).type.shape())
			else:
				return VectorType(shape=node.operand.shape())
		else:
			return ALLOWED_OPERATIONS[operation]

	def visit_Instruction(self, node) -> TYPE or None:
		ALLOWED_ARGUMENT_TYPES = {
			'EYE': [int],
			'ZEROS': [int],
			'ONES': [int],
		}
		VECTOR_CREATION_INSTRUCTIONS = {
			'EYE': lambda x: VectorType(shape=(x, x)),
			'ZEROS': lambda x: VectorType(shape=(x, x)),
			'ONES': lambda x: VectorType(shape=(x, x)),
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
				print(f"Flow control instruction outside loop: {node.instruction}")
			self.current_loop -= 1
			self.symbol_table = self.symbol_table.parent_scope

		if node.instruction in ALLOWED_ARGUMENT_TYPES.keys():
			arg_types = [arg.__class__ for arg in node.args]
			if arg_types != ALLOWED_ARGUMENT_TYPES[node.instruction]:
				print(f"Invalid arguments for instruction {node.instruction}")

			if node.instruction in VECTOR_CREATION_INSTRUCTIONS.keys():
				return VECTOR_CREATION_INSTRUCTIONS[node.instruction](*node.args)

		if node.instruction in LOOP_INSTRUCTIONS:
			self.symbol_table = SymbolTable(parent_scope=self.symbol_table, name=node.instruction)
			self.current_loop += 1
			self.visit(node.args[0])
			self.symbol_table = self.symbol_table.parent_scope
			self.current_loop -= 1

		if hasattr(node, 'args'):
			if isinstance(node.args, tuple):
				for arg in node.args:
					self.visit(arg)
			else:
				self.visit(node.args)

	def visit_Reference(self, node) -> TYPE:
		self.visit(node.id)
		self.visit(node.index)

		id = self.symbol_table.get(node.id.id)

		if id.type is VectorType:
			if len(node.index) > len(id.shape):
				print(f"Index out of bounds: {node.id} {node.index} in {node}")
			for i in range(len(id.shape)):  # check if indexes are integers and within bounds
				if not isinstance(node.index[i], int):
					print(f"Indexes must be an integers: {node.id} {node.index} in {node}")
				if node.index[i] < 0 or node.index[i] >= id.shape[i]:
					print(f"Index out of bounds: {node.id} {node.index} in {node}")

			if len(node.index) == len(id.shape):
				return AST.Numeric
			else:
				return VectorType(shape=id.shape[len(node.index):])
		else:
			print(f"Variable is not a vector: {node.id} in {node}")

	def visit_Variable(self, node) -> TYPE:
		return self.symbol_table.get(node.id).type

	def visit_Vector(self, node) -> TYPE:
		return VectorType(shape=(node.shape()))

	def visit_Numeric(self, node) -> TYPE:
		return AST.Numeric

	def visit_String(self, node) -> TYPE:
		return AST.String

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
