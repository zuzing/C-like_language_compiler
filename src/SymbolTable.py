class Symbol(object):
	def __init__(self, name):
		self.name = name

	def __eq__(self, other):
		return self.name == other.id

	def __hash__(self):
		return hash(self.name)



TYPE = object # keyword to annotate type


class VariableSymbol(Symbol):
	def __init__(self, name: str, type_):
		super().__init__(name)
		self.type = type_


class VectorType(TYPE):
	def __init__(self, shape: tuple):
		self.shape = shape

	def shape(self):
		return self.shape

	def __eq__(self, other):
		if not isinstance(other, VectorType):
			return False
		return self.shape == other.shape

	def __hash__(self):
		return hash(self.shape)

	def __repr__(self):
		return f"VectorType{self.shape}"


class SymbolTable(object):

	def __init__(self, parent_scope: 'SymbolTable' or None, name: str):
		self.symbols: dict = {}
		self.parent_scope = parent_scope
		self.name = name

	def put(self, symbol: Symbol):
		self.symbols[symbol.name] = symbol

	def get(self, name: str):
		symbol = self.symbols.get(name)
		if symbol is not None:
			return symbol
		elif self.parent_scope is not None:
			return self.parent_scope.get(name)
		return None
