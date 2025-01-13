import unittest
import builtins
from Scanner import Scanner
from Mparser import Mparser
from TreePrinter import TreePrinter
import AST

from deepdiff import DeepDiff
from pprint import pprint


class ASTTest(unittest.TestCase):
	def setUp(self):
		self.scanner = Scanner()
		self.parser = Mparser()
		self.tree_printer = TreePrinter()

		self.files = []
		for i in range(1, 4):
			with open(f"./test_data/AST_example/example{i}.txt", "r") as file:
				self.files.append(file.read())

		self.expected_output = []
		for i in range(1, 4):
			with open(f"./test_data/AST_expected/expected_output{i}.txt", "r") as file:
				self.expected_output.append(file.read().strip())

	def monkey_patch_print(self, *args, **kwargs):
		self.print_output = []
		self.original_print = builtins.print

		def custom_print(*args, **kwargs):
			self.print_output.append(" ".join(args))

		builtins.print = custom_print

	def test_AST(self):
		def compare_trees(node1, node2):
			if isinstance(node1, AST.Node):
				if not isinstance(node1, node2.__class__):
					print(f"Different classes: {node1.__class__.__name__} != {node2.__class__.__name__}")
					return False

				children_tree1 = vars(node1)
				children_tree2 = vars(node2)

				if children_tree1.keys() != children_tree2.keys():
					print(f"Different children: {children_tree1} != {children_tree2}")

				for key in children_tree1.keys():
					if not compare_trees(children_tree1[key], children_tree2[key]):
						print(f"Different children: {children_tree1} != {children_tree2}")
						return False

				for val1, val2 in zip(children_tree1.values(), children_tree2.values()):
					if not compare_trees(val1, val2):
						return False
			if isinstance(node1, list):
				if not isinstance(node2, list):
					print(f"Different classes: {node1.__class__.__name__} != {node2.__class__.__name__}")
					return False

				if len(node1) != len(node2):
					print(f"Different lengths: {len(node1)} != {len(node2)}")
					return False

				for val1, val2 in zip(node1, node2):
					if not compare_trees(val1, val2):
						return False
			else:
				if node1 != node2:
					print(f"Different values: {node1} != {node2}")
					return False

			return True


		def prepare_example1():
			A = AST.Assignment(AST.Variable("A"), '=', AST.Instruction("zeros", AST.Numeric(5)))
			B = AST.Assignment(AST.Variable("B"), '=', AST.Instruction("ones", AST.Numeric(7)))
			I = AST.Assignment(AST.Variable("I"), '=', AST.Instruction("eye", AST.Numeric(10)))

			E1 = AST.Assignment(
				AST.Variable("E1"),
				'=',
				AST.Vector([
					AST.Vector([AST.Numeric(1), AST.Numeric(2), AST.Numeric(3)]),
					AST.Vector([AST.Numeric(4), AST.Numeric(5), AST.Numeric(6)]),
					AST.Vector([AST.Numeric(7), AST.Numeric(8), AST.Numeric(9)])
				])
			)

			REF = AST.Assignment(
				AST.Reference(AST.Variable('A'), AST.Vector([AST.Numeric(1), AST.Numeric(3)])),
				'=',
				AST.Numeric(0)
			)
			return AST.Program([A, B, I, E1, REF])

		def prepare_example2():
			D1 = AST.Assignment(AST.Variable("D1"), '=', AST.BinaryOperation('.+', AST.Variable("A"), AST.UnaryOperation("'", AST.Variable("B"))))
			D2 = AST.Assignment(AST.Variable("D2"), '-=', AST.BinaryOperation('.-', AST.Variable("A"), AST.UnaryOperation("'", AST.Variable("B"))))
			D3 = AST.Assignment(AST.Variable("D3"), '*=', AST.BinaryOperation('.*', AST.Variable("A"), AST.UnaryOperation("'", AST.Variable("B"))))
			D4 = AST.Assignment(AST.Variable("D4"), '/=', AST.BinaryOperation('./', AST.Variable("A"), AST.UnaryOperation("'", AST.Variable("B"))))

			return AST.Program([D1, D2, D3, D4])

		def prepare_example3():
			N = AST.Assignment(AST.Variable("N"), '=', AST.Numeric(10))
			M = AST.Assignment(AST.Variable("M"), '=', AST.Numeric(10))

			i = AST.Variable("i")
			j = AST.Variable("j")
			k = AST.Variable("k")

			INNER_FOR = AST.Instruction("FOR", (j, AST.Range(AST.Numeric(1), AST.Variable("M")), AST.Instruction("PRINT", (i, j))))
			OUTER_FOR = AST.Instruction("FOR", (i, AST.Range(AST.Numeric(1), AST.Variable("N")),
										  [INNER_FOR]))
			WHILE = AST.Instruction("WHILE", (AST.BinaryOperation('>', k, AST.Numeric(0)),
											  [AST.Ifstatement(AST.BinaryOperation('<', k, AST.Numeric(5)),
																			AST.Assignment(i, '=', AST.Numeric(1)),
															AST.Ifstatement(AST.BinaryOperation('<', k, AST.Numeric(10)),
																			AST.Assignment(i, '=', AST.Numeric(2)),
																			AST.Assignment(i, '=', AST.Numeric(3)))),
														AST.Assignment(k, '-=', AST.Numeric(1))]))

			return AST.Program([N, M, OUTER_FOR, WHILE])

		expected_tree1 = prepare_example1()
		tokenized_text = self.scanner.tokenize(self.files[0])
		tree = self.parser.parse(tokenized_text)

		self.assertTrue(compare_trees(expected_tree1, tree), f"Trees are not equal.\n Expected:{vars(expected_tree1)}\nGot:{vars(tree)}")


		expected_tree2 = prepare_example2()
		tokenized_text = self.scanner.tokenize(self.files[1])
		tree = self.parser.parse(tokenized_text)

		self.assertTrue(compare_trees(expected_tree2, tree), f"Trees are not equal.\n Expected:{vars(expected_tree2)}\nGot:{vars(tree)}")


		expected_tree3 = prepare_example3()
		tokenized_text = self.scanner.tokenize(self.files[2])
		tree = self.parser.parse(tokenized_text)

		self.assertTrue(compare_trees(expected_tree3, tree), f"Trees are not equal.\n Expected:{vars(expected_tree3)}\nGot:{vars(tree)}")

	def test_tree(self):
		self.monkey_patch_print()

		for text, expected in zip(self.files, self.expected_output):
			self.print_output = []

			tokenized_text = self.scanner.tokenize(text)
			tree = self.parser.parse(tokenized_text)
			tree.printTree()

			output_as_string = "\n".join(self.print_output).strip()
			self.assertEqual(expected, output_as_string, f"Expected:\n {expected}\n\n Got:\n {output_as_string}")

		builtins.print = self.original_print




if __name__ == '__main__':
	unittest.main()