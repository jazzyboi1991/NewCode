from dataclasses import dataclass
from fractions import Fraction

from newcode.errors import Span


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    span: Span


@dataclass
class Expr:
    span: Span


@dataclass
class Number(Expr):
    value: Fraction


@dataclass
class Word(Expr):
    value: str


@dataclass
class Good(Expr):
    value: bool


@dataclass
class Name(Expr):
    value: str


@dataclass
class Input(Expr):
    type_name: str


@dataclass
class Call(Expr):
    name: str
    args: list[Expr]


@dataclass
class Unary(Expr):
    op: str
    value: Expr


@dataclass
class Binary(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class Stmt:
    span: Span


@dataclass
class Declare(Stmt):
    type_name: str
    name: str
    value: Expr


@dataclass
class Assign(Stmt):
    name: str
    value: Expr


@dataclass
class Speak(Stmt):
    items: list[tuple[Expr, Expr | None]]
    number_only: bool


@dataclass
class Verify(Stmt):
    condition: Expr
    yes: list[Stmt]
    no: list[Stmt]


@dataclass
class Repeat(Stmt):
    condition: Expr
    body: list[Stmt]


@dataclass
class Next(Stmt):
    pass


@dataclass
class Stop(Stmt):
    pass


@dataclass
class Report(Stmt):
    value: Expr


@dataclass
class Routine(Stmt):
    return_type: str
    name: str
    params: list[tuple[str, str, Span]]
    body: list[Stmt]


@dataclass
class NativeRoutine(Stmt):
    """A standard-library routine implemented by the reference runtime."""

    return_type: str
    name: str
    params: list[tuple[str, str, Span]]
    handler: object


@dataclass
class CallStatement(Stmt):
    call: Call


@dataclass
class Get(Expr):
    target: Expr
    mode: str
    key: Expr


@dataclass
class Size(Expr):
    target: Expr


@dataclass
class Slice(Expr):
    target: Expr
    start: Expr
    stop: Expr


@dataclass
class LiteralValue(Expr):
    value: object


@dataclass
class Composite(Expr):
    type_name: str
    items: list


@dataclass
class RecordConstruct(Expr):
    type_name: str
    fields: list[tuple[str, Expr]]


@dataclass
class RecordType(Stmt):
    name: str
    fields: list[tuple[str, str, Span]]


@dataclass
class Change(Stmt):
    target: Expr
    mode: str
    key: Expr
    value: Expr


@dataclass
class Add(Stmt):
    value: Expr
    target: Expr


@dataclass
class Remove(Stmt):
    target: Expr
    mode: str
    key: Expr


@dataclass
class Foreach(Stmt):
    names: list[str]
    target: Expr
    body: list


@dataclass
class Try(Stmt):
    body: list
    handlers: list


@dataclass
class OtherCrime:
    span: Span
    code: str | None
    body: list


@dataclass
class FileRead(Expr):
    path: Expr


@dataclass
class FileWrite(Stmt):
    action: str
    path: Expr
    value: Expr


@dataclass
class Lines(Expr):
    target: Expr


@dataclass
class JoinLines(Expr):
    target: Expr


@dataclass
class StringOp(Expr):
    name: str
    args: list[Expr]


@dataclass
class ModuleUse(Stmt):
    name: str
    path: str


@dataclass
class TestThink(Stmt):
    name: str
    body: list


@dataclass
class Program:
    statements: list[Stmt]


def fraction(text: str) -> Fraction:
    whole, dot, tail = text.partition(".")

    if not dot:
        return Fraction(int(whole), 1)

    return Fraction(int(whole + tail), 10 ** len(tail))
