# Newcode

한국어 문서: [README_KR.md](README_KR.md)

Newcode is an experimental programming language inspired by Newspeak from
George Orwell's _Nineteen Eighty-Four_. It treats vocabulary control as a
language-design constraint: source code is written with a deliberately small
approved vocabulary, and the interpreter rejects prohibited words, phrases,
and unapproved alternatives.

The project currently contains a Python reference implementation. The command
line program is named `goodthink`, and Newcode source files use the `.think`
extension.

> This is a critical language experiment about censorship and thought control,
> not an endorsement of those ideas.

## Current status

The language specification is version **0.7** and the Python package reports
implementation version **0.7.0**. Rust and browser ports remain future work;
the executable reference implementation is under `Python/`.

`goodthink version`, `run`, `check`, `format`, `inspect`, `policy`, and `test`
are available. 0.1 compatibility remains covered by the regression suite.

Version 0.7 adds the `commandthink` standard module and installable package
resources. Version 0.6 adds named `recordthink` types with required named fields. Version
0.4 adds reserved standard modules for deterministic random values,
local time, and safe relative paths. See [`CHANGELOG.md`](CHANGELOG.md) for the
version history.

## Requirements

- Python 3.11 or newer is recommended.
- No third-party Python packages are required.

## Run the CLI

From the repository root (`NewCode/`), run the module directly. Source paths
may be relative to the current directory or absolute paths:

```sh
python3 -m goodthink version
python3 -m goodthink check "Python/example/v0.2/For Beginners/01_calculator.think"
python3 -m goodthink run "Python/example/v0.2/For Beginners/01_calculator.think"
```

If you change into `Python/`, remove the `Python/` prefix from the source path:

```sh
cd Python
python3 -m goodthink run "example/v0.2/For Beginners/01_calculator.think"
```

The original entry point also works from the repository root:

```sh
PYTHONPATH=Python python3 Python/goodthink.py version
PYTHONPATH=Python python3 Python/goodthink.py check "Python/example/v0.2/For Beginners/05_routines.think"
PYTHONPATH=Python python3 Python/goodthink.py run "Python/example/v0.2/For Beginners/05_routines.think"
```

The CLI accepts these commands:

```text
goodthink version
goodthink check <program.think>
goodthink run <program.think>
goodthink format [--write] <program.think>
goodthink check [--trace] <program.think>
goodthink inspect --tokens|--ast <program.think>
goodthink policy check "text"
goodthink test <program.think>
```

Version 0.3 adds shortcuts only to the CLI. Newcode language commands keep their
full Newspeak-style names and do not gain aliases or abbreviations:

```text
goodthink program.think
goodthink -c program.think
goodthink -f program.think
goodthink -t program.think
goodthink --tokens program.think
goodthink --ast program.think
goodthink --policy "text"
```

Pass program arguments after `--`. The first argument has index `0`:

```text
goodthink run program.think -- first second
goodthink program.think -- first second
```

`check` lexes, parses, and statically validates a program without executing
it. `run` performs the same validation and then interprets the program.
Programs must have the `.think` suffix. Errors include a diagnostic code and,
when a source span is available, the corresponding line, column, and caret.

Command summary:

- `version` prints the runner and language versions.
- `check` validates without executing; add `--trace` to show validation stages.
- `run` validates and executes a program.
- `format` prints formatted indentation; add `--write` to save it.
- `inspect --tokens` prints lexer tokens and source positions.
- `inspect --ast` prints the parsed AST.
- `policy check "text"` checks text against the censorship policy.
- `test` runs only `testthink` blocks in isolation.

### Optional header

Newcode 0.7 files may omit the language header. A missing header defaults to
Newcode 0.7. Explicit `newcode 0.1` through `newcode 0.6` headers
remain supported for legacy programs.

```newcode
thought numberthink count be 3
speak count
```

### Optional global installation

For a development installation, install the local package once and then use the
short `goodthink` command from any directory:

```sh
cd Python
python3 -m pip install --user -e .
goodthink run "example/v0.2/For Beginners/01_calculator.think"
```

## A Newcode program

```newcode
newcode 0.1

routine numberthink addgood(numberthink first, numberthink second)
    reportvalue first plus second
endroutine

thought numberthink count be 3
thought goodthink approved be count more 0

verify approved
    speak "Victory count: ", addgood(count, 1)
otherthink
    speak "Ungood."
endverify
```

