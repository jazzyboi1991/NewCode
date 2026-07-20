"""Error types used by the NewCodeSpeak interpreter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class NewCodeSpeakError(Exception):
    """Base class for expected NewCodeSpeak errors."""


@dataclass(frozen=True)
class ParseError(NewCodeSpeakError):
    path: Path
    line: int
    column: int
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}:{self.column}: parse error: {self.message}"


@dataclass(frozen=True)
class LexicalError(NewCodeSpeakError):
    """Raised when source text cannot be divided into valid tokens."""

    path: Path
    line: int
    column: int
    character: str
    reason: str

    def __str__(self) -> str:
        return (
            f"{self.path}:{self.line}:{self.column}: "
            f"lexical error: {self.reason}: {self.character!r}"
        )


@dataclass
class CensorshipError(NewCodeSpeakError):
    """Raised when source text contains vocabulary the Party did not approve."""

    path: Path
    line: int
    column: int
    word: str
    reason: str

    def __str__(self) -> str:
        return (
            f"{self.path}:{self.line}:{self.column}: "
            f"censorship error: {self.reason}: {self.word!r}"
        )


@dataclass(frozen=True)
class ApprovalDeclarationError(NewCodeSpeakError):
    """Raised when the mandatory first approval declaration is invalid."""

    path: Path
    line: int
    column: int
    reason: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}:{self.column}: censorship error: {self.reason}"
