import unittest
from pathlib import Path

from newcode.censor import Censor
from newcode.lexer import Lexer
from newcode.errors import Span
from newcode.model import Program, Routine, fraction
from newcode.parser import Parser


ROOT = Path(__file__).parent


class ParserTests(unittest.TestCase):
    def parse_example(self):
        source_path = ROOT / "example" / "victory.think"
        source = source_path.read_text(encoding="utf-8")
        censor = Censor(ROOT / "prohibited_words.json")
        return Parser(Lexer(source, censor).scan()).parse()

    def test_parses_bundled_example_with_routine(self):
        program = self.parse_example()

        self.assertIsInstance(program, Program)
        self.assertEqual(
            sum(isinstance(statement, Routine) for statement in program.statements), 1
        )

    def test_newline_tokens_have_source_spans(self):
        censor = Censor(ROOT / "prohibited_words.json")
        tokens = Lexer("newcode 0.1\n\nthought numberthink count be 0\n", censor).scan()
        newlines = [token for token in tokens if token.kind == "newline"]

        self.assertTrue(newlines)
        self.assertTrue(all(isinstance(token.span, Span) for token in newlines))

    def test_integer_and_decimal_literals_use_exact_fractions(self):
        self.assertEqual(fraction("0").numerator, 0)
        self.assertEqual(fraction("3").denominator, 1)
        self.assertEqual(str(fraction("0.25")), "1/4")


if __name__ == "__main__":
    unittest.main()
