# Changelog

Newcode와 Python 참조 구현의 주요 변경 사항을 기록합니다.

## [Unreleased]

## [0.7.0] — 2026-08-25

### Added

- `standard/commandthink.think`의 `arguments()`와 `argument(index)`를 추가했습니다.
- `goodthink run file.think -- ...` 및 파일명 단축형의 프로그램 인자 전달을 지원합니다.
- 공식 검열 lexicon을 설치 패키지 리소스로 포함하고 wheel·sdist 검증을 추가했습니다.
- Python 3.11~3.14 GitHub Actions 회귀 검증을 추가했습니다.

### Compatibility

- 헤더 없는 프로그램은 Newcode 0.7로 해석하며 `newcode 0.1`~`newcode 0.6`을 계속 지원합니다.
- 언어 명령어 별칭·축약형, 설정 파일, 추적 기능은 추가하지 않았습니다.

## [0.6.0] — 2026-08-20

### Added

- 이름 있는 `recordthink` 자료형 선언과 필수 필드 생성자를 추가했습니다.
- 사용자 정의 자료형의 중첩·목록·`maybe` 조합과 필드 읽기·수정을 지원합니다.
- 사용자 정의 자료형 예제와 회귀 테스트를 추가했습니다.

### Changed

- 헤더 없는 프로그램은 Newcode 0.6으로 해석합니다.
- 정의되지 않은 자료형과 잘못된 필드 생성은 기존 `THINKTYPE ERROR`와
  `THINKLOGIC ERROR`로 진단합니다.

### Compatibility

- `newcode 0.1`~`newcode 0.5` 헤더를 계속 지원합니다.
- 명령행 인자·환경 설정·디버거와 언어 명령어 축약형은 추가하지 않았습니다.

## [0.5.0] — 2026-08-18

### Added

- `othercrime CODE` 실행 오류 handler와 마지막 catch-all을 구현했습니다.
- 허용 오류 코드·중복 handler·catch-all 순서 진단을 추가했습니다.
- `WORKLIMIT`은 handler가 포획하지 않고 즉시 전파합니다.

### Compatibility

- 헤더 없는 파일은 Newcode 0.5로 해석하며 `newcode 0.1`~`newcode 0.4`를 계속 지원합니다.
- 언어 명령어의 별칭·축약형과 반복문 문법은 추가하지 않았습니다.

## [0.4.0] — 2026-08-16

### Added

- 예약된 `standard/` 표준 모듈 레지스트리를 추가했습니다.
- `randomthink`의 시드, 정수 난수, 정확한 난수 분수를 추가했습니다.
- `timethink`의 로컬 시간 record와 Unix epoch 초를 추가했습니다.
- `paththink`의 안전한 상대 경로 조합·분해·일반 파일 존재 확인을 추가했습니다.
- 0.4 표준 모듈 예제와 회귀 테스트를 추가했습니다.

### Changed

- 헤더 없는 프로그램은 Newcode 0.4로 해석합니다.
- 파일 명령과 `paththink`가 같은 상대 경로 보안 검사를 사용합니다.

### Compatibility

- `newcode 0.1`~`newcode 0.3` 헤더를 계속 지원합니다.
- 언어 명령어의 별칭·축약형을 추가하지 않았습니다.

## [0.3.0] — 2026-08-13

### Added

- 문자열 `length(...)`, `find(...)`, `replace(...)`, `split(...)`, `joinwords(...)`
  표현식을 추가했습니다.
- `"""..."""` 여러 줄 문자열을 지원합니다.
- `r`, `b`, `f`, `v`를 포함한 확장 문자열 escape를 지원합니다.
- 중첩 `recordthink`와 중복 필드 검사를 지원합니다.
- 기록·목록 값을 출력할 때 내부 문자열도 검열합니다.
- 모듈 파일 누락, 순환 import, 안전하지 않은 경로를 `MODULECRIME`으로
  진단합니다.
- CLI 단축형을 추가했습니다.

```text
goodthink program.think
goodthink -c program.think
goodthink -f program.think
goodthink -t program.think
goodthink --tokens program.think
goodthink --ast program.think
goodthink --policy "text"
```

- `python -m goodthink` 실행 진입점과 Python 패키징 설정을 추가했습니다.
- 0.3 문자열·기록·여러 줄 문자열 예제를 추가했습니다.
- 오류별 학습 예제와 문법 설명 문서를 추가했습니다.

### Compatibility

- `newcode 0.1`과 `newcode 0.2` 헤더를 계속 지원합니다.
- 기존 언어 명령어에는 별칭이나 축약형을 추가하지 않았습니다.
- 헤더가 없는 프로그램은 기본적으로 Newcode 0.3으로 해석합니다.

### Testing

- 전체 Python 회귀 테스트를 72개로 확장했습니다.
- CLI 단축형, 문자열 검열, 중첩 기록, 모듈 오류, formatter 보존을 검증합니다.

## [0.2.0] — 2026-08-12

### Added

- `listthink`, `recordthink`, `indexthink` 복합 자료형을 추가했습니다.
- `nothink`, `maybe` 자료형 규칙을 추가했습니다.
- 목록·기록·맵의 읽기, 수정, 추가, 삭제, 순회를 지원합니다.
- 상대 경로 텍스트 파일 입출력을 지원합니다.
- routine 공개 모듈과 이름공간 호출을 지원합니다.
- `trythink`, `othercrime`, `testthink`를 추가했습니다.
- `format`, `inspect`, `policy`, `test` 개발 도구를 추가했습니다.
- `INDEXCRIME`, `FILECRIME`, `MODULECRIME`, `TESTCRIME` 진단을 추가했습니다.

### Compatibility

- 0.1의 변수·조건·반복·routine 프로그램을 계속 실행할 수 있습니다.

## [0.1.0] — 2026-07-21

### Added

- Newcode Python 참조 인터프리터를 처음 구현했습니다.
- `thought`, `verify`, `otherthink`, `repeatwhile`, `routine` 기본 문법을
  지원했습니다.
- `numberthink`, `wordthink`, `goodthink`, `silencethink` 자료형을 추가했습니다.
- 숫자 연산, 문자열 결합, 입력, 출력, 소수 자릿수 출력을 지원했습니다.
- Newspeak-inspired 검열 정책과 `WORDCRIME` 진단을 도입했습니다.
