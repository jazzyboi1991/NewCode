"""Command-line interface for the NewCodeWpeak interpreter."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__

EXIT_SUCCESS = 0
EXIT_IO_ERROR = 5


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="ncs",
        description="Run a NewCodeSpeak source file.",
    )
    parser.add_argument(
        "source",
        type=Path,
        nargs="?",
        help="Path to a UTF-8 NewCodeSpeak source file (.ncs)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the NewCodeSpeak version and exit.",
    )
    return parser


def read_source(path: Path) -> str:
    """Read one UTF-8 source file, translating OS errors to a user error."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise OSError(f"source file does not exist: {path}") from error
    except IsADirectoryError as error:
        raise OSError(f"source path is a directory: {path}") from error
    except UnicodeDecodeError as error:
        raise OSError(f"source file is not valid UTF-8: {path}") from error
    except OSError as error:
        raise OSError(f"could not read source file {path}: {error}") from error


def run_source(source: str, path: Path) -> None:
    """Report a successfully loaded source file.
    Phase 01 deliberately does not parse or execute ``source``. Later phases
    will replace this body with the censor, lexer, parser, and runtime.
    """
    print(f"loaded {len(source)} character(s) from {path}")
    print("NewCodeSpeak Phase 01: execution is not implemented yet.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.source is None:
        parser.print_help(sys.stderr)
        return EXIT_IO_ERROR

    try:
        source = read_source(args.source)
    except OSError as error:
        print(f"ncs: input error: {error}", file=sys.stderr)
        return EXIT_IO_ERROR

    run_source(source, args.source)
    return EXIT_SUCCESS
