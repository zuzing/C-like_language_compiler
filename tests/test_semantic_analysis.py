import unittest
from Scanner import Scanner
from Mparser import Mparser
from NodeVisitor import NodeVisitor


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

	def test_semantic_analysis(self):
		for tree in self.trees:
			self.node_visitor.visit(tree)

	def test_example1(self):
		self.node_visitor.visit(self.trees[0])

	def test_example2(self):
		self.node_visitor.visit(self.trees[1])

	def test_example3(self):
		self.node_visitor.visit(self.trees[2])


if __name__ == '__main__':
	unittest.main()
