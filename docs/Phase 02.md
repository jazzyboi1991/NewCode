# Phase 02 — 어휘 정책과 검열기

## 목표

이 단계에서는 NewCodeSpeak의 핵심 제약인 **승인 어휘**를 파서보다 먼저 적용한다. 소스 전체에서 첫 `approve` 선언을 읽어 사용자 이름을 승인하고, 기본 어휘와 승인된 이름 이외의 모든 단어를 거부한다.

검열은 코드에만 적용되지 않는다. 문자열과 `//` 한 줄 주석도 같은 방식으로 검사한다. 아직 구문 분석은 하지 않으므로, 이 단계에서 통과한 소스가 문법적으로 올바르다는 뜻은 아니다.

이 문서에는 사용자가 직접 입력할 전체 코드만 적는다. 여기서 실제 소스 파일을 만들거나 테스트를 실행하지 않는다.

## Phase 01에서 바뀌는 파일

```text
NewSpeak/
├── src/newcodespeak/
│   ├── cli.py             # 수정: 읽은 직후 검열기를 호출
│   ├── errors.py          # 추가: 검열 오류 형식
│   ├── vocabulary.py      # 추가: 기본 어휘와 이름 규칙
│   └── censor.py          # 추가: 승인 선언 확인과 전체 소스 검사
└── tests/
    ├── test_cli.py        # 수정: CLI 검열 동작 확인
    └── test_censor.py     # 추가: 검열기 단위 테스트
```

`__init__.py`, `__main__.py`, `pyproject.toml`은 Phase 01 그대로 둔다.

## 정책 결정

### 기본 어휘

README 명세의 기본 어휘는 항상 허용한다. 따라서 `set`, `party`, `good`, `true` 등은 `approve`에 다시 적지 않는다.

### 사용자 이름

- 프로그램은 공백 뒤가 아닌 소스의 첫 문장으로 `approve` 선언을 하나 가져야 한다.
- 사용자 이름은 쉼표로 구분한다. 예: `approve citizen, quota;`
- 이름은 소문자 영어 글자와 밑줄만으로 이루어진다: `[a-z_]+`.
- 기본 어휘를 사용자 이름으로 다시 승인하거나 같은 이름을 두 번 승인할 수 없다.
- 이 단계에서는 `approve` 뒤의 문장을 문법적으로 해석하지 않는다. 다만 승인 선언 자체의 형태는 검사한다.

### 단어 검사 범위

검열기는 문자·숫자·밑줄·하이픈이 이어진 덩어리를 검사한다. 순수 숫자는 허용하지만, `name2`, `BadName`, `bad-name`, 한글 이름은 모두 유효한 이름이 아니므로 거부한다. 이 규칙 덕분에 문자열과 주석으로 금지 어휘를 숨길 수 없다.

## 완료 기준

- `approve quota; set quota to 1;`은 검열을 통과한다.
- 승인되지 않은 변수·문자열 속 단어·주석 속 단어가 각각 검열 오류가 된다.
- 첫 `approve` 선언이 없거나 잘못된 이름을 선언하면 검열 오류가 된다.
- 오류 객체에는 파일 경로, 줄, 열, 문제 단어가 들어 있다.
- CLI는 검열 오류에 종료 코드 `2`를 사용한다.
- Phase 01의 파일 읽기 동작과 종료 코드 `5`는 유지된다.

## 1. `src/newcodespeak/errors.py` — 새 파일

모든 언어 관련 오류의 기반 클래스와 검열 오류를 정의한다. 아직 Phase 07의 코드 조각 진단 형식은 구현하지 않는다. 하지만 이후 단계에서 같은 오류 객체를 확장할 수 있도록 위치 정보를 지금부터 보관한다.

```python
"""Error types used by the NewCodeSpeak interpreter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class NewCodeSpeakError(Exception):
    """Base class for expected NewCodeSpeak errors."""


@dataclass(frozen=True)
class CensorshipError(NewCodeSpeakError):
    """Raised when source text contains vocabulary the Party did not approve."""

    path: Path
    line: int
    column: int
    word: str
    reason: str

    def __str__(self) -> str:
        return (
            f"{self.path}:{self.line}:{self.column}: "
            f"censorship error: {self.reason}: {self.word!r}"
        )


@dataclass(frozen=True)
class ApprovalDeclarationError(NewCodeSpeakError):
    """Raised when the mandatory first approval declaration is invalid."""

    path: Path
    line: int
    column: int
    reason: str

    def __str__(self) -> str:
        return (
            f"{self.path}:{self.line}:{self.column}: "
            f"censorship error: {self.reason}"
        )
```

