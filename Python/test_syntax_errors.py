import unittest
from pathlib import Path

from newcode.censor import Censor
from newcode.errors import NewcodeError
from newcode.lexer import Lexer
from newcode.parser import Parser


ROOT = Path(__file__).parent


def parse(source):
    censor = Censor(ROOT / "prohibited_words.json")
    return Parser(Lexer(source, censor).scan()).parse()


class SyntaxErrorTests(unittest.TestCase):
    def assert_error(self, source, code):
        with self.assertRaises(NewcodeError) as caught:
            parse(source)
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_unsupported_language_version_is_rejected(self):
        self.assert_error("newcode 0.9\n", "THINKLOGIC ERROR")

    def test_newcode_04_header_is_accepted(self):
        program = parse("newcode 0.4\nspeak 1\n")
        self.assertEqual(len(program.statements), 1)

    def test_newcode_05_header_is_accepted(self):
        program = parse("newcode 0.5\nspeak 1\n")
        self.assertEqual(len(program.statements), 1)

    def test_unclosed_verify_is_rejected(self):
        self.assert_error("newcode 0.2\nverify good\nspeak 1\n", "THINKLOGIC ERROR")

    def test_unclosed_string_is_rejected(self):
        self.assert_error('newcode 0.2\nspeak "abc\n', "THINKLOGIC ERROR")

    def test_invalid_string_escape_is_rejected(self):
        self.assert_error('newcode 0.2\nspeak "abc\\q"\n', "THINKLOGIC ERROR")

    def test_non_ascii_code_outside_comments_is_rejected(self):
        self.assert_error("newcode 0.2\nspeak 안녕\n", "THINKLOGIC ERROR")

    def test_reserved_word_cannot_be_variable_name(self):
        self.assert_error("newcode 0.2\nthought numberthink verify be 1\n", "THINKLOGIC ERROR")

    def test_invalid_decimal_literal_is_rejected(self):
        self.assert_error("newcode 0.2\nspeak 1.\n", "THINKLOGIC ERROR")

    def test_module_path_must_be_a_string(self):
        self.assert_error("newcode 0.2\nuse mathgood from 1\n", "MODULECRIME")

    def test_othercrime_requires_a_single_code(self):
        self.assert_error(
            'newcode 0.2\ntrythink\n    speak 1 divide 0\nothercrime MATHCRIME EXTRA\n    speak "abc"\nendtrythink\n',
            "THINKLOGIC ERROR",
        )

    def test_error_span_points_to_offending_line_and_column(self):
        error = self.assert_error("newcode 0.2\nspeak 1 2\n", "THINKLOGIC ERROR")
        self.assertEqual(error.span.line, 2)
        self.assertEqual(error.span.column, 9)


if __name__ == "__main__":
    unittest.main()
