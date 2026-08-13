# Newcode 오류 예제 문법 설명

이 폴더의 프로그램은 정상 실행 예제가 아닙니다. 각 파일은 **하나의 오류를
의도적으로 발생**시키도록 작성되었습니다. 오류 메시지가 출력되면 예제가
정상적으로 동작한 것입니다.

## 실행 방법

저장소 루트인 `NewCode/`에서 실행합니다.

```sh
python -m goodthink check "Python/example/v0.2/Errors/01_wordcrime.think"
```

문법·정적 검사에서 발생하는 오류는 `check`, 실행 중 발생하는 오류는 `run`,
테스트 격리 오류는 `test`를 사용합니다. 입력이 필요한 예제는 입력을 파이프로
전달합니다.

| 번호 | 파일 | 명령 | 예상 오류 |
| --- | --- | --- | --- |
| 01 | `01_wordcrime.think` | `check` | `WORDCRIME` |
| 02 | `02_crimestop.think` | `check` | `CRIMESTOP` |
| 03 | `03_thinktype_error.think` | `check` | `THINKTYPE ERROR` |
| 04 | `04_thinklogic_error.think` | `check` | `THINKLOGIC ERROR` |
| 05 | `05_mathcrime.think` | `run` | `MATHCRIME` |
| 06 | `06_inputcrime.think` | `run` | `INPUTCRIME` |
| 07 | `07_loopthink.think` | `check` | `LOOPTHINK` |
| 08 | `08_worklimit.think` | `run` | `WORKLIMIT` |
| 09 | `09_indexcrime.think` | `run` | `INDEXCRIME` |
| 10 | `10_filecrime.think` | `run` | `FILECRIME` |
| 11 | `11_modulecrime.think` | `check` | `MODULECRIME` |
| 12 | `12_testcrime.think` | `test` | `TESTCRIME` |

---

## 01. 금지 단어 — `01_wordcrime.think`

### 전체 코드

```newcode
// 금지된 단어를 문자열에 넣어 WORDCRIME을 발생시킵니다.
newcode 0.2
speak "freedom"
```

### 문법 설명

- `speak`는 값을 출력하는 명령입니다.
- 문자열은 큰따옴표로 감쌉니다.
- Newcode는 문자열도 공식 검열 목록으로 검사합니다.
- `freedom`은 금지된 단어이므로 lexer 단계에서 `WORDCRIME`이 발생합니다.

실행:

```sh
python -m goodthink check "Python/example/v0.2/Errors/01_wordcrime.think"
```

---

## 02. 중복 선언 — `02_crimestop.think`

### 전체 코드

```newcode
// 같은 이름을 두 번 선언해 CRIMESTOP을 발생시킵니다.
newcode 0.2
thought numberthink count be 1
thought numberthink count be 2
```

### 문법 설명

- `thought numberthink count be 1`은 숫자 변수 `count`를 선언합니다.
- 같은 범위에서 같은 이름을 다시 선언할 수 없습니다.
- 두 번째 선언이 정적 검사에서 `CRIMESTOP`을 발생시킵니다.

실행:

```sh
python -m goodthink check "Python/example/v0.2/Errors/02_crimestop.think"
```

---

## 03. 자료형 오류 — `03_thinktype_error.think`

### 전체 코드

```newcode
// numberthink 변수에 문자열을 대입해 THINKTYPE ERROR를 발생시킵니다.
newcode 0.2
thought numberthink score be 100
thought score be "one hundred"
```

### 문법 설명

- `score`는 처음에 `numberthink`로 선언되었습니다.
- 선언 뒤의 `thought score be ...`는 기존 변수에 값을 대입합니다.
- `"one hundred"`는 `wordthink`이므로 숫자 변수에 넣을 수 없습니다.
- 자료형이 맞지 않아 `THINKTYPE ERROR`가 발생합니다.

실행:

```sh
python -m goodthink check "Python/example/v0.2/Errors/03_thinktype_error.think"
```

---

## 04. 문법 구조 오류 — `04_thinklogic_error.think`

### 전체 코드

```newcode
// verify를 닫지 않아 THINKLOGIC ERROR를 발생시킵니다.
newcode 0.2
verify 1 same 1
    speak "block"
```

### 문법 설명

- `verify`는 조건문을 시작합니다.
- `1 same 1`은 두 숫자가 같은지 비교하는 조건식입니다.
- 조건문은 반드시 `endverify`로 닫아야 합니다.
- 종료 단어가 없으므로 parser가 `THINKLOGIC ERROR`를 발생시킵니다.

실행:

```sh
python -m goodthink check "Python/example/v0.2/Errors/04_thinklogic_error.think"
```

---

## 05. 0으로 나누기 — `05_mathcrime.think`

### 전체 코드

```newcode
// 0으로 나누어 MATHCRIME을 발생시킵니다.
newcode 0.2
speak 10 divide 0
```

### 문법 설명

- `divide`는 나눗셈 연산자입니다.
- 수학적으로 0으로 나눌 수 없으므로 실행 중 오류가 발생합니다.
- 이 오류는 문법 오류가 아니므로 `check`는 통과하고 `run`에서
  `MATHCRIME`이 발생합니다.

실행:

```sh
python -m goodthink run "Python/example/v0.2/Errors/05_mathcrime.think"
```

---

## 06. 잘못된 입력 — `06_inputcrime.think`

### 전체 코드

```newcode
// 숫자로 읽을 수 없는 입력을 주면 INPUTCRIME이 발생합니다.
newcode 0.2
speak listennumber
```