## 2. `src/newcodespeak/vocabulary.py` — 새 파일

명세의 기본 승인 어휘와 사용자 이름 규칙을 한 모듈에 둔다. Phase 03의 렉서도 이 모듈의 이름 규칙을 재사용해야 검열기와 렉서가 단어를 다르게 해석하지 않는다.

```python
"""The Party-approved vocabulary and user-name policy."""

from __future__ import annotations

import re
from collections.abc import Iterable


CORE_VOCABULARY = frozenset(
    {
        "approve",
        "set",
        "to",
        "if",
        "then",
        "else",
        "repeat",
        "while",
        "end",
        "fact",
        "rule",
        "when",
        "query",
        "proclaim",
        "is",
        "above",
        "below",
        "plus",
        "minus",
        "and",
        "or",
        "good",
        "ungood",
        "plusgood",
        "doubleplusgood",
        "party",
        "citizen",
        "work",
        "obey",
        "ownlife",
        "oldthink",
        "crimethink",
        "true",
        "false",
    }
)

NAME_PATTERN = re.compile(r"[a-z_]+\Z")


def is_valid_user_name(name: str) -> bool:
    """Return whether *name* follows the NewCodeSpeak user-name rule."""
    return NAME_PATTERN.fullmatch(name) is not None


def approved_vocabulary(user_names: Iterable[str]) -> frozenset[str]:
    """Combine the permanently approved words with approved user names."""
    return CORE_VOCABULARY | frozenset(user_names)
```

## 3. `src/newcodespeak/censor.py` — 새 파일

이 모듈은 별도 렉서를 만들지 않고, 검열에 필요한 최소 단어 스캔만 수행한다. `WORD_PATTERN`은 순수 숫자를 제외하고 `bad-name`, `name2` 같은 잘못된 이름도 하나의 후보로 잡는다.

```python
"""Vocabulary censorship performed before lexing and parsing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .errors import ApprovalDeclarationError, CensorshipError
from .vocabulary import CORE_VOCABULARY, approved_vocabulary, is_valid_user_name


APPROVAL_PATTERN = re.compile(r"\A\s*approve\s+(?P<names>[^;]*);")
WORD_PATTERN = re.compile(r"(?<!\w)[\w-]+(?!\w)", re.UNICODE)


@dataclass(frozen=True)
class CensorResult:
    """The approved user names extracted from one source file."""

    user_names: frozenset[str]


def line_and_column(source: str, offset: int) -> tuple[int, int]:
    """Convert a zero-based character offset into one-based source coordinates."""
    line = source.count("\n", 0, offset) + 1
    previous_newline = source.rfind("\n", 0, offset)
    column = offset - previous_newline
    return line, column


def parse_approval_declaration(source: str, path: Path) -> frozenset[str]:
    """Read and validate the required first ``approve`` declaration."""
    match = APPROVAL_PATTERN.match(source)
    if match is None:
        raise ApprovalDeclarationError(
            path=path,
            line=1,
            column=1,
            reason="a program must begin with an approve declaration",
        )

    raw_names = match.group("names")
    declaration_offset = match.start("names")
    pieces = raw_names.split(",")
    names: list[str] = []

    for piece in pieces:
        name = piece.strip()
        name_offset = declaration_offset + piece.find(name) if name else declaration_offset
        line, column = line_and_column(source, name_offset)

        if not name:
            raise ApprovalDeclarationError(
                path=path,
                line=line,
                column=column,
                reason="an approve declaration cannot contain an empty name",
            )
        if not is_valid_user_name(name):
            raise ApprovalDeclarationError(
                path=path,
                line=line,
                column=column,
                reason=f"invalid approved name {name!r}; use lowercase letters and underscores only",
            )
        if name in CORE_VOCABULARY:
            raise ApprovalDeclarationError(
                path=path,
                line=line,
                column=column,
                reason=f"{name!r} is already part of the core vocabulary",
            )
        if name in names:
            raise ApprovalDeclarationError(
                path=path,
                line=line,
                column=column,
                reason=f"{name!r} is approved more than once",
            )
        names.append(name)

    return frozenset(names)


def censor_source(source: str, path: Path) -> CensorResult:
    """Reject every non-numeric word outside the approved vocabulary.

    The scan deliberately includes comments and quoted text. Parsing is not
    required for that policy: any unapproved word is rejected before parsing.
    """
    user_names = parse_approval_declaration(source, path)
    allowed_words = approved_vocabulary(user_names)

    for match in WORD_PATTERN.finditer(source):
        word = match.group()
        if word.isdecimal():
            continue
        if word not in allowed_words:
            line, column = line_and_column(source, match.start())
            raise CensorshipError(
                path=path,
                line=line,
                column=column,
                word=word,
                reason="word is not in the approved vocabulary",
            )

    return CensorResult(user_names=user_names)
```

