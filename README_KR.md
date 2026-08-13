# Newcode

영문 문서: [README.md](README.md)

Newcode는 조지 오웰의 *1984*에 등장하는 신어(Newspeak)에서 영감을 받은 실험적인 프로그래밍 언어입니다. 이 언어는 어휘 통제를 언어 설계의 제약으로 다룹니다. 소스 코드는 의도적으로 작게 제한된 승인 어휘로 작성하며, 인터프리터는 금지된 단어·구문과 승인되지 않은 대체 표현을 거부합니다.

현재 프로젝트에는 Python 참조 구현이 들어 있습니다. 명령줄 프로그램의 이름은 `goodthink`이고 Newcode 소스 파일의 확장자는 `.think`입니다.

> 이 프로젝트는 검열과 사고 통제를 비판적으로 탐구하기 위한 언어 실험이며, 그러한 사상을 지지하기 위한 도구가 아닙니다.

## 현재 상태

언어 사양 버전은 **0.2**, Python 구현 버전은 **0.2.0**입니다. 실행 코드는 `Python/` 아래에 있으며, 복합 자료형·파일·모듈·개발 도구를 포함합니다.

현재 구현은 Python 참조 구현 0.2.0입니다. 0.1 예제의 하위 호환성을 유지하면서 복합 자료형, 파일, 모듈, 포맷·추적·토큰 검사 도구를 제공합니다.

## 요구 사항

- Python 3.11 이상을 권장합니다.
- 별도의 외부 Python 패키지는 필요하지 않습니다.

## CLI 실행

저장소 루트(`NewCode/`)에서는 다음처럼 실행합니다. 파일 경로는 현재 폴더
기준의 상대 경로 또는 `/`로 시작하는 절대 경로 모두 사용할 수 있습니다.

```sh
python3 -m goodthink version
python3 -m goodthink check "Python/example/For Beginners/01_calculator.think"
python3 -m goodthink run "Python/example/For Beginners/01_calculator.think"
```

`Python/` 디렉터리로 이동한 경우에는 경로에서 `Python/`을 빼야 합니다.

```sh
cd Python
python3 -m goodthink run "example/For Beginners/01_calculator.think"
```

저장소 루트에서는 기존 진입점도 사용할 수 있습니다.

```sh
PYTHONPATH=Python python3 Python/goodthink.py version
PYTHONPATH=Python python3 Python/goodthink.py check Python/example/v0.1/victory.think
PYTHONPATH=Python python3 Python/goodthink.py run Python/example/v0.1/victory.think
```

CLI는 다음 명령을 제공합니다.

```text
goodthink version
goodthink check <program.think>
goodthink run <program.think>
goodthink format [--write] <program.think>
goodthink inspect --tokens <program.think>
goodthink inspect --ast <program.think>
goodthink policy check "text"
goodthink test <program.think>
```

`check`는 프로그램을 실행하지 않고 lexing, parsing, 정적 검사를 수행합니다. `run`은 같은 검사를 수행한 다음 프로그램을 인터프리트합니다. 프로그램 파일의 확장자는 반드시 `.think`여야 합니다. 오류에는 진단 코드가 포함되며, 소스 위치를 확인할 수 있는 경우 해당 줄·열과 caret 표시도 함께 출력됩니다.

### CLI 명령 설명

- `version`: goodthink와 Newcode 버전을 출력합니다.
- `check`: 실행하지 않고 문법·자료형을 검사합니다. `--trace`를 붙이면 검사 단계를 표시합니다.
- `run`: 검사 후 프로그램을 실행합니다.
- `format`: 소스의 블록 들여쓰기를 출력합니다. `--write`를 붙이면 파일에 저장합니다.
- `inspect --tokens`: lexer가 만든 토큰과 위치를 출력합니다.
- `inspect --ast`: parser가 만든 AST를 출력합니다.
- `policy check "text"`: 문자열이 검열 정책을 통과하는지 검사합니다.
- `test`: `testthink` 블록만 격리된 환경에서 실행합니다.

### 파일 헤더

Newcode 0.2부터는 `newcode 0.2` 헤더를 생략할 수 있습니다. 헤더가 없으면 기본적으로 0.2 문법으로 해석됩니다. 0.1 호환 파일은 계속 `newcode 0.1`을 명시해야 합니다.

```newcode
thought numberthink count be 3
speak count
```

### 전역 명령 설치(선택 사항)

개발 환경에서 다음 명령으로 프로젝트를 설치하면 어느 폴더에서든 `goodthink`를 사용할 수 있습니다.

```sh
cd Python
python3 -m pip install --user -e .
goodthink run "example/For Beginners/01_calculator.think"
```

## Newcode 프로그램 예시

```newcode
newcode 0.1

routine numberthink addgood(numberthink first, numberthink second)
    reportvalue first plus second
endroutine

thought numberthink count be 3
thought goodthink approved be count more 0

verify approved
    speak "Victory count: ", addgood(count, 1)
otherthink
    speak "Ungood."
endverify
```

Newcode는 일반적인 프로그래밍 용어 대신 신어풍 키워드를 사용합니다.

| 목적           | Newcode 형식                                           |
| -------------- | ------------------------------------------------------ |
| 변수 선언·대입 | `thought ... be ...`                                   |
| 불리언 값      | `good`, `ungood`                                       |
| 조건문         | `verify`, `otherthink`, `endverify`                    |
| 반복문         | `repeatwhile`, `nextrepeat`, `stoprepeat`, `endrepeat` |
| 함수형 routine | `routine`, `reportvalue`, `endroutine`                 |
| 출력           | `speak`, `speaknumber`                                 |
| 입력           | `listennumber`, `listenwords`                          |
| 복합 자료형    | `listthink`, `recordthink`, `indexthink`               |
| 파일·모듈      | `readfile`, `writefile`, `appendfile`, `use`, `call`   |

