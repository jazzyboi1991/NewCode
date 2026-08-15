from newcode.errors import fail
from newcode.model import (
    Add,
    Assign,
    Binary,
    Call,
    CallStatement,
    Declare,
    Change,
    Composite,
    FileRead,
    FileWrite,
    Foreach,
    Get,
    Good,
    Input,
    JoinLines,
    Lines,
    LiteralValue,
    ModuleUse,
    NativeRoutine,
    Name,
    Next,
    Number,
    Repeat,
    Report,
    Routine,
    Remove,
    Speak,
    Slice,
    Stop,
    Unary,
    Verify,
    Word,
    Size,
    StringOp,
    Try,
    TestThink,
)


def expression_calls(expr):
    if isinstance(expr, Call):
        yield expr.name

        for arg in expr.args:
            yield from expression_calls(arg)

    elif isinstance(expr, Unary):
        yield from expression_calls(expr.value)

    elif isinstance(expr, Binary):
        yield from expression_calls(expr.left)
        yield from expression_calls(expr.right)

    elif isinstance(expr, StringOp):
        for arg in expr.args:
            yield from expression_calls(arg)


def statement_calls(stmt):
    if isinstance(stmt, (Declare, Assign, Report)):
        yield from expression_calls(stmt.value)

    elif isinstance(stmt, CallStatement):
        yield from expression_calls(stmt.call)

    elif isinstance(stmt, Speak):
        for value, digits in stmt.items:
            yield from expression_calls(value)

            if digits:
                yield from expression_calls(digits)

    elif isinstance(stmt, Verify):
        yield from expression_calls(stmt.condition)

        for child in stmt.yes + stmt.no:
            yield from statement_calls(child)

    elif isinstance(stmt, Repeat):
        yield from expression_calls(stmt.condition)

        for child in stmt.body:
            yield from statement_calls(child)


