# Newcode Grammar Examples

This directory explains Newcode grammar through small, focused `.think` files.
Each file demonstrates one main grammar feature instead of combining the whole
language into a single tour.

Run examples from the `NewCode/` directory:

```sh
PYTHONPATH=Python python3 Python/goodthink.py check Python/example/04_conditionals.think
PYTHONPATH=Python python3 Python/goodthink.py run Python/example/04_conditionals.think
```

For the input example:

```sh
printf '7\nAlpha\n' | PYTHONPATH=Python python3 Python/goodthink.py run Python/example/09_input.think
```

## Example Map

| File | Main feature |
| --- | --- |
| [`00_header_comments.think`](00_header_comments.think) | Version header, line comments, block comments |
| [`01_declarations_assignment.think`](01_declarations_assignment.think) | Variable declarations and assignment |
| [`02_numbers_arithmetic.think`](02_numbers_arithmetic.think) | Number operators and parentheses |
| [`03_words_join.think`](03_words_join.think) | Strings and `join` |
| [`04_conditionals.think`](04_conditionals.think) | `verify`, `otherthink`, boolean operators |
| [`05_loops.think`](05_loops.think) | `repeatwhile`, `nextrepeat`, `stoprepeat` |
| [`06_routines.think`](06_routines.think) | Typed routines and `reportvalue` |
| [`07_silence_routine.think`](07_silence_routine.think) | `silencethink` routines |
| [`08_output_precision.think`](08_output_precision.think) | `speak`, `speaknumber`, decimal precision |
| [`09_input.think`](09_input.think) | `listennumber` and `listenwords` |

## 00. Header and Comments

Every program begins with the language header:

```newcode
newcode 0.1
```

The current implementation accepts version `0.1`. Blank lines may appear after
the header and between statements.

Newcode supports two comment forms:

```newcode
// line comment
/* block comment */
```

Comments are ignored by the parser. Source code outside comments must be ASCII.

## 01. Declarations and Assignment

Variables are introduced with `thought`, a type, a name, `be`, and an
expression:

```newcode
thought numberthink count be 1
thought wordthink label be "Count"
thought goodthink approved be good
```

Assignment reuses `thought` but does not repeat the type:

```newcode
thought count be count plus 4
```

Newcode has no implicit type conversion. A `numberthink` variable can only
receive a `numberthink` expression, a `wordthink` variable can only receive text,
and a `goodthink` variable can only receive a boolean value.

## 02. Numbers and Arithmetic

`numberthink` supports integers and decimals. Arithmetic uses words instead of
symbols:

| Operator | Meaning |
| --- | --- |
| `plus` | addition |
| `minus` | subtraction |
| `times` | multiplication |
| `divide` | division |

Parentheses control grouping:

```newcode
thought numberthink grouped be (first plus second) times 2
```

Numbers are represented with exact rational arithmetic. Rounding happens only
when a value is printed with a fixed precision.

## 03. Words and `join`

Strings are `wordthink` values:

```newcode
thought wordthink first be "New"
thought wordthink second be "code"
```

The `join` operator concatenates two `wordthink` expressions:

```newcode
thought wordthink label be first join second join " grammar"
```

Identifiers, string literals, input text, and values produced by `join` are
checked against `Python/prohibited_words.json`. This means a program cannot
hide prohibited text by splitting it across multiple strings and joining it
later.

## 04. Conditionals

Conditionals use `verify`, optional `otherthink`, and `endverify`:

```newcode
verify approved
    speak "Condition accepted."
otherthink
    speak "Ungood."
endverify
```

The condition must be `goodthink`. Comparisons such as `more`, `less`, and
`same` produce `goodthink`. Boolean logic uses:

| Operator | Meaning |
| --- | --- |
| `both` | logical and |
| `either` | logical or |
| `un` | logical not |

Use parentheses when negating a comparison:

```newcode
verify un (count less 0)
```

Without parentheses, `un count less 0` tries to apply `un` directly to the
number `count`, which is a type error.

## 05. Loops

Loops use `repeatwhile` and `endrepeat`:

```newcode
repeatwhile count less 6
    thought count be count plus 1
endrepeat
```

The loop condition must be `goodthink`.

Inside a loop:

- `nextrepeat` skips to the next iteration.
- `stoprepeat` exits the nearest loop.

`nextrepeat` and `stoprepeat` are only valid inside a `repeatwhile` block.

## 06. Routines

Routines are top-level declarations:

```newcode
routine numberthink addgood(numberthink first, numberthink second)
    reportvalue first plus second
endroutine
```

A routine declaration contains:

- `routine`
- a return type
- a routine name
- zero or more typed parameters
- a body
- `endroutine`

Routines that return a value must use `reportvalue`. Routine calls are
expressions, so they can appear inside declarations, assignments, output, or
other routine calls.

Routines cannot be nested, cannot be recursive, and cannot read global
variables. Pass values through parameters instead.

## 07. Silence Routines

`silencethink` marks a routine that returns no value:

```newcode
routine silencethink announce(wordthink message)
    speak message
endroutine
```

A `silencethink` call can be used as a statement:

```newcode
announce("Silence routine prints and returns no value.")
```

Because it returns no value, a `silencethink` routine should not be used where
an expression value is required.

## 08. Output and Precision

`speak` prints a line and can combine comma-separated items:

```newcode
speak "two digits: ", share to 2
```

Newcode does not insert spaces automatically. Put spaces in string literals
when you want spaces in the output.

`to` sets numeric precision for that printed number. `speaknumber` is stricter:
it accepts exactly one `numberthink` expression.

```newcode
speaknumber half to 1
```

## 09. Input

Input is expression-based:

```newcode
thought numberthink amount be listennumber
thought wordthink label be listenwords
```

`listennumber` reads one line and accepts an integer or decimal. It also accepts
the prefix form `minus 3`. `listenwords` reads one ASCII line and checks it
against the censorship lexicon.

`09_input.think` needs standard input, so run it with a pipe or type the two
lines interactively.

## Operator Precedence

The parser orders binary operators from low to high precedence:

| Precedence | Operators |
| --- | --- |
| 1 | `either` |
| 2 | `both` |
| 3 | `more`, `less`, `same` |
| 4 | `join` |
| 5 | `plus`, `minus` |
| 6 | `times`, `divide` |

Unary `un` and unary `minus` bind as primary expressions. Use parentheses for
clarity when combining unary operators with comparisons or arithmetic.

## Current Boundaries

The current implementation intentionally has no arrays, maps, objects, files,
modules, network access, implicit type conversion, or user-editable lexicon from
inside a program. This keeps the language small enough to study syntax, type
checking, and vocabulary control directly.
