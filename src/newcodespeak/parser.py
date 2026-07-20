"""Recursive-descent parser for NewCodeSpeak tokens."""
from __future__ import annotations
from pathlib import Path
from . import ast
from .errors import ParseError
from .tokens import Token, TokenType

class Parser:
    def __init__(self, tokens: tuple[Token, ...], path: Path): self.tokens, self.path, self.index = tokens, path, 0
    @property
    def current(self) -> Token: return self.tokens[self.index]
    def error(self, message: str) -> ParseError: return ParseError(self.path, self.current.line, self.current.column, message)
    def take(self, value: str | None = None, kind: TokenType | None = None) -> Token:
        token = self.current
        if (value is not None and token.value != value) or (kind is not None and token.type != kind):
            raise self.error(f"expected {value or kind.name}, found {token.value or 'end of file'}")
        self.index += 1
        return token
    def word(self) -> str:
        if self.current.type not in (TokenType.KEYWORD, TokenType.NAME): raise self.error("expected approved word")
        value = self.current.value; self.index += 1; return value
    def words_until(self, stops: set[str]) -> tuple[str, ...]:
        words=[]
        while self.current.value not in stops:
            if self.current.type == TokenType.EOF: raise self.error("unexpected end of file")
            words.append(self.word())
        if not words: raise self.error("expected proposition")
        return tuple(words)
    def parse(self) -> ast.Program:
        self.take("approve"); names=[self.word()]
        while self.current.type == TokenType.COMMA: self.take(kind=TokenType.COMMA); names.append(self.word())
        self.take(kind=TokenType.SEMICOLON); statements=[]
        while self.current.type != TokenType.EOF: statements.append(self.statement())
        return ast.Program(ast.Approval(tuple(names)), tuple(statements))
    def expression(self) -> ast.Expression:
        if self.current.type == TokenType.INTEGER: node: ast.Expression = ast.IntegerLiteral(int(self.take(kind=TokenType.INTEGER).value))
        else:
            value=self.word(); node=ast.StatusLiteral(value) if value in {"true","false","good","ungood","plusgood","doubleplusgood"} else ast.NameReference(value)
        while self.current.value in {"plus","minus"}:
            operator=self.word(); right=self.expression_value(); node=ast.BinaryExpression(node, operator, right)
        return node
    def expression_value(self) -> ast.Expression:
        if self.current.type == TokenType.INTEGER: return ast.IntegerLiteral(int(self.take(kind=TokenType.INTEGER).value))
        value=self.word(); return ast.StatusLiteral(value) if value in {"true","false","good","ungood","plusgood","doubleplusgood"} else ast.NameReference(value)
    def condition(self) -> ast.Condition:
        # Conditions are delimited by then/end; a comparison is recognized by above/below.
        start=self.index
        while self.current.value not in {"then", "end"} and self.current.type != TokenType.EOF:
            if self.current.value in {"above","below"}:
                self.index=start; left=self.expression(); op=self.word(); right=self.expression(); return ast.Comparison(left, op, right)
            self.index += 1
        self.index=start; return ast.Proposition(self.words_until({"then", "end"}))
    def statement(self) -> ast.Statement:
        lead=self.current.value
        if lead == "set":
            self.take("set"); name=self.word(); self.take("to"); value=self.expression(); self.take(kind=TokenType.SEMICOLON); return ast.Assignment(name,value)
        if lead == "fact":
            self.take("fact"); prop=ast.Proposition(self.words_until({"is"})); self.take("is"); status=ast.StatusLiteral(self.word()); self.take(kind=TokenType.SEMICOLON); return ast.Fact(prop,status)
        if lead == "rule":
            self.take("rule"); conclusion=ast.Proposition(self.words_until({"when"})); self.take("when"); premise=ast.Proposition(self.words_until({";"})); self.take(kind=TokenType.SEMICOLON); return ast.Rule(conclusion,premise)
        if lead == "query": self.take("query"); node=ast.Query(ast.Proposition(self.words_until({";"}))); self.take(kind=TokenType.SEMICOLON); return node
        if lead == "proclaim": self.take("proclaim"); node=ast.Proclaim(self.words_until({";"})); self.take(kind=TokenType.SEMICOLON); return node
        if lead == "if":
            self.take("if"); cond=self.condition(); self.take("then"); yes=[]
            while self.current.value not in {"else","end"}: yes.append(self.statement())
            no=None
            if self.current.value=="else": self.take("else"); no=[]; while_loop=False
            if self.current.value=="else": pass
            if no is not None:
                while self.current.value!="end": no.append(self.statement())
            self.take("end"); return ast.Conditional(cond,tuple(yes),None if no is None else tuple(no))
        if lead == "repeat":
            self.take("repeat"); self.take("while"); cond=self.condition(); body=[]
            while self.current.value!="end": body.append(self.statement())
            self.take("end"); return ast.Repetition(cond,tuple(body))
        raise self.error("expected statement")

def parse_tokens(tokens: tuple[Token, ...], path: Path) -> ast.Program:
    return Parser(tokens, path).parse()
