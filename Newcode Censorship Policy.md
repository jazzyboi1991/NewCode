# Newcode Censorship Policy

Newcode is an educational and critical experiment inspired by the controlled
vocabulary of Newspeak. This policy documents the behavior of the reference
interpreter; it is not an endorsement of censorship or political repression.

## Official lexicon

The official lexicon is [`Python/prohibited_words.json`](Python/prohibited_words.json).
Source programs cannot replace, extend, or modify it at runtime. Changes to the
lexicon are repository changes and must include schema validation and regression
tests.

The lexicon has three primary rule groups:

- `replacement_rules`: oldspeak words that have an approved Newcode replacement.
  These rules cover adjective-like evaluation, emotion, thought, character, and
  loyalty vocabulary, including regular Newspeak-style replacements.
- `prohibited_terms`: sensitive words with no accepted replacement. Categories
  include political dissent, historical memory, religion, regime criticism,
  violence, profanity, privacy, and foreign contact.
- `prohibited_phrases`: phrases rejected as a whole, including political,
  historical, privacy, and oldspeak-intensity expressions.

Replacement rules are organized by lexical category rather than by unrestricted
synonym generation. A replacement is an explicit policy entry; the interpreter
does not invent one.

## Diagnostic behavior

Every prohibited term, phrase, or oldspeak replacement is an immediate
`WORDCRIME`. Newcode does not distinguish a non-blocking warning from a blocking
error for these rules. When an approved replacement exists, the diagnostic names
it so the user can rewrite the source.

## When checking happens

- Identifiers and variable names are checked during lexing.
- Source string literals are checked during lexing.
- `listenwords` input is checked after it is read.
- `join`, string replacement, line joining, and other generated text are checked
  when the result is produced.
- `speak` values are checked immediately before output.
- File contents are checked when read text is used or displayed, and file values
  are checked immediately before writing.
- Module and file paths receive both the normal string policy check and the safe
  relative-path check.
- Numbers and comments are not policy-checked.

Matching is case-insensitive. The normalizer handles the supported leetspeak
substitutions and separator normalization, so changing case or inserting common
visual substitutions is not an approved bypass.

## Scope and future work

The official policy is intentionally fixed for reproducible experiments. A
future settings file must not silently alter the language vocabulary or the
official lexicon. Improvements to `goodthink policy` may expose explanations or
validation results, but the language itself will not gain aliases or abbreviated
spellings as a result.
