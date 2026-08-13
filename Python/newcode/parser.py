from newcode.errors import fail
from newcode.lexer import KEYWORDS, TYPE_NAMES
from newcode.model import *


class Parser:
    PRECEDENCE = {"either": 1, "both": 2, "more": 3, "less": 3, "same": 3,
                  "join": 4, "plus": 5, "minus": 5, "times": 6, "divide": 6}

    def __init__(self, tokens): self.tokens, self.index = tokens, 0
    def current(self): return self.tokens[self.index]
    def word(self, value): return self.current().kind == "word" and self.current().value == value
    def take(self): token = self.current(); self.index += 1; return token
    def require(self, value):
        if self.current().value != value: raise fail("THINKLOGIC ERROR", f"expected '{value}'", self.current().span)
        return self.take()
    def lines(self):
        while self.current().kind == "newline": self.take()
    def end_line(self):
        if self.current().kind not in ("newline", "eof"): raise fail("THINKLOGIC ERROR", "expected end of line", self.current().span)
        self.lines()
    def identifier(self):
        token = self.current()
        if token.kind != "word" or token.value in KEYWORDS: raise fail("THINKLOGIC ERROR", "expected an identifier", token.span)
        return self.take()
    def parse(self):
        self.lines()
        # 0.2부터는 헤더를 생략할 수 있으며, 생략 시 현재 기본 언어 버전을 사용합니다.
        if self.word("newcode"):
            header = self.take(); version = self.current()
            if version.kind != "number" or version.value not in ("0.1", "0.2"):
                raise fail("THINKLOGIC ERROR", "unsupported language version", header.span)
            self.version = version.value
            self.take()
            self.end_line()
        else:
            self.version = "0.2"
        statements = []
        while self.current().kind != "eof": statements.append(self.statement()); self.lines()
        return Program(statements)
    def statement(self):
        token, span = self.current(), self.current().span
        if self.word("thought"):
            self.take(); maybe = False
            if self.word("maybe"): maybe = True; self.take()
            if self.current().value in TYPE_NAMES:
                type_name = self.take().value
                name = self.identifier(); self.require("be"); value = self.expr(); self.end_line()
                return Declare(span, ("maybe " if maybe else "") + type_name, name.value, value)
            if maybe: raise fail("THINKLOGIC ERROR", "maybe must be followed by a type", self.current().span)
            name = self.identifier(); self.require("be"); value = self.expr(); self.end_line(); return Assign(span, name.value, value)
        if self.word("speak") or self.word("speaknumber"):
            number_only = self.take().value == "speaknumber"; items = []
            while True:
                value = self.expr(); digits = None
                if self.word("to"): self.take(); digits = self.expr()
                items.append((value, digits))
                if self.current().kind != ",": break
                self.take()
            self.end_line(); return Speak(span, items, number_only)
        if self.word("verify"):
            self.take(); condition = self.expr(); self.end_line(); yes = self.block({"otherthink", "endverify"}); no=[]
            if self.word("otherthink"): self.take(); self.end_line(); no=self.block({"endverify"})
            self.require("endverify"); self.end_line(); return Verify(span, condition, yes, no)
        if self.word("repeatwhile"):
            self.take(); condition=self.expr(); self.end_line(); body=self.block({"endrepeat"}); self.require("endrepeat"); self.end_line(); return Repeat(span, condition, body)
        if self.word("foreach"):
            self.take(); names=[self.identifier().value]
            if self.current().kind == ",": self.take(); names.append(self.identifier().value)
            self.require("in"); target=self.expr(); self.end_line(); body=self.block({"endforeach"}); self.require("endforeach"); self.end_line(); return Foreach(span,names,target,body)
        if self.word("nextrepeat"): self.take(); self.end_line(); return Next(span)
        if self.word("stoprepeat"): self.take(); self.end_line(); return Stop(span)
        if self.word("reportvalue"): self.take(); value=self.expr(); self.end_line(); return Report(span,value)
        if self.word("change"):
            self.take(); target=self.expr(); mode=self.take().value; key=self.expr(); self.require("be"); value=self.expr(); self.end_line(); return Change(span,target,mode,key,value)
        if self.word("add"):
            self.take(); value=self.expr(); self.require("to"); target=self.expr(); self.end_line(); return Add(span,value,target)
        if self.word("remove"):
            self.take(); target=self.expr(); mode=self.take().value; key=self.expr(); self.end_line(); return Remove(span,target,mode,key)
        if self.word("trythink"):
            self.take(); self.end_line(); body=self.block({"othercrime","endtrythink"}); handlers=[]
            while self.word("othercrime"):
                self.take(); code=None
                if self.current().kind=="word": code=self.take().value
                self.end_line(); handlers.append(OtherCrime(code,self.block({"othercrime","endtrythink"})))
            self.require("endtrythink"); self.end_line(); return Try(span,body,handlers)
        if self.word("writefile") or self.word("appendfile"):
            action=self.take().value; path=self.expr(); self.require("be"); value=self.expr(); self.end_line(); return FileWrite(span,action,path,value)
        if self.word("use"):
            self.take(); name=self.identifier(); self.require("from"); path=self.take()
            if path.kind!="string": raise fail("MODULECRIME","module path must be a string",path.span)
            self.end_line(); return ModuleUse(span,name.value,path.value)
        if self.word("testthink"):
            self.take(); title=self.take()
            if title.kind!="string": raise fail("TESTCRIME","test name must be a string",title.span)
            self.end_line(); body=self.block({"endtestthink"}); self.require("endtestthink"); self.end_line(); return TestThink(span,title.value,body)
        if self.word("routine"): return self.routine(span)
        if token.kind=="word" and token.value not in KEYWORDS:
            call=self.expr()
            if isinstance(call,Call): self.end_line(); return CallStatement(span,call)
        raise fail("THINKLOGIC ERROR", "expected a statement", span)
    def routine(self, span):
        self.take(); return_type=self.take().value; name=self.identifier(); self.require("("); params=[]; self.lines()
        while self.current().kind!=")":
            typ=self.take(); param=self.identifier(); params.append((typ.value,param.value,param.span)); self.lines()
            if self.current().kind!=",": break
            self.take(); self.lines()
        self.require(")"); self.end_line(); body=self.block({"endroutine"}); self.require("endroutine"); self.end_line(); return Routine(span,return_type,name.value,params,body)
    def block(self,endings):
        result=[]; self.lines()
        while self.current().kind!="eof" and self.current().value not in endings:
            if self.word("routine"): raise fail("THINKLOGIC ERROR","routines are only allowed at top level",self.current().span)
            result.append(self.statement()); self.lines()
        if self.current().kind=="eof": raise fail("THINKLOGIC ERROR","unclosed block",self.current().span)
        return result
    def expr(self, minimum=0):
        left=self.primary()
        while self.current().kind=="word" and self.current().value in self.PRECEDENCE:
            op=self.current().value; priority=self.PRECEDENCE[op]
            if priority<minimum: break
            operator=self.take(); left=Binary(operator.span,left,op,self.expr(priority+1))
        return left
    def primary(self):
        token=self.take()
        if token.kind=="number": return Number(token.span,fraction(token.value))
        if token.kind=="string": return Word(token.span,token.value)
        if token.kind=="word" and token.value in ("good","ungood"): return Good(token.span,token.value=="good")
        if token.kind=="word" and token.value=="nothink": return LiteralValue(token.span,None)
        if token.kind=="word" and token.value in ("un","minus"): return Unary(token.span,token.value,self.primary())
        if token.kind=="word" and token.value in ("listennumber","listenwords"): return Input(token.span,"numberthink" if token.value=="listennumber" else "wordthink")
        if token.kind=="word" and token.value=="call":
            module=self.take().value; routine=self.take().value; self.require("("); args=[]
            while self.current().kind!=")":
                args.append(self.expr())
                if self.current().kind!=",": break
                self.take()
            self.require(")"); return Call(token.span,module+"."+routine,args)
        if token.kind=="word" and token.value in ("size","lines","joinlines","readfile"):
            inner=self.primary(); return {"size":Size,"lines":Lines,"joinlines":JoinLines,"readfile":FileRead}[token.value](token.span,inner)
        if token.kind=="word" and token.value=="slice":
            target=self.primary(); self.require("from"); start=self.expr(); self.require("to"); return Slice(token.span,target,start,self.expr())
        if token.kind=="word" and token.value=="get":
            target=self.primary(); mode=self.take().value; key=self.primary(); return Get(token.span,target,mode,key)
        if token.kind=="word" and token.value in ("listthink","recordthink","indexthink"):
            self.require("("); items=[]
            while self.current().kind!=")":
                first=self.expr()
                if token.value in ("recordthink","indexthink"):
                    self.require("be"); items.append((first,self.expr()))
                else: items.append(first)
                if self.current().kind!=",": break
                self.take(); self.lines()
            self.require(")"); return Composite(token.span,token.value,items)
        if token.kind=="word" and token.value not in KEYWORDS:
            if self.current().kind!="(": return Name(token.span,token.value)
            self.take(); self.lines(); args=[]
            while self.current().kind!=")":
                args.append(self.expr()); self.lines()
                if self.current().kind!=",": break
                self.take(); self.lines()
            self.require(")"); return Call(token.span,token.value,args)
        if token.kind=="(":
            value=self.expr(); self.require(")"); return value
        raise fail("THINKLOGIC ERROR","expected an expression",token.span)
