from newcode.censor import Censor
from newcode.errors import Span, fail
from newcode.model import Token


KEYWORDS = frozenset(
    """
newcode thought be speak speaknumber listennumber listenwords verify otherthink endverify
repeatwhile endrepeat nextrepeat stoprepeat routine endroutine reportvalue numberthink
wordthink goodthink silencethink rawthink listthink recordthink indexthink nothink maybe
plus minus times divide more less same both either un join to good ungood get at field key
change add remove size slice from foreach in endforeach trythink othercrime endtrythink
readfile writefile appendfile lines joinlines use call testthink endtestthink
""".split()
)
TYPE_NAMES = frozenset({"numberthink", "wordthink", "goodthink", "silencethink", "rawthink", "listthink", "recordthink", "indexthink"})


class Lexer:
    def __init__(self, source: str, censor: Censor):
        self.source, self.censor, self.index, self.line, self.column = (
            source,
            censor,
            0,
            1,
            1,
        )

    def scan(self) -> list[Token]:

        tokens = []

        while self.index < len(self.source):
            ch, span = self.source[self.index], Span(self.line, self.column)
            if ch in " \t\r":
                self._advance()
                continue
            if ch == "\n":
                tokens.append(Token("newline", "", span))
                self._advance()
                continue
            if self.source.startswith("//", self.index):
                while self.index < len(self.source) and self.source[self.index] != "\n":
                    self._advance()
                continue
            if self.source.startswith("/*", self.index):
                self._advance(2)
                while self.index < len(self.source) and not self.source.startswith(
                    "*/", self.index
                ):
                    self._advance()
                if self.index >= len(self.source):
                    raise fail("THINKLOGIC ERROR", "unclosed block comment", span)
                self._advance(2)
                continue
            if ch in "(),":
                tokens.append(Token(ch, ch, span))
                self._advance()
                continue
            if ch == '"':
                tokens.append(Token("string", self._string(span), span))
                continue
            if ch.isascii() and ch.isdigit():
                tokens.append(Token("number", self._number(span), span))
                continue
            if ch.isascii() and (ch.isalpha() or ch == "_"):
                name = self._name()
                if name not in KEYWORDS:
                    self.censor.check(name, True, span)
                tokens.append(Token("word", name, span))
                continue
            if ch.isascii():
                raise fail("THINKLOGIC ERROR", f"unexpected character '{ch}'", span)
            raise fail(
                "THINKLOGIC ERROR",
                "non-ASCII code is not allowed outside comments",
                span,
            )

        return tokens + [Token("eof", "", Span(self.line, self.column))]

    def _advance(self, count=1):
        for _ in range(count):
            if self.source[self.index] == "\n":
                self.line, self.column = self.line + 1, 1
            else:
                self.column += 1
            self.index += 1

    def _name(self):
        start = self.index
        self._advance()

        while (
            self.index < len(self.source)
            and self.source[self.index].isascii()
            and (self.source[self.index].isalnum() or self.source[self.index] == "_")
        ):
            self._advance()

        return self.source[start : self.index]

    def _number(self, span):
        start = self.index

        while self.index < len(self.source) and self.source[self.index].isdigit():
            self._advance()
        if self.index < len(self.source) and self.source[self.index] == ".":
            self._advance()
            if self.index >= len(self.source) or not self.source[self.index].isdigit():
                raise fail(
                    "THINKLOGIC ERROR",
                    "a decimal point must have digits after it",
                    span,
                )
            while self.index < len(self.source) and self.source[self.index].isdigit():
                self._advance()
        if self.index < len(self.source) and (
            self.source[self.index].isalpha() or self.source[self.index] == "_"
        ):
            raise fail(
                "THINKLOGIC ERROR",
                "numbers cannot be followed by identifier characters",
                span,
            )

        return self.source[start : self.index]

    def _string(self, span):
        self._advance()
        output = []

        while self.index < len(self.source):
            ch = self.source[self.index]
            if ch == '"':
                self._advance()
                value = "".join(output)
                self.censor.check(value, False, span)

                return value
            if ch == "\n":
                raise fail(
                    "THINKLOGIC ERROR", "string literals cannot span lines", span
                )
            if ch == "\\":
                self._advance()
                if self.index >= len(self.source):
                    break
                escaped = self.source[self.index]
                table = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
                if escaped not in table:
                    raise fail(
                        "THINKLOGIC ERROR", f"invalid string escape '\\{escaped}'", span
                    )
                output.append(table[escaped])
                self._advance()
                continue
            if not ch.isascii():
                raise fail("WORDCRIME", "non-ASCII string", span)
            output.append(ch)
            self._advance()
        raise fail("THINKLOGIC ERROR", "unclosed string literal", span)
