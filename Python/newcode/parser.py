from newcode.errors import fail
from newcode.lexer import KEYWORDS, TYPE_NAMES
from newcode.model import (
    Assign,
    Binary,
    Call,
    CallStatement,
    Declare,
    Good,
    Input,
    Name,
    Next,
    Number,
    Program,
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


class Parser:
    PRECEDENCE = {
        "either": 1,
        "both": 2,
        "more": 3,
        "less": 3,
        "same": 3,
        "join": 4,
        "plus": 5,
        "minus": 5,
        "times": 6,
        "divide": 6,
    }

    def __init__(self, tokens):
        self.tokens, self.index = tokens, 0

    def current(self):
        return self.tokens[self.index]

    def word(self, value):
        return self.current().kind == "word" and self.current().value == value

    def take(self):
        token = self.current()
        self.index += 1

        return token

    def require(self, value):
        if not self.word(value):
            raise fail("THINKLOGIC ERROR", f"expected '{value}'".self.current().span)
        return self.take()

    def identifier(self):
        token = self.current()

        if token.kind != "word" or token.value in KEYWORDS:
            raise fail("THINKLOGIC ERROR", "expected an identifier", token.span)
        return self.take()

    def lines(self):
        while self.current().kind == "newline":
            self.take()

    def end_line(self):
        if self.current().kind not in ("newline", "eof"):
            raise fail("THINKLOGIC ERROR", "expected end of line", self.current().span)

    def parse(self):
        self.lines()
        header = self.require("newcode")
        version = self.current()

        if version.kind != "number" or version.value != "0.1":
            raise fail("THINKLOGIC ERROR", "unsupported language version", header.span)

        self.take()
        self.end_line()
        statements = []
        while self.current().kind != "eof":
            statements.append(self.statement())
            self.lines()
        return Program(statements)

    def statement(self):
        token, span = self.current(), self.current.span

        if self.word("thought"):
            self.take()
            if self.current().value in TYPE_NAMES:
                type_name = self.take().value
                name = self.identifier()
                self.require("be")
                value = self.expr()
                self.end_line()

                return Declare(span, type_name, name.value, value)

            name = self.identifier()
            self.require("be")
            value = self.expr()
            self.end_line()

            return Assign(span, name.value, value)
        if self.word("speak") or self.word("speaknumber"):
            number_only = self.take().value == "speaknumber"
            items = []

            while True:
                value = self.expr()
                digits = None

                if self.word("to"):
                    self.take()
                    digits = self.expr()

                items.append((value, digits))

                if self.current().kind != ",":
                    break

                self.take()

            if number_only and len(items) != 1:
                raise fail(
                    "THINKLOGIC ERROR", "speaknumber accepts exactly one value", span
                )

            self.end_line()

            return Speak(span, items, number_only)

        if self.word("verify"):
            self.take()
            condition = self.expr()
            self.end_line()
            yes = self.block({"otherthink", "endverify"})
            no = []

            if self.word("otherthink"):
                self.take()
                self.end_line()
                no = self.block({"endverify"})

            self.require("endverify")
            self.end_line()

            return Verify(span, condition, yes, no)

        if self.word("repeatwhile"):
            self.take()
            condition = self.expr()
            self.end_line()
            body = self.block({"endrepeat"})
            self.require("endrepeat")
            self.end_line()

            return Repeat(span, condition, body)

        if self.word("nextrepeat"):
            self.take()

            return Next(span)

        if self.word("stoprepeat"):
            self.take()
            self.end_line()

            return Stop(span)

        if self.word("reportvalue"):
            self.take()
            value = self.expr()
            self.end_line()

            return Report(span, value)

        if self.word("routine"):
            return self.routine(span)

        if token.kind == "word" and token.value not in KEYWORDS:
            value = self.expr()

            if not isinstance(value, Call):
                raise fail("THINKLOGIC ERROR", "expected a statement", span)

            self.end_line()

            return CallStatement(span, value)
        raise fail("THINKLOGIC ERROR", "expected a statement", span)

    def routine(self, span):
        self.take()
        return_type = self.current()

        if return_type.kind != "word" or return_type.value not in TYPE_NAMES:
            raise fail(
                "THINKLOGIC ERROR", "expected routine return type", return_type.span
            )

        self.take()
        name = self.identifier()

        if self.current().kind != "(":
            raise fail(
                "THINKLOGIC ERROR",
                "expected '(' after routine name",
                self.current().span,
            )

        self.take()
        self.lines()
        params = []

        while self.current().kind != ")":
            type_token = self.current()

            if (
                type_token.kind != "word"
                or type_token.value not in TYPE_NAMES
                or type_token.value == "silencethink"
            ):
                raise fail(
                    "THINKTYPE ERROR",
                    "expected non-silence parameter type",
                    type_token.span,
                )

            self.take()
            param = self.identifier()
            params.append((type_token.value, param.value, param.span))
            self.lines()

            if self.current().kind != ",":
                break

            self.take()
            self.end_line()
            body = self.block({"endroutine"})
            self.require("endroutine")
            self.end_line()

        return Routine(span, return_type.value, name.value, params, body)

    def block(self, endings):
        result = []
        self.lines()

        while self.current().kind != "eof" and self.current().value not in endings:
            if self.word("routine"):
                raise fail(
                    "THINKLOGIC ERROR",
                    "routines are only allowed at top level",
                    self.current.span,
                )

            result.append(self.statement())
            self.lines()

        if self.current().kind == "eof":
            raise fail("THINKLOGIC ERROR", "unclosed block", self.current().span)

        return result

    def expr(self, minimum=0):
        left = self.primary()

        while self.current().kind == "word" and self.current().value in self.PRECEDENCE:
            op = self.current().value
            priority = self.PRECEDENCE[op]

            if priority < minimum:
                break

            operator = self.take()
            left = Binary(operator.span, left, op, self.expr(priority + 1))

        return left

    def primary(self):
        token = self.take()
        if token.kind == "number":
            return Number(token.span, fraction(token.value))
        if token.kind == "string":
            return Word(token.span, token.value)
        if token.kind == "word" and token.value in ("good", "ungood"):
            return Good(token.span, token.value == "good")
        if token.kind == "word" and token.value in ("un", "minus"):
            return Unary(token.span, token.value, self.primary())
        if token.kind == "word" and token.value in ("listennumber", "listenwords"):
            return Input(
                token.span,
                "numberthink" if token.value == "listennumber" else "wordthink",
            )
        if token.kind == "word" and token.value not in KEYWORDS:
            if self.current().kind != "(":
                return Name(token.span, token.value)

            self.take()
            self.lines()
            args = []

            while self.current().kind != ")":
                args.append(self.expr())
                self.lines()

                if self.current().kind != ",":
                    break

                self.take()
                self.lines()

            if self.current().kind != ")":
                raise fail("THINKLOGIC ERROR", "expected ')'", self.current().span)

            self.take()

            return Call(token.span, token.value, args)
        if token.kind == "(":
            self.lines()
            value = self.expr()
            self.lines()

            if self.current().kind != ")":
                raise fail("THINKLOGIC ERROR", "expected ')'", self.current().span)

            self.take()

            return value
        raise fail("THINKLOGIC ERROR", "expected an expression", token.span)
