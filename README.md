# Newcode

한국어 문서: [README_KR.md](README_KR.md)

Newcode is an experimental programming language inspired by Newspeak from
George Orwell's *Nineteen Eighty-Four*. It treats vocabulary control as a
language-design constraint: source code is written with a deliberately small
approved vocabulary, and the interpreter rejects prohibited words, phrases,
and unapproved alternatives.

The project currently contains a Python reference implementation. The command
line program is named `goodthink`, and Newcode source files use the `.think`
extension.

> This is a critical language experiment about censorship and thought control,
> not an endorsement of those ideas.

## Current status

The language specification is version **0.1** and the Python package reports
implementation version **0.1.0**. The repository has no Rust or browser
implementation; the executable code is under `Python/`.

The implementation is an active prototype. `goodthink version`, `check`, and
`run` are verified against the bundled example program. Treat the documents in
`docs/` as design/reference material, not as a guarantee that every planned
feature is currently executable.

## Requirements

- Python 3.11 or newer is recommended.
- No third-party Python packages are required.

## Run the CLI

Run commands from the repository root:

```sh
PYTHONPATH=Python python3 Python/goodthink.py version
PYTHONPATH=Python python3 Python/goodthink.py check Python/example/victory.think
PYTHONPATH=Python python3 Python/goodthink.py run Python/example/victory.think
```

The CLI accepts three commands:

```text
goodthink version
goodthink check <program.think>
goodthink run <program.think>
```

`check` lexes, parses, and statically validates a program without executing
it. `run` performs the same validation and then interprets the program.
Programs must have the `.think` suffix. Errors include a diagnostic code and,
when a source span is available, the corresponding line, column, and caret.

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

| Purpose | Newcode forms |
| --- | --- |
| Variable declaration/assignment | `thought ... be ...` |
| Boolean values | `good`, `ungood` |
| Conditional | `verify`, `otherthink`, `endverify` |
| Loop | `repeatwhile`, `nextrepeat`, `stoprepeat`, `endrepeat` |
| Function-like routine | `routine`, `reportvalue`, `endroutine` |
| Output | `speak`, `speaknumber` |
| Input | `listennumber`, `listenwords` |

## Language model

Newcode 0.1 has four explicit types:

- `numberthink` — exact integer and decimal values represented internally with
  `fractions.Fraction`.
- `wordthink` — ASCII strings checked by the official lexicon.
- `goodthink` — the boolean values `good` and `ungood`.
- `silencethink` — a routine that returns no value.

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
runtime maintains global and routine-local scopes and stops execution after
`1_000_000` counted steps.

## Censorship policy

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
`THINKLOGIC ERROR`, `MATHCRIME`, `INPUTCRIME`, `LOOPTHINK`, and `WORKLIMIT`.

## Repository layout

```text
NewCode/
├── Python/
│   ├── goodthink.py              # CLI entry point
│   ├── prohibited_words.json     # Official censorship lexicon
│   ├── test_parser.py            # Regression tests for parser-adjacent bugs
│   ├── example/victory.think     # Example Newcode program
│   └── newcode/
│       ├── cli.py                # Argument parsing and command orchestration
│       ├── lexer.py              # Tokens, literals, comments, lexeme checks
│       ├── parser.py             # AST construction
│       ├── model.py              # AST/token data classes and decimal parsing
│       ├── validator.py          # Static checks and type analysis
│       ├── runtime.py            # Interpreter and formatted output
│       ├── censor.py             # Lexicon loading and matching
│       ├── errors.py             # Source spans and diagnostics
│       └── __init__.py            # Version and execution limit
├── docs/
│   ├── 계획서 1.md               # Language design and implementation plan
│   ├── 계획서 2.md               # Additional planning notes
│   └── Python Codes.md           # Expanded Python reference notes
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

The 0.1 design does not provide arrays, maps, objects, files, modules,
network access, complex numbers, implicit type conversion, or user-controlled
changes to the official lexicon. These limitations are part of the experiment:
they make it possible to observe how a restricted vocabulary changes the shape
of programs.

## Development notes

The repository has a small `unittest` regression suite and no packaging
metadata. Before extending the language, keep the following boundaries in mind:

1. Add or change syntax in `lexer.py` and `parser.py`.
2. Represent new syntax in `model.py`.
3. Enforce static rules in `validator.py`.
4. Implement execution semantics in `runtime.py`.
5. Update the lexicon and the design documents when vocabulary rules change.

The next practical maintenance step is to expand regression coverage for
tokenization, parsing, censorship, type errors, control flow, routines, and
runtime edge cases.