## 4. `src/newcodespeak/cli.py` — 전체 교체

기존의 파일 읽기 동작을 유지하고, 성공적으로 읽은 소스를 `censor_source()`에 전달한다. 검열 오류는 `stderr`에 출력하고 종료 코드 `2`를 반환한다.

```python
"""Command-line interface for the NewCodeSpeak interpreter."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys

from . import __version__
from .censor import censor_source
from .errors import NewCodeSpeakError


EXIT_SUCCESS = 0
EXIT_CENSORSHIP_ERROR = 2
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
    """Censor a loaded source file without parsing or executing it yet."""
    censor_source(source, path)
    print(f"loaded {len(source)} character(s) from {path}")
    print("NewCodeSpeak Phase 02: vocabulary passed; execution is not implemented yet.")


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

    try:
        run_source(source, args.source)
    except NewCodeSpeakError as error:
        print(f"ncs: {error}", file=sys.stderr)
        return EXIT_CENSORSHIP_ERROR

    return EXIT_SUCCESS
```

## 5. `tests/test_censor.py` — 새 파일

아래 테스트는 검열 정책을 직접 검증한다. 문자열과 주석은 아직 문법이 아니어도 검열 대상이므로, 검열기 테스트에는 포함한다.

```python
from __future__ import annotations

from pathlib import Path
import unittest

from newcodespeak.censor import censor_source, line_and_column
from newcodespeak.errors import ApprovalDeclarationError, CensorshipError


TEST_PATH = Path("program.ncs")


class CensorTests(unittest.TestCase):
    def test_approved_user_name_and_core_words_pass(self) -> None:
        result = censor_source("approve quota; set quota to 1;", TEST_PATH)

        self.assertEqual(result.user_names, frozenset({"quota"}))

    def test_core_word_needs_no_user_approval(self) -> None:
        result = censor_source("approve quota; proclaim doubleplusgood;", TEST_PATH)

        self.assertEqual(result.user_names, frozenset({"quota"}))

    def test_unapproved_code_word_is_rejected_with_location(self) -> None:
        with self.assertRaises(CensorshipError) as raised:
            censor_source("approve quota; set memory to 1;", TEST_PATH)

        error = raised.exception
        self.assertEqual(error.word, "memory")
        self.assertEqual((error.line, error.column), (1, 20))

    def test_unapproved_word_in_string_is_rejected(self) -> None:
        with self.assertRaises(CensorshipError) as raised:
            censor_source('approve quota; proclaim "doubt";', TEST_PATH)

        self.assertEqual(raised.exception.word, "doubt")

    def test_unapproved_word_in_comment_is_rejected(self) -> None:
        with self.assertRaises(CensorshipError) as raised:
            censor_source("approve quota; // past", TEST_PATH)

        self.assertEqual(raised.exception.word, "past")

    def test_missing_first_approval_is_rejected(self) -> None:
        with self.assertRaises(ApprovalDeclarationError):
            censor_source("set quota to 1;", TEST_PATH)

    def test_declaration_must_be_the_first_statement(self) -> None:
        with self.assertRaises(ApprovalDeclarationError):
            censor_source("set quota to 1; approve quota;", TEST_PATH)

    def test_invalid_user_names_are_rejected(self) -> None:
        for name in ("Upper", "quota2", "quota-name", "할당량"):
            with self.subTest(name=name):
                with self.assertRaises(ApprovalDeclarationError):
                    censor_source(f"approve {name};", TEST_PATH)

    def test_empty_duplicate_and_core_names_are_rejected(self) -> None:
        invalid_sources = (
            "approve quota,;",
            "approve quota, quota;",
            "approve party;",
        )

        for source in invalid_sources:
            with self.subTest(source=source):
                with self.assertRaises(ApprovalDeclarationError):
                    censor_source(source, TEST_PATH)

    def test_numbers_are_not_vocabulary_words(self) -> None:
        censor_source("approve quota; set quota to 1984;", TEST_PATH)

    def test_line_and_column_are_one_based(self) -> None:
        self.assertEqual(line_and_column("one\ntwo", 4), (2, 1))


if __name__ == "__main__":
    unittest.main()
```

