"""Error types used by the NewCodeSpeak interpreter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class NewCodeSpeakError(Exception):
    """Base class for expected NewCodeSpeak errors."""


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
