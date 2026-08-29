import json
import re
from copy import deepcopy
from pathlib import Path
from importlib import resources

from newcode.errors import Span, fail


class Censor:
    def __init__(self, path: Path):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise RuntimeError(f"cannot read official lexicon {path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid official lexicon {path}: {exc}") from exc

        self.schema_version = str(raw.get("schema_version", ""))
        self.language_version = str(raw.get("language_version", ""))
        self.normalization = deepcopy(raw.get("normalization", {}))

        rules = raw.get("replacement_rules", [])

        self.replacements = (
            list(rules.items())
            if isinstance(rules, dict)
            else [
                (str(item.get("term", "")), str(item.get("replacement", "")))
                for item in rules
                if isinstance(item, dict)
            ]
        )
        self.terms = [
            self._entry(item, "term") for item in raw.get("prohibited_terms", [])
        ]
        self.phrases = [
            self._entry(item, "phrase") for item in raw.get("prohibited_phrases", [])
        ]
        self.replacements = [(a, b) for a, b in self.replacements if a]
        self.terms, self.phrases = (
            [x for x in self.terms if x],
            [x for x in self.phrases if x],
        )

    @classmethod
    def official(cls):
        """Load the bundled official lexicon from an installed package."""
        return cls(resources.files("newcode").joinpath("prohibited_words.json"))

    def policy_summary(self):
        """Return public policy metadata without exposing lexicon entries."""
        normalization = self.normalization
        substitutions = normalization.get("leet_substitutions", {})
        return {
            "schema_version": self.schema_version,
            "language_version": self.language_version,
            "counts": {
                "replacement_rules": len(self.replacements),
                "prohibited_terms": len(self.terms),
                "prohibited_phrases": len(self.phrases),
            },
            "checkpoints": [
                "identifiers and source strings",
                "input values",
                "join and replacement results",
                "output and file writes",
            ],
            "normalization": {
                "case_sensitive": bool(normalization.get("case_sensitive", False)),
                "collapse_whitespace": bool(normalization.get("collapse_whitespace", True)),
                "remove_separators": list(normalization.get("remove_separators", [])),
                "leet_substitutions": dict(substitutions),
            },
            "lexicon_mutable": False,
        }

    @staticmethod
    def _entry(item, key):
        return str(item.get(key, "")) if isinstance(item, dict) else str(item)

    @staticmethod
    def normalize(text: str, identifier: bool) -> str:
        table = str.maketrans(
            {
                "0": "o",
                "1": "i",
                "3": "e",
                "4": "a",
                "@": "a",
                "5": "s",
                "$": "s",
                "7": "t",
            }
        )
        text = text.lower().translate(table)
        if identifier:
            return "".join(ch for ch in text if ch.isascii() and ch.isalnum())

        return re.sub(
            r"\s+",
            " ",
            "".join(ch if ch.isascii() and ch.isalnum() else " " for ch in text),
        ).strip()

    @staticmethod
    def compact(text: str) -> str:
        """Return the separator-free form used to reject visual policy bypasses."""
        table = str.maketrans(
            {
                "0": "o",
                "1": "i",
                "3": "e",
                "4": "a",
                "5": "s",
                "7": "t",
                "@": "a",
                "$": "s",
            }
        )
        return "".join(
            ch
            for ch in text.lower().translate(table)
            if ch.isascii() and ch.isalnum()
        )

    def check(self, text: str, identifier: bool, span: Span) -> None:
        actual = self.normalize(text, identifier)
        compact_actual = self.compact(text)

        def found(value: str) -> bool:
            needle = self.normalize(value, identifier)

            if not needle:
                return False
            regular_match = (
                needle in actual
                if identifier
                else bool(re.search(rf"(?<![a-z]){re.escape(needle)}(?![a-z])", actual))
            )
            compact_needle = self.compact(value)
            return regular_match or bool(compact_needle and compact_needle in compact_actual)

        for phrase in sorted(self.phrases, key=len, reverse=True):
            if found(phrase):
                raise fail(
                    "WORDCRIME",
                    f"prohibited phrase '{phrase}'. No approved replacement.",
                    span,
                )
        for term in sorted(self.terms, key=len, reverse=True):
            if found(term):
                raise fail(
                    "WORDCRIME",
                    f"prohibited word '{term}', No approved replacement.",
                    span,
                )
        for old, replacement in sorted(
            self.replacements, key=lambda item: len(item[0]), reverse=True
        ):
            if found(old):
                raise fail(
                    "WORDCRIME",
                    f"oldspeak '{old}'. Use '{replacement}'.",
                    span,
                )