### 문법 설명

- `listennumber`는 입력 한 줄을 숫자로 변환합니다.
- `not-a-number`는 숫자 형식이 아니므로 변환할 수 없습니다.
- 입력 변환 실패는 `INPUTCRIME`입니다.

실행:

```sh
printf 'not-a-number\\n' | python -m goodthink run "Python/example/v0.2/Errors/06_inputcrime.think"
```

---

## 07. 순환 모듈 import — `07_loopthink.think`

### 전체 코드

```newcode
// 자기 자신을 모듈로 불러 순환 import를 만들어 LOOPTHINK를 발생시킵니다.
newcode 0.2
use loopgood from "07_loopthink.think"
```

### 문법 설명

- `use 이름 from "파일"`은 모듈을 불러오는 문법입니다.
- 이 예제는 자기 자신을 다시 불러옵니다.
- 모듈을 읽는 과정이 끝나기 전에 같은 파일을 다시 만나므로
  `LOOPTHINK`가 발생합니다.

실행:

```sh
python -m goodthink check "Python/example/v0.2/Errors/07_loopthink.think"
```

---

## 08. 실행 한도 초과 — `08_worklimit.think`

### 전체 코드

```newcode
// 조건이 계속 참인 반복문으로 WORKLIMIT을 발생시킵니다.
newcode 0.2
repeatwhile good
endrepeat
```

### 문법 설명

- `repeatwhile good`은 조건이 항상 참인 반복문입니다.
- 반복문 안에서 조건을 거짓으로 바꾸는 문장이 없습니다.
- interpreter는 무한 실행을 막기 위해 실행 단계 제한을 둡니다.
- 제한을 넘으면 `WORKLIMIT`이 발생합니다.

실행:

```sh
python -m goodthink run "Python/example/v0.2/Errors/08_worklimit.think"
```

실행 제한에 도달하기까지 잠시 걸릴 수 있습니다.

---

## 09. 범위를 벗어난 위치 — `09_indexcrime.think`

### 전체 코드

```newcode
// 목록에 없는 위치를 읽어 INDEXCRIME을 발생시킵니다.
newcode 0.2
thought listthink values be listthink(1, 2)
speak get values at 2
```

### 문법 설명

- 목록의 위치는 0부터 시작합니다.
- 두 항목의 유효한 위치는 0과 1입니다.
- `get values at 2`는 존재하지 않는 위치를 읽으려 합니다.
- 잘못된 위치 접근은 `INDEXCRIME`입니다.

실행:

```sh
python -m goodthink run "Python/example/v0.2/Errors/09_indexcrime.think"
```

---

## 10. 허용되지 않은 파일 경로 — `10_filecrime.think`

### 전체 코드

```newcode
// 실행 폴더 밖으로 나가는 경로를 사용해 FILECRIME을 발생시킵니다.
newcode 0.2
speak readfile "../outside.txt"
```

### 문법 설명

- `readfile`은 텍스트 파일을 읽습니다.
- 파일 접근은 실행 폴더 아래의 상대 경로만 허용됩니다.
- `../`는 실행 폴더 밖으로 이동하려는 경로입니다.
- 안전하지 않은 경로는 파일을 읽기 전에 `FILECRIME`으로 차단됩니다.

실행:

```sh
python -m goodthink run "Python/example/v0.2/Errors/10_filecrime.think"
```

---

## 11. 잘못된 모듈 구조 — `11_modulecrime.think`

### 전체 코드

```newcode
// top-level 출력이 있는 모듈을 불러 MODULECRIME을 발생시킵니다.
newcode 0.2
use modulegood from "11_modulecrime_source.think"
```

보조 파일 `11_modulecrime_source.think`의 내용:

```newcode
// 이 파일은 모듈 오류를 일으키기 위한 보조 파일입니다.
newcode 0.2
speak "modules may contain routines only"
```

### 문법 설명

- `use`는 같은 폴더의 모듈 파일을 불러옵니다.
- Newcode 0.2 모듈은 routine만 공개할 수 있습니다.
- 보조 모듈의 top-level `speak`는 허용되지 않습니다.
- 잘못된 모듈 구조는 `MODULECRIME`입니다.
- 두 파일이 같은 폴더에 있어야 합니다.

실행:

```sh
python -m goodthink check "Python/example/v0.2/Errors/11_modulecrime.think"
```

---

## 12. 테스트 격리 위반 — `12_testcrime.think`

### 전체 코드

```newcode
// testthink 안에서 입력을 시도해 TESTCRIME을 발생시킵니다.
newcode 0.2
testthink "input is not isolated"
    speak listennumber
endtestthink
```

### 문법 설명

- `testthink`는 독립된 테스트 블록을 시작합니다.
- 테스트는 외부 입력에 의존하지 않도록 격리됩니다.
- `listennumber`로 입력을 시도하면 `TESTCRIME`이 발생합니다.
- 테스트 블록은 `endtestthink`으로 닫습니다.

실행:

```sh
python -m goodthink test "Python/example/v0.2/Errors/12_testcrime.think"
```

## 오류를 학습하는 방법

1. 먼저 README의 예상 오류 코드와 실제 출력이 같은지 확인합니다.
2. 오류가 발생한 줄과 열을 살펴봅니다.
3. 오류를 일으킨 문장을 주석 처리하거나 올바르게 고쳐 봅니다.
4. `check`가 통과한 뒤 `run` 또는 `test`를 다시 실행합니다.
5. 일반 기능 예제는 `../For Beginners/` 폴더에서 참고합니다.
