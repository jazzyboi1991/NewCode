# Newcode 0.5 examples

`20_trythink_handlers.think`는 실행 오류를 지정해서 처리한 뒤, 마지막에
코드 없는 `othercrime` catch-all을 두는 방법을 보여 줍니다.

```sh
python3 -m goodthink check "example/v0.5/20_trythink_handlers.think"
python3 -m goodthink run "example/v0.5/20_trythink_handlers.think"
```

허용 handler 코드는 `MATHCRIME`, `INDEXCRIME`, `FILECRIME`, `INPUTCRIME`,
`WORDCRIME`, `TESTCRIME`입니다. `WORKLIMIT`은 포획되지 않습니다.
