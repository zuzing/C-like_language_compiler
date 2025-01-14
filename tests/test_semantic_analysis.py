import unittest
from Scanner import Scanner
from Mparser import Mparser
from NodeVisitor import NodeVisitor
import warnings


class TestSemanticAnalysis(unittest.TestCase):
	def setUp(self):
		self.scanner = Scanner()
		self.parser = Mparser()

		self.trees = []
		for i in range(1, 4):
			with open(f"./test_data/semantic_analysis_example/example{i}.txt", "r") as file:
				text = file.read()
			tokenized_text = self.scanner.tokenize(text)
			self.trees.append(self.parser.parse(tokenized_text))

		self.node_visitor = NodeVisitor()

		warnings.simplefilter('always', UserWarning)

	def test_flow_control(self):
		self.node_visitor.visit(self.trees[0]) # TODO: delete this

		expected_reasons = ["continue", "return", "break", "return", "return"]
		with warnings.catch_warnings(record=True) as w:
			self.node_visitor.visit(self.trees[0])
			self.assertEqual(5, len(w))
			for i in range(5):
				assert expected_reasons[i] in str(w[i].message)

	def test_matrix_creation(self):
		self.node_visitor.visit(self.trees[1])

		with warnings.catch_warnings(record=True) as w:
			self.node_visitor.visit(self.trees[1])
			self.assertEqual(1, len(w))
			assert "Vector dimensions do not match" in str(w[0].message)

	def test_binary_operations(self):
		self.node_visitor.visit(self.trees[2])

		with warnings.catch_warnings(record=True) as w:
			self.node_visitor.visit(self.trees[2])
			self.assertEqual(6, len(w))


if __name__ == '__main__':
	unittest.main()
