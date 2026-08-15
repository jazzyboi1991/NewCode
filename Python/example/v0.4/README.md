# Newcode 0.4 예제

0.4은 새 언어 키워드를 만들지 않고, 기존 `use`·`call` 문법으로 표준 모듈을
사용합니다. `standard/` 경로는 실행기가 제공하는 예약 경로이므로 프로젝트 파일로
바꿀 수 없습니다.

- `17_randomthink.think`: 시드, 정수 난수, 난수 분수
- `18_timethink.think`: 로컬 시간 record와 epoch 초
- `19_paththink.think`: 안전한 상대 경로 조작과 파일 존재 확인

저장소 루트에서 실행합니다.

```sh
python3 -m goodthink run "Python/example/v0.4/17_randomthink.think"
python3 -m goodthink run "Python/example/v0.4/18_timethink.think"
python3 -m goodthink run "Python/example/v0.4/19_paththink.think"
```

`paththink`는 `/`를 쓰는 상대 경로만 허용합니다. 절대 경로·`..`·역슬래시는
`FILECRIME`을 발생시킵니다.
