import argparse
import sys
import time
from pathlib import Path

from newcode import LANGUAGE_VERSION, VERSION
from newcode.censor import Censor
from newcode.errors import NewcodeError
from newcode.lexer import Lexer
from newcode.parser import Parser
from newcode.runtime import Runtime
from newcode.validator import Validator


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="goodthink", usage="goodthink <run|check|version> [program.think]"
    )

    parser.add_argument("command", choices=("run", "check", "version"))
    parser.add_argument("file", nargs="?")

    args = parser.parse_args(argv)

    if args.command == "version":
        print(f"goodthink {VERSION} (Newcode {LANGUAGE_VERSION})")

        return 0

    if not args.file or Path(args.file).suffix != ".think":
        print("THINKLOGIC ERROR: source file must end with .think", file=sys.stderr)

        return 2

    path = Path(args.file)

    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"{path}: {exc}", file=sys.stderr)

        return 2

    try:
        censor = Censor(Path(__file__).parent.parent / "prohibited_words.json")
    except RuntimeError as exc:
        print(f"THINKLOGIC ERROR: {exc}", file=sys.stderr)

        return 2

    started = time.perf_counter()

    try:
        program = Parser(Lexer(source, censor).scan()).parse()
        routines = Validator(program).validate()
    except NewcodeError as exc:
        print(exc.display(str(path), source), file=sys.stderr)

        return 1

    validation_ms = (time.perf_counter() - started) * 1000

    if args.command == "check":
        print("GOODTHINK: program approved.")
        print(f"Validation time: {validation_ms:.2f} ms")

        return 0

    started = time.perf_counter()

    try:
        Runtime(censor, routines).execute(program)
    except NewcodeError as exc:
        print(exc.display(str(path), source), file=sys.stderr)

        return 1

    print("GOODTHINK: program approved and completed.")
    print(f"Validation time: {validation_ms:.2f} ms")
    print(f"Execution time: {(time.perf_counter() - started) * 1000:.2f} ms")

    return 0
