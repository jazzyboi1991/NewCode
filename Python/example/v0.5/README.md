# Newcode 0.5 examples

`20_trythink_handlers.think`는 실행 오류를 지정해서 처리한 뒤, 마지막에
코드 없는 `othercrime` catch-all을 두는 방법을 보여 줍니다.

| 파일 | 보여 주는 내용 | 실행 명령 |
| --- | --- | --- |
| `20_trythink_handlers.think` | 특정 오류와 마지막 catch-all | `run` |
| `21_multiple_handlers.think` | `MATHCRIME`, `INDEXCRIME`, `FILECRIME`별 처리 | `run` |
| `22_handler_propagation.think` | handler 내부 오류의 바깥 전파 | `run` |
| `23_testcrime_handler.think` | `testthink`의 `TESTCRIME` 처리 | `test` |

```sh
python3 -m goodthink check "example/v0.5/20_trythink_handlers.think"
python3 -m goodthink run "example/v0.5/20_trythink_handlers.think"
python3 -m goodthink run "example/v0.5/21_multiple_handlers.think"
python3 -m goodthink run "example/v0.5/22_handler_propagation.think"
python3 -m goodthink test "example/v0.5/23_testcrime_handler.think"
```

허용 handler 코드는 `MATHCRIME`, `INDEXCRIME`, `FILECRIME`, `INPUTCRIME`,
`WORDCRIME`, `TESTCRIME`입니다. `WORKLIMIT`은 포획되지 않습니다.
