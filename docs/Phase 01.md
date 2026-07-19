# Phase 01 — 프로젝트 골격과 CLI 진입점

## 목표

이 단계에서는 NewCodeSpeak를 실행할 수 있는 Python 패키지의 뼈대를 만든다. 아직 언어를 해석하지는 않는다. 대신 `.ncs` 파일을 안전하게 읽고, 이후 단계가 연결될 명령줄 인터페이스 `ncs`를 제공한다.

이 문서의 코드는 모두 사용자가 직접 각 파일에 입력한다. 이 단계에서 생성해야 할 파일은 아래뿐이며, 인터프리터·파서·검열기는 아직 만들지 않는다.

```text
NewSpeak/
├── README.md
├── 전체 개발 계획.md
├── Phase 01.md
├── pyproject.toml
├── src/
│   └── newcodespeak/
│       ├── __init__.py
│       ├── __main__.py
│       └── cli.py
└── tests/
    └── test_cli.py
```

## 완료 기준

- `python -m newcodespeak --help`가 도움말을 출력한다.
- `python -m newcodespeak --version`이 버전을 출력한다.
- 존재하는 UTF-8 `.ncs` 파일을 주면 파일을 읽었다는 메시지를 출력한다.
- 존재하지 않는 파일과 UTF-8이 아닌 파일은 이해 가능한 오류와 종료 코드 `5`를 반환한다.
- 빈 파일도 정상적으로 읽는다.
- 아직 실행기가 없다는 사실이 출력에 명시된다.

## 1. `pyproject.toml`

프로젝트 루트인 `NewSpeak/pyproject.toml`에 아래 전체 내용을 입력한다. 외부 런타임 의존성은 아직 필요 없다. `ncs`는 패키지를 설치했을 때 사용할 명령 이름이다.

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "newcodespeak"
version = "0.1.0"
description = "A critical Newspeak-inspired programming language experiment"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [
  { name = "NewCodeSpeak Contributors" }
]

[project.scripts]
ncs = "newcodespeak.cli:main"

[tool.setuptools]
package-dir = { "" = "src" }

[tool.setuptools.packages.find]
where = ["src"]
```

## 2. `src/newcodespeak/__init__.py`

이 파일은 패키지의 공개 버전 정보를 한곳에 둔다.

```python
"""NewCodeSpeak reference interpreter."""

__version__ = "0.1.0"
```

## 3. `src/newcodespeak/__main__.py`

`python -m newcodespeak` 실행을 CLI 함수로 연결한다.

```python
"""Module entry point for ``python -m newcodespeak``."""

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
```

## 4. `src/newcodespeak/cli.py`

이 단계의 전체 CLI 구현이다. 파일의 내용을 읽기만 하며, 내용을 출력하거나 해석하지 않는다. 이후 단계에서 `run_source()` 자리에 검열기·렉서·파서·실행기를 순서대로 연결한다.

```python
"""Command-line interface for the NewCodeSpeak interpreter."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys

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
        help="Path to a UTF-8 NewCodeSpeak source file (.ncs).",
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
    """Run the CLI and return a documented process exit code."""
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
```

## 5. `tests/test_cli.py`

표준 라이브러리 `unittest`만 사용한다. 따라서 별도의 테스트 패키지를 설치하지 않아도 된다. 아래는 이 단계의 전체 테스트 코드다.

```python
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from newcodespeak import __version__
from newcodespeak.cli import EXIT_IO_ERROR, EXIT_SUCCESS, main, read_source


class CliTests(unittest.TestCase):
    def test_version_prints_package_version(self) -> None:
        output = StringIO()

        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as raised:
                main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(output.getvalue(), f"ncs {__version__}\n")

    def test_missing_source_prints_help_and_returns_io_error(self) -> None:
        error_output = StringIO()

        with redirect_stderr(error_output):
            result = main([])

        self.assertEqual(result, EXIT_IO_ERROR)
        self.assertIn("usage: ncs", error_output.getvalue())

    def test_existing_source_is_loaded_without_execution(self) -> None:
        with TemporaryDirectory() as directory:
            source_path = Path(directory) / "program.ncs"
            source_path.write_text("approve citizen;\n", encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                result = main([str(source_path)])

        self.assertEqual(result, EXIT_SUCCESS)
        self.assertIn("loaded 17 character(s)", output.getvalue())
        self.assertIn("execution is not implemented yet", output.getvalue())

    def test_empty_source_is_loaded(self) -> None:
        with TemporaryDirectory() as directory:
            source_path = Path(directory) / "empty.ncs"
            source_path.write_text("", encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                result = main([str(source_path)])

        self.assertEqual(result, EXIT_SUCCESS)
        self.assertIn("loaded 0 character(s)", output.getvalue())

    def test_missing_file_returns_io_error(self) -> None:
        error_output = StringIO()

        with redirect_stderr(error_output):
            result = main(["missing-file.ncs"])

        self.assertEqual(result, EXIT_IO_ERROR)
        self.assertIn("source file does not exist", error_output.getvalue())

    def test_non_utf8_file_returns_io_error(self) -> None:
        with TemporaryDirectory() as directory:
            source_path = Path(directory) / "invalid.ncs"
            source_path.write_bytes(b"\xff")
            error_output = StringIO()

            with redirect_stderr(error_output):
                result = main([str(source_path)])

        self.assertEqual(result, EXIT_IO_ERROR)
        self.assertIn("not valid UTF-8", error_output.getvalue())

    def test_read_source_rejects_a_directory(self) -> None:
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(OSError, "source path is a directory"):
                read_source(Path(directory))


if __name__ == "__main__":
    unittest.main()
```

## 6. 사용자가 수행할 검증 순서

다음 명령은 **위 파일들을 직접 만든 뒤에만** 실행한다. 여기서는 실행하지 않는다.

```bash
cd NewSpeak
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --editable .
python -m unittest discover -s tests -v
python -m newcodespeak --help
python -m newcodespeak --version
```

작은 확인용 소스 파일을 직접 만든 뒤에는 아래처럼 확인한다.

```bash
ncs examples/conforming.ncs
```

예상 출력은 파일의 문자 수가 달라질 수 있다는 점을 제외하면 다음과 같다.

```text
loaded <문자 수> character(s) from examples/conforming.ncs
NewCodeSpeak Phase 01: execution is not implemented yet.
```

## 7. 이 단계에서 하지 않는 일

- `approve`의 승인 여부를 검사하지 않는다.
- `.ncs`의 문법을 해석하지 않는다.
- 프로그램을 실행하거나 출력 내용을 평가하지 않는다.
- `examples/` 파일을 자동으로 만들지 않는다.

이 제한은 의도적이다. Phase 02에서 어휘 정책과 검열기를 추가한 뒤, Phase 03부터 토큰화와 파싱을 연결한다.
