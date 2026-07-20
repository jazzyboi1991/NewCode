"""Convert censored NewCodeSpeak source text into positioned tokens."""

from __future__ import annotations

from pathlib import Path

from .errors import LexicalError
from .tokens import Token, TokenType
from .vocabulary import CORE_VOCABULARY


PUNCTUATION = {
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
}


def lex_source(source: str, path: Path) -> tuple[Token, ...]:
    """Tokenize one already-censored source file.

    Whitespace and ``//`` comments are deliberately discarded. The censor has
    already scanned their contents, so discarding comments here does not make
    them an escape route around the vocabulary policy.
    """
    tokens: list[Token] = []
    offset = 0
    line = 1
    column = 1

    while offset < len(source):
        character = source[offset]

        if character in " \t\r":
            offset += 1
            column += 1
            continue

        if character == "\n":
            offset += 1
            line += 1
            column = 1
            continue

        if source.startswith("//", offset):
            while offset < len(source) and source[offset] != "\n":
                offset += 1
                column += 1
            continue

        punctuation_type = PUNCTUATION.get(character)
        if punctuation_type is not None:
            tokens.append(Token(punctuation_type, character, line, column))
            offset += 1
            column += 1
            continue

        if "0" <= character <= "9":
            start = offset
            start_column = column
            while offset < len(source) and "0" <= source[offset] <= "9":
                offset += 1
                column += 1
            tokens.append(Token(TokenType.INTEGER, source[start:offset], line, start_column))
            continue

        if "a" <= character <= "z" or character == "_":
            start = offset
            start_column = column
            while offset < len(source):
                candidate = source[offset]
                if not ("a" <= candidate <= "z" or candidate == "_"):
                    break
                offset += 1
                column += 1

            word = source[start:offset]
            token_type = TokenType.KEYWORD if word in CORE_VOCABULARY else TokenType.NAME
            tokens.append(Token(token_type, word, line, start_column))
            continue

        raise LexicalError(
            path=path,
            line=line,
            column=column,
            character=character,
            reason="unexpected character",
        )

    tokens.append(Token(TokenType.EOF, "", line, column))
    return tuple(tokens)

