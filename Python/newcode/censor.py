import json
import re
from pathlib import Path

from .errors import Span, fail


class Censor:
    def __init__(self, path: Path):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise RuntimeError(f"cannot read official lexicon {path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid official lexicon {path}: {exc}") from exc

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

    def check(self, text: str, identifier: bool, span: Span) -> None:
        actual = self.normalize(text, identifier)

        def found(value: str) -> bool:
            needle = self.normalize(value, identifier)

            return bool(needle) and (
                needle in actual
                if identifier
                else bool(re.search(rf"(?<![a-z]){re.escape(needle)}(?![a-z])", actual))
            )

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
