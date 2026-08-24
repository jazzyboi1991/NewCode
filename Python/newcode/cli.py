import argparse, sys, time
import copy
from pathlib import Path
from dataclasses import asdict, fields, is_dataclass
from . import LANGUAGE_VERSION, VERSION
from .censor import Censor
from .errors import NewcodeError
from .lexer import Lexer
from .parser import Parser
from .runtime import Runtime
from .validator import Validator
from .model import Call, ModuleUse, NativeRoutine, Routine, TestThink, Program
from .standard import STANDARD_PREFIX, standard_module


def official_censor():
    return Censor.official()


def _prefix_call_names(value, module):
    if isinstance(value, list) or isinstance(value, tuple):
        for item in value:
            _prefix_call_names(item, module)
    elif isinstance(value, Call):
        value.name = f"{module}.{value.name}"
        for argument in value.args:
            _prefix_call_names(argument, module)
    elif is_dataclass(value):
        for field in fields(value):
            _prefix_call_names(getattr(value, field.name), module)


def namespace_routine(routine, module):
    result = copy.deepcopy(routine)
    result.name = f"{module}.{result.name}"
    if isinstance(result, Routine):
        _prefix_call_names(result.body, module)
    return result


def load_import(base, module_path, censor, seen=None, span=None):
    standard = standard_module(module_path)
    if standard is not None:
        return list(standard.values())
    if module_path.startswith(STANDARD_PREFIX):
        raise NewcodeError("MODULECRIME", f"unknown standard module '{module_path}'", span or __import__('newcode.errors',fromlist=['Span']).Span(1,1))

    path = (Path(base) / module_path).resolve()
    try:
        path.relative_to(Path(base).resolve())
    except ValueError:
        raise NewcodeError("MODULECRIME", "module path must be a safe relative .think file", span or __import__('newcode.errors',fromlist=['Span']).Span(1,1))
    if path.suffix != ".think":
        raise NewcodeError("MODULECRIME", "module path must be a safe relative .think file", span or __import__('newcode.errors',fromlist=['Span']).Span(1,1))
    return load(path, censor, seen)

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
            child=load_import(path.parent, statement.path, censor, seen, statement.span)
            routines.extend([namespace_routine(r, statement.name) for r in child])
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
    opens={"verify","repeatwhile","foreach","routine","trythink","testthink","recordthink"}
    closes={"endverify","endrepeat","endforeach","endroutine","endtrythink","endtestthink","endrecordthink"}
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
    program_args = []
    if "--" in argv:
        separator = argv.index("--")
        program_args = argv[separator + 1:]
        argv = argv[:separator]
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
    if program_args and args.command != "run":
        print("THINKLOGIC ERROR: program arguments are supported only with run", file=sys.stderr)
        return 2
    if args.command=="policy":
        censor=official_censor()
        try: censor.check(" ".join(args.rest[1:]) if args.rest and args.rest[0]=="check" else " ".join(args.rest),False,__import__('newcode.errors',fromlist=['Span']).Span(1,1)); print("GOODTHINK: text approved."); return 0
        except NewcodeError as exc: print(f"{exc.code}: {exc.message}"); return 1
    if not args.rest: print("THINKLOGIC ERROR: source file is required",file=sys.stderr); return 2
    path=Path(args.rest[-1])
    try: source=path.read_text(encoding="utf-8")
    except OSError as exc: print(str(exc),file=sys.stderr); return 2
    try:
        censor=official_censor()
        program=Parser(Lexer(source,censor).scan()).parse()
        imported=[]
        for statement in program.statements:
            if isinstance(statement,ModuleUse):
                imported.extend([namespace_routine(r, statement.name) for r in load_import(path.parent, statement.path, censor, span=statement.span)])
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
            for test in tests: Runtime(censor,routines,cwd=path.parent,test_mode=True,argv=[]).execute(Program(test.body))
            print(f"GOODTHINK: {len(tests)} tests approved."); return 0
        Runtime(censor,routines,cwd=path.parent,argv=program_args).execute(program)
    except (NewcodeError,OSError) as exc:
        print(exc.display(str(path),source) if isinstance(exc,NewcodeError) else str(exc),file=sys.stderr); return 1
    print("GOODTHINK: program approved and completed."); return 0
