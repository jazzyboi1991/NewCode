# Newcode 0.5 Examples

These examples show `trythink` error handlers and the final code-free
`othercrime` catch-all.

| File | Demonstrates | Command |
| --- | --- | --- |
| `20_trythink_handlers.think` | A specific handler and final catch-all | `run` |
| `21_multiple_handlers.think` | Separate `MATHCRIME`, `INDEXCRIME`, and `FILECRIME` handlers | `run` |
| `22_handler_propagation.think` | An error inside a handler propagating outward | `run` |
| `23_testcrime_handler.think` | Handling `TESTCRIME` from `testthink` | `test` |

```sh
python3 -m goodthink check "example/v0.5/20_trythink_handlers.think"
python3 -m goodthink run "example/v0.5/20_trythink_handlers.think"
python3 -m goodthink run "example/v0.5/21_multiple_handlers.think"
python3 -m goodthink run "example/v0.5/22_handler_propagation.think"
python3 -m goodthink test "example/v0.5/23_testcrime_handler.think"
```

The catchable codes are `MATHCRIME`, `INDEXCRIME`, `FILECRIME`, `INPUTCRIME`,
`WORDCRIME`, and `TESTCRIME`. `WORKLIMIT` always propagates.

## 한국어

이 예제들은 `trythink` 오류 handler와 마지막에 두는 코드 없는
`othercrime` catch-all을 보여 줍니다.

표의 `run`·`test`는 해당 명령으로 실행하며, 허용되는 handler 코드는
`MATHCRIME`, `INDEXCRIME`, `FILECRIME`, `INPUTCRIME`, `WORDCRIME`,
`TESTCRIME`입니다. `WORKLIMIT`은 항상 바깥으로 전파됩니다.
