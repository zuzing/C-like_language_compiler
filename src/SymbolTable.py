class Symbol(object):
	def __init__(self, name):
		self.name = name


UNKNOWN = None  # keyword to annotate unknown type or value
TYPE = object # keyword to annotate type


class VariableSymbol(Symbol):
	def __init__(self, name: str, type_):
		super().__init__(name)
		self.type = type_

class VectorVariableSymbol(VariableSymbol):
	def __init__(self, name: str, type_: TYPE, shape: tuple):
		super().__init__(name, type_)
		self.shape = shape

	def shape(self):
		return self.shape


class SymbolTable(object):

	def __init__(self, parent_scope: 'SymbolTable' | None, name: str):
		self.symbols: dict = {}
		self.parent_scope = parent_scope
		self.name = name

	def put(self, symbol: Symbol):
		self.symbols[symbol.name] = symbol

	def get(self, name: str):
		symbol = self.symbols[name]
		if symbol is not None:
			return symbol
		elif self.parent_scope is not None:
			return self.parent_scope.get(name)
		raise ValueError(f"Symbol {name} not in symbol table")
