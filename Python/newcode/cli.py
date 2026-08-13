import argparse, sys, time
from pathlib import Path
from dataclasses import asdict, is_dataclass
from . import LANGUAGE_VERSION, VERSION
from .censor import Censor
from .errors import NewcodeError
from .lexer import Lexer
from .parser import Parser
from .runtime import Runtime
from .validator import Validator
from .model import ModuleUse, Routine, TestThink, Program

def load(path, censor, seen=None):
    seen=set() if seen is None else seen
    path=Path(path).resolve()
    if path in seen: raise NewcodeError("LOOPTHINK", "cyclic module import", __import__('newcode.errors',fromlist=['Span']).Span(1,1))
    seen.add(path)
    try:
        source=path.read_text(encoding="utf-8")
    except OSError as exc:
        raise NewcodeError("MODULECRIME", f"cannot load module '{path}': {exc}", __import__('newcode.errors',fromlist=['Span']).Span(1,1)) from exc
    program=Parser(Lexer(source,censor).scan()).parse()
    routines=[]
    for statement in program.statements:
        if isinstance(statement,ModuleUse):
            module_path=(path.parent/statement.path).resolve()
            try:
                module_path.relative_to(path.parent)
            except ValueError:
                raise NewcodeError("MODULECRIME", "module path must be a safe relative .think file", statement.span)
            if module_path.suffix != ".think":
                raise NewcodeError("MODULECRIME", "module path must be a safe relative .think file", statement.span)
            child=load(module_path,censor,seen)
            routines.extend([Routine(r.span,r.return_type,f"{statement.name}.{r.name}",r.params,r.body) for r in child])
        elif isinstance(statement,Routine): routines.append(statement)
        elif isinstance(statement,ModuleUse): pass
        else: raise NewcodeError("MODULECRIME", "modules may contain routines only", statement.span)
    return routines

def format_source(source):
    # Triple-quoted strings may contain meaningful line breaks and indentation.
    # Leave such source byte-for-byte intact until the formatter has a full string-aware pass.
    if '"""' in source:
        return source if source.endswith("\n") else source + "\n"
    level=0; output=[]
    opens={"verify","repeatwhile","foreach","routine","trythink","testthink"}
    closes={"endverify","endrepeat","endforeach","endroutine","endtrythink","endtestthink"}
    for raw in source.splitlines():
        line=raw.strip()
        if not line: output.append(""); continue
        first=line.split()[0]
        if first in closes: level=max(0,level-1)
        if first in {"otherthink", "othercrime"}: level=max(0,level-1)
        output.append("    "*level+line)
        if first in opens: level+=1
        if first in {"otherthink", "othercrime"}: level+=1
    return "\n".join(output)+"\n"

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # CLI 단축형은 언어 문법과 분리된 명령행 편의 기능입니다.
    if argv and (argv[0].endswith(".think") or Path(argv[0]).exists()):
        argv = ["run", *argv]
    elif argv and argv[0] in {"-c", "-f", "-t"}:
        argv = [{"-c": "check", "-f": "format", "-t": "test"}[argv[0]], *argv[1:]]
    elif argv and argv[0] == "--tokens":
        argv = ["inspect", "--tokens", *argv[1:]]
    elif argv and argv[0] == "--ast":
        argv = ["inspect", "--ast", *argv[1:]]
    elif argv and argv[0] == "--policy":
        argv = ["policy", "check", *argv[1:]]
    ap=argparse.ArgumentParser(prog="goodthink")
    ap.add_argument("command", choices=("run","check","version","format","inspect","policy","test"))
    ap.add_argument("rest", nargs="*"); ap.add_argument("--write",action="store_true"); ap.add_argument("--trace",action="store_true"); ap.add_argument("--tokens",action="store_true"); ap.add_argument("--ast",action="store_true")
    args=ap.parse_args(argv)
    if args.command=="version": print(f"goodthink {VERSION} (Newcode {LANGUAGE_VERSION})"); return 0
    if args.command=="policy":
        censor=Censor(Path(__file__).parent.parent/"prohibited_words.json")
        try: censor.check(" ".join(args.rest[1:]) if args.rest and args.rest[0]=="check" else " ".join(args.rest),False,__import__('newcode.errors',fromlist=['Span']).Span(1,1)); print("GOODTHINK: text approved."); return 0
        except NewcodeError as exc: print(f"{exc.code}: {exc.message}"); return 1
    if not args.rest: print("THINKLOGIC ERROR: source file is required",file=sys.stderr); return 2
    path=Path(args.rest[-1])
    try: source=path.read_text(encoding="utf-8")
    except OSError as exc: print(str(exc),file=sys.stderr); return 2
    try:
        censor=Censor(Path(__file__).parent.parent/"prohibited_words.json")
        program=Parser(Lexer(source,censor).scan()).parse()
        imported=[]
        for statement in program.statements:
            if isinstance(statement,ModuleUse):
                imported.extend([Routine(r.span,r.return_type,f"{statement.name}.{r.name}",r.params,r.body) for r in load(path.parent/statement.path,censor)])
        program.statements.extend(imported)
        routines=Validator(program).validate()
        if args.command=="inspect":
            if args.tokens: print("\n".join(f"{t.span.line}:{t.span.column} {t.kind} {t.value}" for t in Lexer(source,censor).scan()))
            else: print(program)
            return 0
        if args.command=="format":
            result=format_source(source)
            if args.write: path.write_text(result,encoding="utf-8")
            else: print(result,end="")
            return 0
        if args.command=="check":
            if args.trace: print("[LEX] approved\n[PARSE] approved\n[TYPE] approved\n[CHECK] approved")
            print("GOODTHINK: program approved."); return 0
        if args.command=="test":
            tests=[x for x in program.statements if isinstance(x,TestThink)]
            for test in tests: Runtime(censor,routines,cwd=path.parent,test_mode=True).execute(Program(test.body))
            print(f"GOODTHINK: {len(tests)} tests approved."); return 0
        Runtime(censor,routines,cwd=path.parent).execute(program)
    except (NewcodeError,OSError) as exc:
        print(exc.display(str(path),source) if isinstance(exc,NewcodeError) else str(exc),file=sys.stderr); return 1
    print("GOODTHINK: program approved and completed."); return 0