## 6. `tests/test_cli.py` — 전체 교체

Phase 01의 모든 입출력 테스트를 유지하면서, 성공한 소스는 승인 선언을 포함하도록 바꾸고 검열 오류의 종료 코드를 추가한다.

```python
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from newcodespeak import __version__
from newcodespeak.cli import (
    EXIT_CENSORSHIP_ERROR,
    EXIT_IO_ERROR,
    EXIT_SUCCESS,
    main,
    read_source,
)


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

    def test_approved_source_is_loaded_without_execution(self) -> None:
        with TemporaryDirectory() as directory:
            source_path = Path(directory) / "program.ncs"
            source_path.write_text("approve quota;\nset quota to 1;\n", encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                result = main([str(source_path)])

        self.assertEqual(result, EXIT_SUCCESS)
        self.assertIn("loaded 31 character(s)", output.getvalue())
        self.assertIn("vocabulary passed", output.getvalue())
        self.assertIn("execution is not implemented yet", output.getvalue())

    def test_empty_source_is_a_censorship_error(self) -> None:
        with TemporaryDirectory() as directory:
            source_path = Path(directory) / "empty.ncs"
            source_path.write_text("", encoding="utf-8")
            error_output = StringIO()

            with redirect_stderr(error_output):
                result = main([str(source_path)])

        self.assertEqual(result, EXIT_CENSORSHIP_ERROR)
        self.assertIn("must begin with an approve declaration", error_output.getvalue())

    def test_unapproved_source_word_returns_censorship_error(self) -> None:
        with TemporaryDirectory() as directory:
            source_path = Path(directory) / "censored.ncs"
            source_path.write_text("approve quota; set memory to 1;", encoding="utf-8")
            error_output = StringIO()

            with redirect_stderr(error_output):
                result = main([str(source_path)])

        self.assertEqual(result, EXIT_CENSORSHIP_ERROR)
        self.assertIn("memory", error_output.getvalue())

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

## 7. 사용자가 수행할 검증 순서

아래 명령은 위 파일을 모두 직접 입력한 뒤에만 실행한다. 이 문서 작성 과정에서는 실행하지 않는다.

```bash
cd NewSpeak
source .venv/bin/activate
python -m unittest discover -s tests -v
```

수동 확인에는 다음 두 파일 내용을 사용할 수 있다.

```newcodespeak
approve quota;
set quota to 1;
```

위 소스는 현재 문법 실행 전 단계이지만, CLI에서 “vocabulary passed” 메시지와 함께 성공해야 한다.

```newcodespeak
approve quota;
// past
```

위 소스는 `past`가 승인 어휘에 없으므로 검열 오류와 종료 코드 `2`를 반환해야 한다.

## 8. 다음 단계로 넘기는 결과

Phase 03은 `censor_source()`를 통과한 소스만 렉서에 전달한다. 이 단계에서 만든 다음 요소를 그대로 재사용한다.

- `CORE_VOCABULARY`와 `is_valid_user_name()`
- `CensorshipError`의 경로·줄·열 정보
- `CensorResult.user_names`
- CLI의 `EXIT_CENSORSHIP_ERROR = 2`
