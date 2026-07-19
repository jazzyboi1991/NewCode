"""The Party-approved vocabulary and user-name policy"""

from __future__ import annotations

import re
from collections.abc import Iterable

CORE_VOCABULARY = frozenset(
    {
        "approve",
        "set",
        "to",
        "if",
        "then",
        "else",
        "repeat",
        "while",
        "end",
        "fact",
        "rule",
        "when",
        "query",
        "proclaim",
        "is",
        "above",
        "below",
        "plus",
        "minus",
        "and",
        "or",
        "good",
        "ungood",
        "plusgood",
        "doubleplusgood",
        "party",
        "citizen",
        "work",
        "obey",
        "ownlife",
        "oldthink",
        "crimethink",
        "true",
        "false",
    }
)

NAME_PATTERN = re.compile(r"[a-z_]+\Z")


def is_valid_user_name(name: str) -> bool:
    """Return whether *name* follows the NewCodeSpeak user-name rule."""
    return NAME_PATTERN.fullmatch(name) is not None


def approved_vocabulary(user_names: Iterable[str]) -> frozenset[str]:
    """Combine the permanently approved words with approved user names."""
    return CORE_VOCABULARY | frozenset(user_names)
