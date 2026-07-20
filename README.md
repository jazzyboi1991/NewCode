# Newcode

Newcode is an executable programming-language experiment inspired by the controlled vocabulary and bureaucratic tone of *Nineteen Eighty-Four*. Its official runner is `goodthink`; Newcode source files use the `.think` extension.

This final 0.1 release contains a Rust command-line runner and a browser edition written in TypeScript. The censorship policy is deliberately data-driven: edit [`prohibited_words.json`](prohibited_words.json) to adjust the official sensitive-language and oldspeak-replacement rules.

## Run the command-line runner

Rust 1.85 or newer is required.

```sh
cargo build --release
./target/release/goodthink version
./target/release/goodthink check examples/victory.think
./target/release/goodthink run examples/victory.think
```

`check` validates syntax, the censorship policy, routine declarations, and recursion before running anything. `run` then executes the program, reporting validation and execution times. Errors use `file: line, column: ERROR: message` followed by a source caret.

## Use the browser edition

```sh
cd web
npm install
npm run build
cd ..
python3 -m http.server 8000
```

Open [http://127.0.0.1:8000/web/](http://127.0.0.1:8000/web/). Serving from the repository root lets the page load the shared `prohibited_words.json` file.

## A small program

```newcode
newcode 0.1

thought numberthink count be 3
thought numberthink share be 1 divide 3

routine numberthink addgood(numberthink first, numberthink second)
    reportvalue first plus second
endroutine

verify count more 0
    speak "Approved count: ", addgood(count, 1)
    speak "Share: ", share to 2
otherthink
    speak "Ungood."
endverify
```

The language supports exact decimal arithmetic in the Rust runner, `verify` / `otherthink`, `repeatwhile`, typed routines, `listennumber`, `listenwords`, C-style comments, and `join`. See [`docs/계획서.md`](docs/%EA%B3%84%ED%9A%8D%EC%84%9C.md) for the complete 0.1 language definition and [`examples/`](examples/) for runnable examples.

## Current boundary

Newcode 0.1 intentionally has no arrays, maps, files, modules, network access, or complex numbers. Complex-number support is reserved for a future version.