The language uses Newspeak-flavoured keywords instead of conventional
programming terminology:

| Purpose                         | Newcode forms                                          |
| ------------------------------- | ------------------------------------------------------ |
| Variable declaration/assignment | `thought ... be ...`                                   |
| Boolean values                  | `good`, `ungood`                                       |
| Conditional                     | `verify`, `otherthink`, `endverify`                    |
| Loop                            | `repeatwhile`, `nextrepeat`, `stoprepeat`, `endrepeat` |
| Function-like routine           | `routine`, `reportvalue`, `endroutine`                 |
| Output                          | `speak`, `speaknumber`                                 |
| Input                           | `listennumber`, `listenwords`                          |

## Language model

Newcode 0.3 adds `length(...)`, `find(...)`, `replace(...)`, `split(...)`, and
`joinwords(...)`, plus triple-quoted multiline strings (`"""..."""`). Newcode
0.4 adds standard modules without adding language aliases or abbreviated
keywords. Language commands deliberately keep their full Newspeak-style names;
only the CLI has short forms.

### Standard modules (0.4)

Standard modules use the existing `use` and `call` syntax. Their reserved
`standard/` paths are supplied by the interpreter and cannot be replaced by a
project file.

```newcode
use randomthink from "standard/randomthink.think"
use timethink from "standard/timethink.think"
use paththink from "standard/paththink.think"
```

| Module | Routine | Result |
| --- | --- | --- |
| `randomthink` | `setseed(number)` | Sets a per-run integer seed; returns `silencethink`. |
|  | `randomnumber(low, high)` | Inclusive integer in the requested range. |
|  | `randomfraction()` | Exact number from 0 inclusive to 1 exclusive. |
| `timethink` | `currenttime()` | Local-time `recordthink` with `year` through `second`. |
|  | `timecount()` | Whole Unix epoch seconds. |
| `paththink` | `joinpath`, `filename`, `extension`, `parentpath` | Safe relative-path construction and inspection. |

### Reliable `trythink` handlers (0.5)

`othercrime CODE` handles one runtime error code. Accepted codes are
`MATHCRIME`, `INDEXCRIME`, `FILECRIME`, `INPUTCRIME`, `WORDCRIME`, and
`TESTCRIME`. A code-free `othercrime` is the catch-all and must appear once,
last. `WORKLIMIT` always propagates and cannot be caught.

```newcode
trythink
    speak 1 divide 0
othercrime MATHCRIME
    speak "calculation blocked"
othercrime
    speak "unexpected runtime error"
endtrythink
```

### Command-line arguments (0.7)

```newcode
use commandthink from "standard/commandthink.think"
speak call commandthink argument(0)
```

`arguments()` returns all values after the CLI `--` separator as a `listthink`.
`argument(index)` returns one `wordthink` using zero-based indexing. Missing
positions produce `INPUTCRIME`; command-line values are checked by the official
censorship policy.

### User-defined `recordthink` types (0.6)

Declare named record types at the top level. Every field is required and
constructors use named `be` arguments, so field order does not matter.

```newcode
recordthink Person
    thought wordthink name
    thought numberthink age
endrecordthink

thought Person user be Person(age be 30, name be "Ada")
speak get user field name
change user field age be 31
```

User-defined records may be nested in records and lists and may be used with
`maybe`. Missing or unknown constructor fields are `THINKLOGIC ERROR`, field
type mismatches are `THINKTYPE ERROR`, and missing field access is `INDEXCRIME`.
|  | `pathexists(path)` | `good` only for an existing regular file. |

`randomnumber` and `setseed` require integer `numberthink` values. Path values
must use `/`; absolute paths, `..`, and backslashes raise `FILECRIME`. Path
results are checked against the same censorship policy as other generated text.

Newcode 0.2 retains the four basic types and adds:

- `numberthink` — exact integer and decimal values represented internally with
  `fractions.Fraction`.
- `wordthink` — ASCII strings checked by the official lexicon.
- `goodthink` — the boolean values `good` and `ungood`.
- `silencethink` — a routine that returns no value.
- `nothink` — the absence of a value, usable with `maybe <type>`.
- `listthink`, `recordthink`, and `indexthink` — mixed nested list/record/map values.
- `rawthink` — file/input text checked when it reaches an output or text operation.

