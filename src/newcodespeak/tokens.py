"""Token definitions for the NewCodeSpeak lexer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """The finite set of tokens understood before parsing."""

    KEYWORD = auto()
    NAME = auto()
    INTEGER = auto()
    SEMICOLON = auto()
    COMMA = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    """One lexeme together with its one-based source location."""

    type: TokenType
    value: str
    line: int
    column: int

