import unittest
from Scanner import Scanner
from Mparser import Mparser
from NodeVisitor import NodeVisitor
from interpreter.Interpreter import Interpreter


class TestInterpreter(unittest.TestCase):
	def setUp(self):
		self.scanner = Scanner()
		self.parser = Mparser()
		self.interpreter = Interpreter()

	def test_interpreter_fibonacci(self):
		with open('./test_data/interpreter_example/fibonacci.txt', 'r') as file:
			text = file.read()
		tokenized_text = self.scanner.tokenize(text)
		ast = self.parser.parse(tokenized_text)
		ast.accept(self.interpreter)

	def test_interpreter_matrix(self):
		with open('./test_data/interpreter_example/matrix.txt', 'r') as file:
			text = file.read()
		tokenized_text = self.scanner.tokenize(text)
		ast = self.parser.parse(tokenized_text)
		ast.accept(self.interpreter)

	def test_interpreter_pi(self):
		with open('./test_data/interpreter_example/pi.txt', 'r') as file:
			text = file.read()
		tokenized_text = self.scanner.tokenize(text)
		ast = self.parser.parse(tokenized_text)
		ast.accept(self.interpreter)

	def test_interpreter_primes(self):
		with open('./test_data/interpreter_example/primes.txt', 'r') as file:
			text = file.read()
		tokenized_text = self.scanner.tokenize(text)
		ast = self.parser.parse(tokenized_text)
		ast.accept(self.interpreter)

	def test_interpreter_sqrt(self):
		with open('./test_data/interpreter_example/sqrt.txt', 'r') as file:
			text = file.read()
		tokenized_text = self.scanner.tokenize(text)
		ast = self.parser.parse(tokenized_text)
		ast.accept(self.interpreter)

	def test_interpreter_triangle(self):
		with open('./test_data/interpreter_example/triangle.txt', 'r') as file:
			text = file.read()
		tokenized_text = self.scanner.tokenize(text)
		ast = self.parser.parse(tokenized_text)
		ast.accept(self.interpreter)
