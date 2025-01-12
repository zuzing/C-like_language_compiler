import unittest
from Scanner import Scanner
from Mparser import Mparser


class ParserTest(unittest.TestCase):
	def setUp(self):
		self.scanner = Scanner()
		self.parser = Mparser()

		self.files = []
		for i in range(1, 4):
			with open(f"./test_data/parser_example/example{i}.txt", "r") as file:
				self.files.append(file.read())

		debugfile = f"./parser_debug/debug.out"
		self.parser.debug(debugfile)

	def test_parse(self):
		for text in self.files:
			tokenized_text = self.scanner.tokenize(text)
			self.parser.parse(tokenized_text)


if __name__ == '__main__':
	unittest.main()