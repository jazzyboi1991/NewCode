"""Vocabulary censorship performed before lexing and parsing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .errors import ApprovalDeclarationError, CensorshipError
from .vocabulary import CORE_VOCABULARY, approved_vocabulary, is_valid_user_name

APPROVED_PATTERN = re.compile(r"\A\s*approve\s+(?P<names>[^;]*);")
WORD_PATTERN = re.compile(r"(?<!\w)[\w-]+(?!\w)", re.UNICODE)


@dataclass(frozen=True)
class CensorResult:
    """The approved user names extracted from one source file."""

    user_names: frozenset[str]


def line_and_column(source: str, offset: int) -> tuple[int, int]:
    """Convert a zero-based character offset into one-based source coordinates."""
    line = source.count("\n", 0, offset) + 1
    previous_newline = source.rfind("\n", 0, offset)
    column = offset - previous_newline
    return line, column


def parse_approval_declaration(source: str, path: Path) -> frozenset[str]:
    """Read and validate the required first ``approve`` declaration"""
    match = APPROVED_PATTERN.match(source)
    if match is None:
        raise ApprovalDeclarationError(
            path=path,
            line=1,
            column=1,
            reason="a program must begin with an approve declaration",
        )

    raw_names = match.group("names")
    declaration_offset = match.start("names")
    pieces = raw_names.split(",")
    names: list[str] = []

    for piece in pieces:
        name = piece.strip()
        name_offset = (
            declaration_offset + piece.find(name) if name else declaration_offset
        )
        line, column = line_and_column(source, name_offset)

        if not name:
            raise ApprovalDeclarationError(
                path=path,
                line=line,
                column=column,
                reason="an approve declaration cannot contain an empty name",
            )
        if not is_valid_user_name(name):
            raise ApprovalDeclarationError(
                path=path,
                line=line,
                column=column,
                reason=f"invalid approved name {name!r}; use lowercase and underscores only",
            )
        if name in CORE_VOCABULARY:
            raise ApprovalDeclarationError(
                path=path,
                line=line,
                column=column,
                reason=f"{name!r} is already part of the core vocabulary",
            )
        if name in names:
            raise ApprovalDeclarationError(
                path=path,
                line=line,
                column=column,
                reason=f"{name!r} is approved more than once",
            )
        names.append(name)
    return frozenset(names)


def censor_source(source: str, path: Path) -> CensorResult:
    """Reject every non-numeric word outside the approved vocabulary.

    The scan deliberately includes comments and quoted text. Parsing is not
    required for that policy: any unapproved word is rejected before parsing.
    """
    user_names = parse_approval_declaration(source, path)
    allowed_words = approved_vocabulary(user_names)

    for match in WORD_PATTERN.finditer(source):
        word = match.group()
        if word.isdecimal():
            continue
        if word not in allowed_words:
            line, column = line_and_column(source, match.start())
            raise CensorshipError(
                path=path,
                line=line,
                column=column,
                word=word,
                reason="word is not in the approved vocabulary",
            )

    return CensorResult(user_names=user_names)
