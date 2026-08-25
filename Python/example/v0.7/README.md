# Newcode 0.7 Examples

`25_commandthink.think` demonstrates the `standard/commandthink.think` module.
The first program argument has index `0`.

```sh
python3 -m goodthink run "example/v0.7/25_commandthink.think" -- first second
python3 -m goodthink "example/v0.7/25_commandthink.think" -- first second
```

`arguments()` returns every value after `--` as a `listthink`.
`argument(index)` returns one `wordthink`; a missing position raises
`INPUTCRIME`. Command-line values are checked by the official censorship policy.

## 한국어

`25_commandthink.think`는 `standard/commandthink.think` 표준 모듈을 보여 줍니다.
첫 번째 프로그램 인자의 번호는 `0`입니다.

위 명령처럼 소스 파일 뒤의 `--` 다음에 프로그램 인자를 전달합니다.
`arguments()`는 모든 인자를 `listthink`로 반환하고, `argument(index)`는 하나의
`wordthink`를 반환합니다. 없는 위치는 `INPUTCRIME`이며 명령행 값에도 공식
검열 정책이 적용됩니다.
