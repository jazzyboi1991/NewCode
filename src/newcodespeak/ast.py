"""Immutable abstract-syntax-tree nodes for NewCodeSpeak.

The parser is introduced in Phase 04. These nodes intentionally contain no
evaluation behaviour; the runtime will interpret them in a later phase.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Approval:
    """The mandatory opening declaration of approved user names."""

    names: tuple[str, ...]


@dataclass(frozen=True)
class Program:
    """A complete source program."""

    approval: Approval
    statements: tuple[Statement, ...]


class Statement:
    """Base class for all statement nodes."""


class Expression:
    """Base class for values and arithmetic expressions."""


class Condition:
    """Base class for boolean conditions."""


@dataclass(frozen=True)
class NameReference(Expression):
    """A reference to an approved name."""

    name: str


@dataclass(frozen=True)
class IntegerLiteral(Expression):
    """A non-negative integer written in source code."""

    value: int


@dataclass(frozen=True)
class StatusLiteral(Expression):
    """An approved status such as ``good`` or ``true``."""

    value: str


@dataclass(frozen=True)
class BinaryExpression(Expression):
    """An arithmetic expression joined by ``plus`` or ``minus``."""

    left: Expression
    operator: str
    right: Expression


@dataclass(frozen=True)
class Proposition(Condition):
    """A Party-record proposition, represented by one or more approved words."""

    words: tuple[str, ...]


@dataclass(frozen=True)
class Comparison(Condition):
    """A numeric comparison using ``above`` or ``below``."""

    left: Expression
    operator: str
    right: Expression


@dataclass(frozen=True)
class LogicalCondition(Condition):
    """A condition joined by ``and`` or ``or``."""

    left: Condition
    operator: str
    right: Condition


@dataclass(frozen=True)
class Assignment(Statement):
    """A ``set name to expression`` statement."""

    name: str
    expression: Expression


@dataclass(frozen=True)
class Fact(Statement):
    """A current-record assertion with an approved status."""

    proposition: Proposition
    status: StatusLiteral


@dataclass(frozen=True)
class Rule(Statement):
    """A conclusion that becomes true when its premise is true."""

    conclusion: Proposition
    premise: Proposition


@dataclass(frozen=True)
class Query(Statement):
    """A request for the current status of a proposition."""

    proposition: Proposition


@dataclass(frozen=True)
class Proclaim(Statement):
    """Output consisting solely of approved words."""

    words: tuple[str, ...]


@dataclass(frozen=True)
class Conditional(Statement):
    """An ``if`` block with an optional ``else`` branch."""

    condition: Condition
    then_branch: tuple[Statement, ...]
    else_branch: tuple[Statement, ...] | None


@dataclass(frozen=True)
class Repetition(Statement):
    """A ``repeat while`` block."""

    condition: Condition
    body: tuple[Statement, ...]

