# Newcode 0.7 examples

`25_commandthink.think` demonstrates the `standard/commandthink.think` module.
The first user argument is index `0`.

```sh
python -m newcode.cli run 25_commandthink.think -- first second
goodthink 25_commandthink.think -- first second
```

`arguments()` returns every value after `--` as a `listthink`. `argument(index)`
returns one `wordthink`; a missing position raises `INPUTCRIME`.
