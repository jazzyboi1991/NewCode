import re
from dataclasses import dataclass

from newcode import MAX_STEPS
from newcode.errors import fail
from newcode.model import (
    Assign,
    Call,
    CallStatement,
    Declare,
    Good,
    Input,
    Name,
    Next,
    Number,
    Repeat,
    Report,
    Routine,
    Speak,
    Stop,
    Unary,
    Verify,
    Word,
    fraction,
)


@dataclass
class Variable:
    type_name: str
    value: object


class ContinueFlow(Exception):
    pass


class StopFlow(Exception):
    pass


class ReturnFlow(Exception):
    def __init__(self, value):
        self.value = value


class Runtime:
    def __init__(self, censor, routines):
        self.censor, self.routines = censor, routines
        self.global_scopes, self.local_scopes = [dict()], []
        self.steps = self.loop_depth = 0

    def execute(self, program):
        self._block([x for x in program.statements if not isinstance(x, Routine)])

    def _in_function(self):
        return bool(self.local_scopes)

    def _scopes(self):
        return self.local_scopes if self._in_function() else self.global_scopes

    def _tick(self, span):
        self.steps += 1

        if self.steps > MAX_STEPS:
            raise fail("WORKLIMIT", "execution limit exceeded", span)

    def _lookup(self, name, span):
        for scope in reversed(self._scopes()):
            if name in scope:
                return scope[name]

        message = (
            f"global variable access denied or undeclared name '{name}'"
            if self._in_function()
            else f"undeclared name '{name}'"
        )

        raise fail("CRIMESTOP", message, span)

    def _nested(self, statements):
        self._scopes().append({})

        try:
            self._block(statements)
        finally:
            self._scopes().pop()

    def _value(self, expr):
        self._tick(expr.span)

        if isinstance(expr, Number):
            return expr.value

        if isinstance(expr, Word):
            return expr.value

        if isinstance(expr, Good):
            return expr.value

        if isinstance(expr, Name):
            return self._lookup(expr.value, expr.span).value

        if isinstance(expr, Input):
            return self._input(expr)

        if isinstance(expr, Unary):
            return (
                not self._value(expr.value)
                if expr.op == "un"
                else -self._value(expr.value)
            )

        if isinstance(expr, Call):
            return self._call(expr)

        left, right = self._value(expr.left), self._value(expr.right)

        if expr.op == "join":
            value = left + right
            self.censor.check(value, False, expr.span)

            return value

        if expr.op == "plus":
            return left + right

        if expr.op == "minus":
            return left - right

        if expr.op == "times":
            return left * right

        if expr.op == "divide":
            if right == 0:
                raise fail("MATHCRIME", "division by zero", expr.span)

            return left / right

        if expr.op == "more":
            return left > right

        if expr.op == "less":
            return left < right

        if expr.op == "same":
            return left == right

        if expr.op == "both":
            return left and right

        return left or right

    def _input(self, expr):
        raw = input()

        if expr.type_name == "wordthink":
            if not raw.isascii():
                raise fail("INPUTCRIME", "non-ASCII input", expr.span)

            self.censor.check(raw, False, expr.span)

            return raw

        raw = raw.strip()
        raw = "-" + raw[6:] if raw.startswith("minus ") else raw

        if not re.fullmatch(r"-?\d+(?:\.\d+)?", raw):
            raise fail("INPUTCRIME", "invalid number", expr.span)

        return -fraction(raw[1:]) if raw.startswith("-") else fraction(raw)

    def _call(self, call):
        routine = self.routines[call.name]
        values = [self._value(arg) for arg in call.args]

        scope = {
            name: Variable(type_name, value)
            for value, (type_name, name, _) in zip(values, routine.params)
        }

        saved_scopes, self.local_scopes = self.local_scopes, [scope]
        saved_depth, self.loop_depth = self.loop_depth, 0

        try:
            try:
                self._block(routine.body)
            except ReturnFlow as flow:
                return flow.value

            if routine.return_type == "silencethink":
                return None

            raise fail(
                "THINKLOGIC ERROR",
                f"routine '{routine.name}' did not report a value",
                call.span,
            )
        finally:
            self.local_scopes, self.loop_depth = saved_scopes, saved_depth

    def _block(self, statements):
        for statement in statements:
            self._statement(statement)

    def _statement(self, statement):
        self._tick(statement.span)

        if isinstance(statement, Declare):
            self._scopes()[-1][statement.name] = Variable(
                statement.type_name, self._value(statement.value)
            )

        elif isinstance(statement, Assign):
            self._lookup(statement.name, statement.span).value = self._value(
                statement.value
            )

        elif isinstance(statement, Speak):
            output = ""

            for value, digits in statement.items:
                result = self._value(value)

                if digits is None:
                    output += display(result)
                else:
                    precision = self._value(digits)

                    if precision.denominator != 1 or precision < 0:
                        raise fail(
                            "MATHCRIME",
                            "precision must be a non-negative integer",
                            digits.span,
                        )

                    output += display(result, int(precision))

            print(output)

        elif isinstance(statement, Verify):
            self._nested(
                statement.yes if self._value(statement.condition) else statement.no
            )

        elif isinstance(statement, Repeat):
            while self._value(statement.condition):
                self.loop_depth += 1

                try:
                    try:
                        self._nested(statement.body)
                    except ContinueFlow:
                        continue
                    except StopFlow:
                        break
                finally:
                    self.loop_depth -= 1

        elif isinstance(statement, Next):
            raise ContinueFlow()

        elif isinstance(statement, Stop):
            raise StopFlow()

        elif isinstance(statement, Report):
            raise ReturnFlow(self._value(statement.value))

        elif isinstance(statement, CallStatement):
            self._value(statement.call)


def display(value, digits=None):
    if isinstance(value, bool):
        return "good" if value else "ungood"

    if value is None:
        return ""

    if isinstance(value, str):
        return value

    sign = "-" if value < 0 else ""
    value = abs(value)
    whole, remainder = divmod(value.numerator, value.denominator)
    count = 28 if digits is None else digits
    scale = 10**count
    part, tail = divmod(remainder * scale, value.denominator)

    if tail * 2 >= value.denominator:
        part += 1

    if part == scale:
        whole, part = whole + 1, 0

    if count == 0:
        return sign + str(whole)

    result = f"{sign}{whole}.{part:0{count}d}"

    return result if digits is not None else result.rstrip("0").rstrip(".")
