import unittest
from Scanner import Scanner


class ScannerTest(unittest.TestCase):
	def setUp(self):
		self.scanner = Scanner()

		with open("./test_data/scanner_example/example.txt", "r") as file:
			self.text = file.read()

	def test_tokenize(self):

		with open("./test_data/scanner_expected/expected_output.txt", "r") as file:
			expected_output = file.read().splitlines()

		for token, expected_token in zip(self.scanner.tokenize(self.text), expected_output):
			self.assertEqual(expected_token, str(token.type), f"Unexpected token: {token}")


if __name__ == '__main__':
	unittest.main()