from __future__ import annotations

from pathlib import Path
import unittest

from newcodespeak.errors import LexicalError
from newcodespeak.lexer import lex_source
from newcodespeak.tokens import Token, TokenType


TEST_PATH = Path("program.ncs")


class LexerTests(unittest.TestCase):
    def test_lexes_keywords_names_integers_and_punctuation(self) -> None:
        tokens = lex_source("approve quota; set quota to 12;", TEST_PATH)

        self.assertEqual(
            tokens,
            (
                Token(TokenType.KEYWORD, "approve", 1, 1),
                Token(TokenType.NAME, "quota", 1, 9),
                Token(TokenType.SEMICOLON, ";", 1, 14),
                Token(TokenType.KEYWORD, "set", 1, 16),
                Token(TokenType.NAME, "quota", 1, 20),
                Token(TokenType.KEYWORD, "to", 1, 26),
                Token(TokenType.INTEGER, "12", 1, 29),
                Token(TokenType.SEMICOLON, ";", 1, 31),
                Token(TokenType.EOF, "", 1, 32),
            ),
        )

    def test_core_domain_words_are_keywords(self) -> None:
        tokens = lex_source("fact citizen is good;", TEST_PATH)

        self.assertEqual(
            [token.type for token in tokens[:-1]],
            [
                TokenType.KEYWORD,
                TokenType.KEYWORD,
                TokenType.KEYWORD,
                TokenType.KEYWORD,
                TokenType.SEMICOLON,
            ],
        )

    def test_comments_and_whitespace_are_discarded(self) -> None:
        tokens = lex_source("approve quota; // party\n\tset quota to 1;", TEST_PATH)

        self.assertEqual([token.value for token in tokens], ["approve", "quota", ";", "set", "quota", "to", "1", ";", ""])
        self.assertEqual(tokens[3].line, 2)
        self.assertEqual(tokens[3].column, 2)

    def test_comma_is_a_token(self) -> None:
        tokens = lex_source("approve quota, count;", TEST_PATH)

        self.assertEqual(tokens[2], Token(TokenType.COMMA, ",", 1, 14))

    def test_unexpected_character_has_its_source_location(self) -> None:
        with self.assertRaises(LexicalError) as raised:
            lex_source("approve quota; @", TEST_PATH)

        error = raised.exception
        self.assertEqual(error.character, "@")
        self.assertEqual((error.line, error.column), (1, 16))

    def test_quote_is_not_part_of_the_phase_03_token_set(self) -> None:
        with self.assertRaises(LexicalError) as raised:
            lex_source('approve quota; proclaim "good";', TEST_PATH)

        self.assertEqual(raised.exception.character, '"')


if __name__ == "__main__":
    unittest.main()
