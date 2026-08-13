# Newcode 초보자 예제

아래 순서대로 실행하면 Newcode의 기본 흐름을 단계별로 익힐 수 있습니다.

## 실행 준비

`NewCode/Python/` 디렉터리에서 모듈 명령으로 실행하면 명령이 짧습니다.

```sh
cd NewCode/Python
python3 -m goodthink check "example/For Beginners/01_calculator.think"
python3 -m goodthink run "example/For Beginners/01_calculator.think"
```

`check`는 문법과 자료형만 검사하고, `run`은 검사 후 실제로 실행합니다.
파일에 `newcode 0.2`를 적지 않아도 기본적으로 0.2 문법으로 실행됩니다.

## 학습 순서

### 1. 계산기

파일: `01_calculator.think`

- `thought`로 변수를 선언합니다.
- `numberthink`는 숫자 자료형입니다.
- `plus`로 덧셈을 합니다.
- `speak`로 결과를 출력합니다.

### 2. 점수 판정

파일: `02_conditionals.think`

- `more`로 두 숫자를 비교합니다.
- 비교 결과는 `goodthink` 값이 됩니다.
- `verify`와 `otherthink`로 조건에 따라 다른 문장을 실행합니다.

### 3. 할 일 목록

파일: `09_lists.think`

- `listthink(...)`로 목록을 만듭니다.
- `add`로 항목을 추가합니다.
- `foreach`로 목록을 순회합니다.
- `remove`로 항목을 삭제합니다.
- `size`로 목록의 항목 수를 확인합니다.

각 파일을 수정해 숫자, 문장, 목록 항목을 바꿔 보세요. 수정한 뒤에는 항상 `check`로 먼저 확인하고 `run`으로 실행하면 됩니다.

## 기능별 파일 목록

| 번호 | 파일 | 연습하는 기능 |
| --- | --- | --- |
| 01 | `01_calculator.think` | 변수, 숫자, 산술, 출력 |
| 02 | `02_conditionals.think` | 비교, 불리언, 조건문 |
| 03 | `03_strings.think` | 문자열, `join` |
| 04 | `04_loops.think` | `repeatwhile` |
| 05 | `05_routines.think` | 반환값 routine |
| 06 | `06_output.think` | 소수 자릿수 출력 |
| 07 | `07_input.think` | 숫자·문자열 입력 |
| 08 | `08_records.think` | 기록 자료형과 필드 수정 |
| 09 | `09_lists.think` | 목록, `foreach`, 추가·삭제 |
| 10 | `10_files.think` | 파일 쓰기·추가·읽기 |
| 11 | `11_modules_math.think` | 모듈 routine 정의 |
| 12 | `12_modules.think` | 모듈 불러오기와 호출 |
| 13 | `13_tests.think` | `testthink` |

입력이 필요한 `07_input.think`는 다음처럼 실행합니다.

```sh
printf '7\nAlpha\n' | PYTHONPATH=NewCode/Python python3 NewCode/Python/goodthink.py run "NewCode/Python/example/For Beginners/07_input.think"
```

파일·모듈 예제는 실행 폴더에 따라 결과가 달라질 수 있습니다. `10_files.think`는 현재 실행 폴더에 `beginner_note.txt`를 만들며, `11_modules_math.think`와 `12_modules.think`는 같은 폴더에 있어야 합니다.
