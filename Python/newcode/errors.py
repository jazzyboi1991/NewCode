from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Span:
    line: int
    column: int


class NewcodeError(Exception):
    def __init__(self, code: str, message: str, span: Span):
        self.code, self.message, self.span = code, message, span
        super().__init__(message)

    def display(self, filename: str, source: str) -> str:
        result = f"{filename}: line {self.span.line}, column {self.span.column}: {self.code}: {self.message}"
        lines = source.splitlines()

        if 1 <= self.span.line <= len(lines):
            result += (
                "\n"
                + lines[self.span.line - 1]
                + "\n"
                + " " * (self.span.column - 1)
                + "^"
            )
        return result

def fail(code: str, message: str, span: Span) -> NewcodeError:
    return NewcodeError(code, message, span)