Numeric operators are `plus`, `minus`, `times`, and `divide`. Comparisons are
`more`, `less`, and `same`; boolean operators are `both`, `either`, and the
unary `un`. The `join` operator concatenates strings and immediately checks the
result against the censorship policy.

Statements are separated by newlines. The lexer supports `//` and `/* ... */`
comments, ASCII identifiers, decimal literals, and the escapes `\\n`, `\\t`,
`\\"`, and `\\\\` in strings. Blocks are explicitly closed with words such as
`endverify`, `endrepeat`, and `endroutine`.

The validator performs type checking, name/scope checks, duplicate declaration
checks, return-path checks, and direct or indirect recursion rejection. The
runtime maintains global and routine-local scopes, supports `foreach`,
`trythink`, safe relative text-file I/O, and stops execution after `1_000_000`
counted steps. Modules expose routines through `call module routine(...)`;
`testthink` blocks run in isolated test mode.

## Censorship policy

The full policy is documented in
[`Newcode Censorship Policy.md`](Newcode%20Censorship%20Policy.md).

The official policy is stored in
[`Python/prohibited_words.json`](Python/prohibited_words.json). Source programs
cannot modify it. The policy contains:

- `replacement_rules` — oldspeak terms that must be replaced by approved
  Newcode vocabulary;
- `prohibited_terms` — words with no accepted replacement;
- `prohibited_phrases` — phrases that are rejected as a whole.

Identifiers, string literals, and `listenwords` input are checked. Matching is
case-insensitive and normalizes common separator and leetspeak variations.
The interpreter also rechecks text created by `join`, so concatenation cannot
be used to bypass the policy.

Typical diagnostics include `WORDCRIME`, `CRIMESTOP`, `THINKTYPE ERROR`,
`THINKLOGIC ERROR`, `MATHCRIME`, `INPUTCRIME`, `LOOPTHINK`, `WORKLIMIT`,
`INDEXCRIME`, `FILECRIME`, `MODULECRIME`, and `TESTCRIME`.

## Repository layout

```text
NewCode/
├── Python/
│   ├── goodthink.py              # CLI entry point
│   ├── prohibited_words.json     # Official censorship lexicon
│   ├── test_parser.py            # Regression tests for parser-adjacent bugs
│   ├── test_newcode02.py         # 0.2 type/file/module/exception tests
│   ├── example/
│   │   ├── v0.1/                 # 0.1 regression examples
│   │   ├── v0.2/                 # 0.2 examples, beginners, and errors
│   │   ├── v0.3/                 # 0.3 string and nested-record examples
│   │   ├── v0.4/                 # 0.4 standard-library examples
│   │   ├── v0.5/                 # 0.5 exception-handler examples
│   │   ├── v0.6/                 # 0.6 user-defined recordthink examples
│   │   └── v0.7/                 # 0.7 commandthink examples
│   └── newcode/
│       ├── cli.py                # Argument parsing and command orchestration
│       ├── lexer.py              # Tokens, literals, comments, lexeme checks
│       ├── parser.py             # AST construction
│       ├── model.py              # AST/token data classes and decimal parsing
│       ├── validator.py          # Static checks and type analysis
│       ├── runtime.py            # Interpreter and formatted output
│       ├── standard.py           # Reserved standard-module registry
│       ├── paths.py              # Shared safe relative-path rules
│       ├── censor.py             # Lexicon loading and matching
│       ├── errors.py             # Source spans and diagnostics
│       └── __init__.py            # Version and execution limit
├── README.md
└── README_KR.md
```

The implementation pipeline is:

```text
source.think
   → Censor + Lexer
   → Parser / AST
   → Validator
   → Runtime
```

## Deliberate limitations

Newcode 0.7 still excludes network access, environment settings, complex
numbers, implicit type conversion, and
user-controlled changes to the official lexicon. These
limitations are part of the experiment:
they make it possible to observe how a restricted vocabulary changes the shape
of programs.

## Development notes

The repository has a `unittest` regression suite and Python packaging metadata.
Before extending the language, keep the following boundaries in mind:

1. Add or change syntax in `lexer.py` and `parser.py`.
2. Represent new syntax in `model.py`.
3. Enforce static rules in `validator.py`.
4. Implement execution semantics in `runtime.py`.
5. Update the lexicon and the design documents when vocabulary rules change.

The next practical maintenance step is to expand regression coverage for
tokenization, parsing, censorship, type errors, control flow, routines, and
runtime edge cases.
