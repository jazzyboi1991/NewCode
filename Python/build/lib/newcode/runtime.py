import re
import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from newcode import MAX_STEPS
from newcode.errors import NewcodeError, Span, fail
from newcode.model import *
from newcode.paths import safe_file_path

@dataclass
class Variable:
    type_name: str
    value: object

class ContinueFlow(Exception): pass
class StopFlow(Exception): pass
class ReturnFlow(Exception):
    def __init__(self, value): self.value=value

class Runtime:
    def __init__(self, censor, routines, cwd=None, test_mode=False, now_provider=None, time_provider=None, argv=None):
        self.censor,self.routines,self.cwd=censor,routines,Path(cwd or Path.cwd())
        self.test_mode = test_mode
        self.command_args = [] if test_mode else list(argv or [])
        self.random_generator = random.Random()
        self.now_provider = now_provider or (lambda: datetime.now().astimezone())
        self.time_provider = time_provider or time.time
        self.global_scopes,self.local_scopes=[{}],[]; self.steps=self.loop_depth=0
    def execute(self, program): self._block([x for x in program.statements if not isinstance(x,(Routine,NativeRoutine))])
    def _scopes(self): return self.local_scopes if self.local_scopes else self.global_scopes
    def _tick(self, span):
        self.steps+=1
        if self.steps>MAX_STEPS: raise fail("WORKLIMIT","execution limit exceeded",span)
    def _lookup(self,name,span):
        for scope in reversed(self._scopes()):
            if name in scope: return scope[name]
        message=f"global variable access denied or undeclared name '{name}'" if self.local_scopes else f"undeclared name '{name}'"
        raise fail("CRIMESTOP",message,span)
    def _nested(self, statements):
        self._scopes().append({})
        try: self._block(statements)
        finally: self._scopes().pop()
    def _value(self, expr):
        self._tick(expr.span)
        if isinstance(expr,Number): return expr.value
        if isinstance(expr,Word): return expr.value
        if isinstance(expr,Good): return expr.value
        if isinstance(expr,LiteralValue): return expr.value
        if isinstance(expr,Name): return self._lookup(expr.value,expr.span).value
        if isinstance(expr,RecordConstruct):
            return {name: self._value(value) for name, value in expr.fields}
        if isinstance(expr,Input): return self._input(expr)
        if isinstance(expr,Composite):
            if expr.type_name=="listthink": return [self._value(x) for x in expr.items]
            return {(k.value if isinstance(k,Name) else self._value(k)):self._value(v) for k,v in expr.items}
        if isinstance(expr,FileRead):
            path=self._safe_path(self._value(expr.path), expr.path.span)
            try: return path.read_text(encoding="utf-8")
            except OSError as exc: raise fail("FILECRIME",str(exc),expr.span)
        if isinstance(expr,Size): return len(self._value(expr.target))
        if isinstance(expr,Lines): return self._value(expr.target).splitlines()
        if isinstance(expr,JoinLines): return "\n".join(str(x) for x in self._value(expr.target))
        if isinstance(expr,StringOp):
            values = [self._value(arg) for arg in expr.args]
            if expr.name == "length": return len(values[0])
            if expr.name == "find": return values[0].find(values[1])
            if expr.name == "replace":
                value = values[0].replace(values[1], values[2])
                self.censor.check(value, False, expr.span)
                return value
            if expr.name == "split": return values[0].split(values[1])
            if expr.name == "joinwords":
                value = str(values[1]).join(str(item) for item in values[0])
                self.censor.check(value, False, expr.span)
                return value
        if isinstance(expr,Slice):
            value=self._value(expr.target); return value[int(self._value(expr.start)):int(self._value(expr.stop))]
        if isinstance(expr,Get):
            value=self._value(expr.target); key=expr.key.value if expr.mode=="field" and isinstance(expr.key,Name) else self._value(expr.key)
            if expr.mode == "at":
                try: return value[int(key)]
                except (IndexError, KeyError, TypeError, ValueError):
                    raise fail("INDEXCRIME", "item does not exist", expr.span)
            try: return value.get(key)
            except (AttributeError, TypeError): raise fail("INDEXCRIME", "field or key access is invalid", expr.span)
        if isinstance(expr,Unary): return not self._value(expr.value) if expr.op=="un" else -self._value(expr.value)
        if isinstance(expr,Call): return self._call(expr)
        left,right=self._value(expr.left),self._value(expr.right)
        if expr.op=="join":
            value=str(left)+str(right); self.censor.check(value,False,expr.span); return value
        if expr.op=="plus": return left+right
        if expr.op=="minus": return left-right
        if expr.op=="times": return left*right
        if expr.op=="divide":
            if right==0: raise fail("MATHCRIME","division by zero",expr.span)
            return left/right
        if expr.op=="more": return left>right
        if expr.op=="less": return left<right
        if expr.op=="same": return left==right
        if expr.op=="both": return left and right
        return left or right
    def _input(self, expr):
        if self.test_mode: raise fail("TESTCRIME", "input is unavailable in testthink", expr.span)
        raw=input().strip()
        if expr.type_name=="wordthink":
            if not raw.isascii(): raise fail("INPUTCRIME","non-ASCII input",expr.span)
            self.censor.check(raw,False,expr.span); return raw
        raw="-"+raw[6:] if raw.startswith("minus ") else raw
        if not re.fullmatch(r"-?\d+(?:\.\d+)?",raw): raise fail("INPUTCRIME","invalid number",expr.span)
        return -fraction(raw[1:]) if raw.startswith("-") else fraction(raw)
    def _call(self, call):
        routine=self.routines[call.name]; values=[self._value(x) for x in call.args]
        if isinstance(routine, NativeRoutine):
            return routine.handler(self, values, call.span)
        scope={name:Variable(typ,val) for val,(typ,name,_) in zip(values,routine.params)}
        saved=self.local_scopes; self.local_scopes=[scope]; old=self.loop_depth; self.loop_depth=0
        try:
            try: self._block(routine.body)
            except ReturnFlow as flow: return flow.value
            if routine.return_type=="silencethink": return None
            raise fail("THINKLOGIC ERROR",f"routine '{routine.name}' did not report a value",call.span)
        finally: self.local_scopes=saved; self.loop_depth=old
    def _block(self, statements):
        for statement in statements: self._statement(statement)
    def _statement(self, statement):
        self._tick(statement.span)
        if isinstance(statement,(ModuleUse,TestThink,RecordType)): pass
        elif isinstance(statement,Declare): self._scopes()[-1][statement.name]=Variable(statement.type_name,self._value(statement.value))
        elif isinstance(statement,Assign): self._lookup(statement.name,statement.span).value=self._value(statement.value)
        elif isinstance(statement,Speak):
            output=""
            for value,digits in statement.items:
                result=self._value(value)
                self._check_output(result, value.span)
                if isinstance(result,str): self.censor.check(result,False,value.span)
                output+=display(result) if digits is None else display(result,int(self._value(digits)))
            print(output)
        elif isinstance(statement,Change):
            target=self._value(statement.target)
            key=statement.key.value if statement.mode=="field" and isinstance(statement.key,Name) else self._value(statement.key)
            value=self._value(statement.value)
            try: target[int(key) if statement.mode=="at" else key]=value
            except (IndexError,KeyError,TypeError): raise fail("INDEXCRIME","item does not exist",statement.span)
        elif isinstance(statement,Add):
            target=self._value(statement.target)
            if not isinstance(target,list): raise fail("THINKTYPE ERROR","add requires listthink",statement.span)
            target.append(self._value(statement.value))
        elif isinstance(statement,Remove):
            target=self._value(statement.target)
            key=statement.key.value if statement.mode=="field" and isinstance(statement.key,Name) else self._value(statement.key)
            try: target.pop(int(key)) if statement.mode=="at" else target.pop(key)
            except (IndexError,KeyError,TypeError): raise fail("INDEXCRIME","item does not exist",statement.span)
        elif isinstance(statement,Verify): self._nested(statement.yes if self._value(statement.condition) else statement.no)
        elif isinstance(statement,Repeat):
            while self._value(statement.condition):
                self.loop_depth+=1
                try:
                    try: self._nested(statement.body)
                    except ContinueFlow: continue
                    except StopFlow: break
                finally: self.loop_depth-=1
        elif isinstance(statement,Foreach):
            target=self._value(statement.target); pairs=list(enumerate(target)) if isinstance(target,list) else list(target.items()) if isinstance(target,dict) else []
            for pair in pairs:
                self.loop_depth+=1; self.local_scopes.append({n:Variable("numberthink",v) for n,v in zip(statement.names,pair)})
                try: self._block(statement.body)
                except ContinueFlow: pass
                except StopFlow: break
                finally: self.local_scopes.pop(); self.loop_depth-=1
        elif isinstance(statement,Next): raise ContinueFlow()
        elif isinstance(statement,Stop): raise StopFlow()
        elif isinstance(statement,Report): raise ReturnFlow(self._value(statement.value))
        elif isinstance(statement,CallStatement): self._value(statement.call)
        elif isinstance(statement,FileWrite):
            if self.test_mode: raise fail("TESTCRIME", "file writing is unavailable in testthink", statement.span)
            path=self._safe_path(self._value(statement.path), statement.path.span); value=self._value(statement.value)
            if isinstance(value,str): self.censor.check(value,False,statement.value.span)
            try:
                if statement.action=="writefile": path.write_text(str(value),encoding="utf-8")
                else:
                    with path.open("a",encoding="utf-8") as handle: handle.write(str(value))
            except OSError as exc: raise fail("FILECRIME",str(exc),statement.span)
        elif isinstance(statement,Try):
            try:
                self._nested(statement.body)
            except NewcodeError as exc:
                if exc.code == "WORKLIMIT":
                    raise
                code = getattr(exc, "code", None)
                handler = next((h for h in statement.handlers if h.code == code), None)
                if handler is None:
                    handler = next((h for h in statement.handlers if h.code is None), None)
                if handler is None:
                    raise
                self._nested(handler.body)
    def _safe_path(self, raw, span):
        return safe_file_path(self.cwd, raw, span)

    def _check_output(self, value, span):
        if isinstance(value, str):
            self.censor.check(value, False, span)
        elif isinstance(value, list):
            for item in value: self._check_output(item, span)
        elif isinstance(value, dict):
            for key, item in value.items():
                self._check_output(str(key), span)
                self._check_output(item, span)

def display(value,digits=None):
    if isinstance(value,bool): return "good" if value else "ungood"
    if value is None: return "nothink"
    if isinstance(value,str): return value
    if isinstance(value,list): return "[" + ", ".join(display(item) for item in value) + "]"
    if isinstance(value,dict): return "{" + ", ".join(f"{key}: {display(item)}" for key,item in value.items()) + "}"
    sign="-" if value<0 else ""; value=abs(value); whole,remainder=divmod(value.numerator,value.denominator); count=28 if digits is None else digits; scale=10**count; part,tail=divmod(remainder*scale,value.denominator)
    if tail*2>=value.denominator: part+=1
    if part==scale: whole,part=whole+1,0
    if count==0: return sign+str(whole)
    result=f"{sign}{whole}.{part:0{count}d}"
    return result if digits is not None else result.rstrip("0").rstrip(".")