## 언어 모델

Newcode 0.2는 0.1의 단순 변수와 routine을 유지하면서 `nothink`, `maybe`, 복합 자료형, `foreach`, 파일·모듈 기능을 추가하는 버전입니다.

Newcode 0.1에는 네 가지 명시적 자료형이 있습니다.

- `numberthink` — `fractions.Fraction`으로 내부 표현되는 정확한 정수·십진수 값
- `wordthink` — 공식 lexicon의 검사를 받는 ASCII 문자열
- `goodthink` — `good`와 `ungood` 불리언 값
- `silencethink` — 반환값이 없는 routine

수치 연산자는 `plus`, `minus`, `times`, `divide`입니다. 비교 연산자는 `more`, `less`, `same`이며, 불리언 연산자는 `both`, `either`, 단항 연산자 `un`입니다. `join`은 문자열을 연결한 뒤 결과를 즉시 검열 정책으로 다시 검사합니다.

문장은 줄바꿈으로 구분합니다. lexer는 `//`와 `/* ... */` 주석, ASCII 식별자, 십진수 리터럴, 문자열 안의 `\\n`, `\\t`, `\\"`, `\\\\` escape를 지원합니다. 블록은 `endverify`, `endrepeat`, `endroutine` 같은 종료 키워드로 닫습니다.

validator는 자료형 검사, 이름·스코프 검사, 중복 선언 검사, 반환 경로 검사, 직접·간접 재귀 거부를 수행합니다. runtime은 전역 스코프와 routine 지역 스코프를 관리하며, 기본적으로 `1_000_000`개의 실행 단계를 넘으면 실행을 중단합니다.

## 검열 정책

공식 정책은 [`Python/prohibited_words.json`](Python/prohibited_words.json)에 저장되어 있습니다. 소스 프로그램은 이 파일을 수정할 수 없습니다. 정책은 다음 세 부분으로 구성됩니다.

- `replacement_rules` — 승인된 Newcode 어휘로 바꿔야 하는 oldspeak 표현
- `prohibited_terms` — 허용되는 대체어가 없는 금지 단어
- `prohibited_phrases` — 전체 표현 단위로 거부되는 금지 구문

식별자, 문자열 리터럴, `listenwords` 입력이 검사 대상입니다. 매칭은 대소문자를 구분하지 않으며 일반적인 구분 문자와 leetspeak 변형을 정규화합니다. 또한 `join`으로 만들어진 문자열도 다시 검사하므로 문자열 연결로 정책을 우회할 수 없습니다.

대표적인 진단 코드는 `WORDCRIME`, `CRIMESTOP`, `THINKTYPE ERROR`, `THINKLOGIC ERROR`, `MATHCRIME`, `INPUTCRIME`, `LOOPTHINK`, `WORKLIMIT`입니다.

## 저장소 구조

```text
NewCode/
├── Python/
│   ├── goodthink.py              # CLI 진입점
│   ├── prohibited_words.json     # 공식 검열 lexicon
│   ├── test_parser.py            # parser 인접 결함 회귀 테스트
│   ├── test_newcode02.py         # 0.2 자료형·파일·모듈·예외 테스트
│   ├── example/
│   │   ├── For Beginners/        # 기능별 초보자 예제
│   │   ├── v0.1/                 # 0.1 회귀 예제와 문법 문서
│   │   └── v0.2/                 # 0.2 모듈·테스트 예제
│   └── newcode/
│       ├── cli.py                # 인자 처리와 명령 실행 조정
│       ├── lexer.py              # 토큰, 리터럴, 주석, 어휘 검사
│       ├── parser.py             # AST 구성
│       ├── model.py              # AST·토큰 data class와 십진수 처리
│       ├── validator.py          # 정적 검사와 자료형 분석
│       ├── runtime.py            # 인터프리터와 출력 형식화
│       ├── censor.py             # lexicon 로드와 매칭
│       ├── errors.py             # 소스 위치와 진단
│       └── __init__.py            # 버전과 실행 제한
├── README.md
└── README_KR.md
```

구현 파이프라인은 다음과 같습니다.

```text
source.think
   → Censor + Lexer
   → Parser / AST
   → Validator
   → Runtime
```

## 의도적인 제한

0.2에서는 목록·기록·맵, 파일, 모듈을 지원하지만 네트워크 접근, 복소수, 암시적 자료형 변환, 공식 lexicon 변경은 여전히 제공하지 않습니다. 이 제한은 실험의 일부입니다. 제한된 어휘가 프로그램의 형태를 어떻게 바꾸는지 관찰할 수 있도록 언어의 표현 범위를 의도적으로 좁혔습니다.

## 개발 참고 사항

현재 저장소에는 작은 `unittest` 회귀 테스트가 있으며, 패키징 메타데이터는 없습니다. 언어를 확장할 때는 다음 모듈 경계를 유지하는 것이 좋습니다.

1. 문법 변경은 `lexer.py`와 `parser.py`에 반영합니다.
2. 새로운 문법 구조는 `model.py`에 표현합니다.
3. 정적 규칙은 `validator.py`에서 검사합니다.
4. 실행 의미론은 `runtime.py`에 구현합니다.
5. 어휘 규칙을 바꾸면 lexicon과 설계 문서도 함께 갱신합니다.

가장 실용적인 다음 작업은 토큰화·parsing, 검열, 자료형 오류, 제어 흐름, routine, runtime 경계 조건에 대한 회귀 테스트를 넓히는 것입니다.
