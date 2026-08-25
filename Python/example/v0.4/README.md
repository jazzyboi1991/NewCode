# Newcode 0.4 Examples

Version 0.4 uses the existing `use` and `call` syntax for reserved standard
modules. The `standard/` paths are supplied by the interpreter.

- `17_randomthink.think`: seeds, integer random values, and random fractions
- `18_timethink.think`: local time records and Unix epoch seconds
- `19_paththink.think`: safe relative paths and regular-file existence checks

```sh
python3 -m goodthink run "Python/example/v0.4/17_randomthink.think"
python3 -m goodthink run "Python/example/v0.4/18_timethink.think"
python3 -m goodthink run "Python/example/v0.4/19_paththink.think"
```

`paththink` accepts only safe relative paths using `/`. Absolute paths, `..`,
and backslashes produce `FILECRIME`.

## 한국어

0.4에서는 새 언어 키워드를 만들지 않고 기존 `use`·`call` 문법으로 예약 표준
모듈을 사용합니다. `standard/` 경로는 실행기가 제공합니다.

- `17_randomthink.think`: 시드·정수 난수·난수 분수
- `18_timethink.think`: 로컬 시간 기록과 Unix epoch 초
- `19_paththink.think`: 안전한 상대 경로와 일반 파일 존재 확인

위 실행 명령으로 각 예제를 실행할 수 있습니다. `paththink`는 `/`를 사용하는
안전한 상대 경로만 허용하며 절대 경로·`..`·역슬래시는 `FILECRIME`을 발생시킵니다.