class Validator:
    def __init__(self, program):
        self.program, self.routines = program, {}
        self.global_scopes, self.local_scopes = [dict()], []
        self.return_type, self.loop_depth = None, 0

    def validate(self):
        for statement in self.program.statements:
            if isinstance(statement, (Routine, NativeRoutine)):
                if statement.name in self.routines:
                    raise fail(
                        "CRIMESTOP",
                        f"duplicate global name '{statement.name}'",
                        statement.span,
                    )

                names = set()

                for _, name, span in statement.params:
                    if name in names:
                        raise fail("CRIMESTOP", f"duplicate parameter '{name}'", span)

                    names.add(name)

                self.routines[statement.name] = statement

        self._reject_recursion()

        for routine in self.routines.values():
            if isinstance(routine, Routine):
                self._routine(routine)

        self._block([x for x in self.program.statements if not isinstance(x, (Routine, NativeRoutine))])

        return self.routines

    def _reject_recursion(self):
        graph = {
            name: {
                call
                for statement in getattr(routine, "body", [])
                for call in statement_calls(statement)
                if call in self.routines
            }
            for name, routine in self.routines.items()
        }
        done, active = set(), set()

        def visit(name):
            if name in active:
                raise fail(
                    "LOOPTHINK",
                    f"recursive routine '{name}' is prohibited",
                    self.routines[name].span,
                )

            if name in done:
                return

            active.add(name)

            for child in graph[name]:
                visit(child)

            active.remove(name)
            done.add(name)

        for name in graph:
            visit(name)

    def _routine(self, routine):
        self.local_scopes, self.return_type, self.loop_depth = (
            [dict()],
            routine.return_type,
            0,
        )

        for type_name, name, span in routine.params:
            self._declare(type_name, name, span)

        returns = self._block(routine.body)

        if routine.return_type != "silencethink" and not returns:
            raise fail(
                "THINKLOGIC ERROR",
                f"routine '{routine.name}' does not report a {routine.return_type} value",
                routine.span,
            )

        self.local_scopes, self.return_type = [], None

    def _scopes(self):
        return self.local_scopes if self.return_type else self.global_scopes

    def _lookup(self, name, span):
        for scope in reversed(self._scopes()):
            if name in scope:
                return scope[name]

        message = (
            f"global variable access denied or undeclared name '{name}'"
            if self.return_type
            else f"undeclared name '{name}'"
        )

        raise fail("CRIMESTOP", message, span)

    def _declare(self, type_name, name, span):
        used = (
            any(name in scope for scope in self._scopes())
            or any(name in scope for scope in self.global_scopes)
            or name in self.routines
        )

        if used:
            raise fail("CRIMESTOP", f"duplicate or shadowed name '{name}'", span)

        self._scopes()[-1][name] = type_name

    def _type(self, expr):
        if isinstance(expr, LiteralValue):
            return "nothink"
        if isinstance(expr, Composite):
            if expr.type_name == "recordthink":
                fields = set()
                for key, value in expr.items:
                    if not isinstance(key, Name):
                        raise fail("THINKLOGIC ERROR", "record fields require identifiers", key.span)
                    if key.value in fields:
                        raise fail("CRIMESTOP", f"duplicate record field '{key.value}'", key.span)
                    fields.add(key.value)
                    self._type(value)
            elif expr.type_name == "listthink":
                for item in expr.items: self._type(item)
            elif expr.type_name == "indexthink":
                for key, value in expr.items: self._type(key); self._type(value)
            return expr.type_name
        if isinstance(expr, FileRead):
            return "rawthink"
        if isinstance(expr, Size):
            return "numberthink"
        if isinstance(expr, Lines):
            return "listthink"
        if isinstance(expr, JoinLines):
            return "wordthink"
        if isinstance(expr, StringOp):
            expected = {"length": ("wordthink",), "find": ("wordthink", "wordthink"), "replace": ("wordthink", "wordthink", "wordthink"), "split": ("wordthink", "wordthink"), "joinwords": ("listthink", "wordthink")}[expr.name]
            for arg, wanted in zip(expr.args, expected):
                got = self._type(arg)
                if got not in (wanted, "rawthink"):
                    raise fail("THINKTYPE ERROR", f"expected {wanted}, received {got}", arg.span)
            return "numberthink" if expr.name in ("length", "find") else ("listthink" if expr.name == "split" else "wordthink")
        if isinstance(expr, Slice):
            return "wordthink"
        if isinstance(expr, Get):
            return "nothink"
        if isinstance(expr, Number):
            return "numberthink"

        if isinstance(expr, Word):
            return "wordthink"

        if isinstance(expr, Good):
            return "goodthink"

        if isinstance(expr, Name):
            return self._lookup(expr.value, expr.span)

        if isinstance(expr, Input):
            return expr.type_name

        if isinstance(expr, Unary):
            got, expected = (
                self._type(expr.value),
                "goodthink" if expr.op == "un" else "numberthink",
            )

            if got != expected:
                raise fail(
                    "THINKTYPE ERROR", f"expected {expected}, received {got}", expr.span
                )

            return expected

        if isinstance(expr, Call):
            routine = self.routines.get(expr.name)

            if not routine:
                raise fail("CRIMESTOP", f"undeclared routine '{expr.name}'", expr.span)

            if len(expr.args) != len(routine.params):
                raise fail(
                    "THINKTYPE ERROR",
                    f"routine '{expr.name}' expects {len(routine.params)} arguments",
                    expr.span,
                )

            for arg, (expected, _, _) in zip(expr.args, routine.params):
                got = self._type(arg)

                if got != expected:
                    raise fail(
                        "THINKTYPE ERROR",
                        f"expected {expected}, received {got}",
                        arg.span,
                    )

            return routine.return_type

        left, right = self._type(expr.left), self._type(expr.right)

        if expr.op == "same":
            if left != right:
                raise fail(
                    "THINKTYPE ERROR", f"expected {left}, received {right}", expr.span
                )

            return "goodthink"

        if expr.op == "join" and left in ("wordthink", "rawthink") and right in ("wordthink", "rawthink"):
            return "wordthink"

        expected = (
            "wordthink"
            if expr.op == "join"
            else "goodthink"
            if expr.op in ("both", "either")
            else "numberthink"
        )

        if left != expected or right != expected:
            raise fail(
                "THINKTYPE ERROR",
                f"expected {expected}, received {left if left != expected else right}",
                expr.span,
            )

        return (
            "goodthink" if expr.op in ("more", "less", "both", "either") else expected
        )

    def _nested(self, statements):
        self._scopes().append({})

        try:
            return self._block(statements)
        finally:
            self._scopes().pop()

    def _block(self, statements):
        guaranteed = False

        for statement in statements:
            if not guaranteed:
                guaranteed = self._statement(statement)

        return guaranteed

    def _statement(self, statement):
        if isinstance(statement, (ModuleUse, TestThink)): return False
        if isinstance(statement, Declare):
            got = self._type(statement.value)

            declared = statement.type_name.removeprefix("maybe ")
            if got != declared and not (statement.type_name.startswith("maybe ") and got == "nothink"):
                raise fail(
                    "THINKTYPE ERROR",
                    f"expected {statement.type_name}, received {got}",
                    statement.span,
                )

            self._declare(statement.type_name, statement.name, statement.span)

        elif isinstance(statement, Assign):
            expected, got = (
                self._lookup(statement.name, statement.span),
                self._type(statement.value),
            )

            if expected != got and not (expected.startswith("maybe ") and got in ("nothink", expected[6:])):
                raise fail(
                    "THINKTYPE ERROR",
                    f"expected {expected}, received {got}",
                    statement.span,
                )

        elif isinstance(statement, (Change, Add, Remove, FileWrite)):
            if isinstance(statement, Change):
                self._type(statement.target)
                if not (statement.mode == "field" and isinstance(statement.key, Name)):
                    self._type(statement.key)
                self._type(statement.value)
            elif isinstance(statement, Add):
                self._type(statement.value)
                if self._type(statement.target) != "listthink":
                    raise fail("THINKTYPE ERROR", "add requires listthink", statement.target.span)
            elif isinstance(statement, Remove):
                target_type = self._type(statement.target)
                if target_type not in ("listthink", "recordthink", "indexthink"):
                    raise fail("THINKTYPE ERROR", "remove requires a compound value", statement.target.span)
                if not (statement.mode == "field" and isinstance(statement.key, Name)):
                    self._type(statement.key)
            else:
                self._type(statement.path); self._type(statement.value)

        elif isinstance(statement, Foreach):
            self._type(statement.target); self.loop_depth += 1
            self._scopes().append({name: "numberthink" for name in statement.names})
            try: self._block(statement.body)
            finally: self.loop_depth -= 1
            self._scopes().pop()

        elif isinstance(statement, Try):
            self._nested(statement.body)
            for handler in statement.handlers: self._nested(handler.body)

        elif isinstance(statement, Speak):
            for value, digits in statement.items:
                actual = self._type(value)

                if (statement.number_only or digits) and actual != "numberthink":
                    raise fail(
                        "THINKTYPE ERROR",
                        f"expected numberthink, received {actual}",
                        value.span,
                    )

                if digits and self._type(digits) != "numberthink":
                    raise fail(
                        "THINKTYPE ERROR", "precision must be numberthink", digits.span
                    )

        elif isinstance(statement, Verify):
            if self._type(statement.condition) != "goodthink":
                raise fail(
                    "THINKTYPE ERROR",
                    "verify condition must be goodthink",
                    statement.span,
                )

            yes_returns = self._nested(statement.yes)
            no_returns = self._nested(statement.no)

            return yes_returns and no_returns

        elif isinstance(statement, Repeat):
            if self._type(statement.condition) != "goodthink":
                raise fail(
                    "THINKTYPE ERROR",
                    "repeatwhile condition must be goodthink",
                    statement.span,
                )

            self.loop_depth += 1

            try:
                self._nested(statement.body)
            finally:
                self.loop_depth -= 1

        elif isinstance(statement, (Next, Stop)):
            if not self.loop_depth:
                raise fail(
                    "CRIMESTOP",
                    "repeat control is only allowed in a repeatwhile block",
                    statement.span,
                )

        elif isinstance(statement, Report):
            if not self.return_type:
                raise fail(
                    "CRIMESTOP",
                    "reportvalue is only allowed in a routine",
                    statement.span,
                )

            got = self._type(statement.value)

            if got != self.return_type:
                raise fail(
                    "THINKTYPE ERROR",
                    f"expected {self.return_type}, received {got}",
                    statement.span,
                )

            return True

        elif isinstance(statement, CallStatement):
            self._type(statement.call)

        return False
