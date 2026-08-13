# Newcode 초보자 문법 설명

이 문서는 `For Beginners` 폴더의 예제를 위에서부터 따라가며 Newcode 0.2의
기본 문법을 익히도록 구성되어 있습니다. 각 예제는 한 가지 기능에 집중하며,
코드 전체를 그대로 실행할 수 있습니다.

## 실행 방법

저장소 루트인 `NewCode/`에서 실행합니다.

```sh
python -m goodthink check "Python/example/For Beginners/01_calculator.think"
python -m goodthink run "Python/example/For Beginners/01_calculator.think"
```

`check`는 실행하지 않고 문법과 자료형을 검사합니다. `run`은 검사한 뒤 실제로
실행합니다. 파일 경로는 현재 위치 기준의 상대 경로나 절대 경로를 사용할 수
있습니다.

모든 예제는 `newcode 0.2`를 적었지만, 0.2에서는 헤더를 생략해도 기본적으로
0.2 문법으로 해석됩니다.

## 공통 문법

| 목적 | 문법 |
| --- | --- |
| 변수 선언 | `thought 자료형 이름 be 값` |
| 기존 변수 대입 | `thought 이름 be 값` |
| 출력 | `speak 값` |
| 조건문 | `verify 조건 ... otherthink ... endverify` |
| 반복문 | `repeatwhile 조건 ... endrepeat` |
| routine 반환 | `reportvalue 값` |
| 주석 | `// 주석` 또는 `/* 주석 */` |

자료형은 숫자 `numberthink`, 문자열 `wordthink`, 불리언 `goodthink`, 목록
`listthink`, 기록 `recordthink` 등을 사용합니다. 문장은 줄바꿈으로 구분하고,
블록은 반드시 `endverify`, `endrepeat` 같은 종료 단어로 닫습니다.

---

## 01. 숫자와 변수 — `01_calculator.think`

### 전체 코드

```newcode
// 초보자용 첫 번째 예제: 숫자를 저장하고 계산합니다.
newcode 0.2

// 두 개의 숫자를 변수에 저장합니다.
thought numberthink first be 8
thought numberthink second be 3

// plus로 덧셈을 수행하고 결과를 새 변수에 저장합니다.
thought numberthink total be first plus second

// 문자열과 숫자를 함께 출력할 수 있습니다.
speak "first: ", first
speak "second: ", second
speak "total: ", total
```

### 문법 설명

- `thought numberthink first be 8`은 `first`라는 숫자 변수를 선언합니다.
- 선언할 때는 자료형을 적고, 이후 대입할 때는 자료형을 생략합니다.
- `plus`는 덧셈 연산자입니다. 뺄셈·곱셈·나눗셈은 `minus`, `times`, `divide`를
  사용합니다.
- `speak`의 쉼표는 여러 값을 붙여 출력한다는 뜻입니다. 공백은 자동으로
  들어가지 않으므로 문자열 안에 직접 적습니다.

---

## 02. 조건문과 불리언 — `02_conditionals.think`

### 전체 코드

```newcode
// 초보자용 두 번째 예제: 조건문으로 점수를 판정합니다.
newcode 0.2

// 점수를 저장하고, 60점 이상인지 불리언 값으로 기록합니다.
thought numberthink score be 75
thought goodthink passed be score more 60

// passed가 good이면 첫 번째 블록을 실행합니다.
verify passed
    speak "result: passed"
otherthink
    // passed가 ungood이면 otherthink 블록을 실행합니다.
    speak "result: try again"
endverify
```

### 문법 설명

- `good`와 `ungood`은 `goodthink` 자료형의 두 값입니다.
- `more`는 왼쪽 값이 오른쪽보다 큰지 비교합니다. `less`와 `same`도 사용할
  수 있습니다.
- `verify`의 조건이 `good`이면 첫 블록을 실행합니다.
- 조건이 `ungood`이면 선택 사항인 `otherthink` 블록을 실행합니다.
- 조건문은 `endverify`로 닫습니다.

---

## 03. 문자열과 `join` — `03_strings.think`

### 전체 코드

```newcode
// 문자열 변수와 join을 연습합니다.
newcode 0.2

thought wordthink greeting be "Good"
thought wordthink name be "thinker"
thought wordthink message be greeting join ", " join name

speak message
```

### 문법 설명

- 문자열은 큰따옴표로 감싸고 `wordthink` 변수에 저장합니다.
- `join`은 문자열 두 개를 이어 붙입니다.
- `greeting join ", " join name`은 세 문자열을 차례로 합칩니다.
- 문자열은 검열 정책의 검사 대상이므로 금지된 단어를 넣을 수 없습니다.

---

## 04. 반복문 — `04_loops.think`

### 전체 코드

```newcode
// repeatwhile로 같은 작업을 여러 번 실행합니다.
newcode 0.2

thought numberthink count be 1

repeatwhile count less 4
    speak "count: ", count
    thought count be count plus 1
endrepeat
```

### 문법 설명

- `repeatwhile`은 조건이 `good`인 동안 본문을 반복합니다.
- 반복 조건은 반드시 `goodthink` 값이어야 합니다.
- 반복 안에서 `count`를 1씩 증가시켜 언젠가 조건이 거짓이 되게 합니다.
- `endrepeat`를 빠뜨리면 `THINKLOGIC ERROR`가 발생합니다.

---

## 05. 반환값 routine — `05_routines.think`

### 전체 코드

```newcode
// 값을 반환하는 routine을 정의하고 호출합니다.
newcode 0.2

routine numberthink addgood(numberthink first, numberthink second)
    reportvalue first plus second
endroutine

speak "answer: ", addgood(4, 6)
```

### 문법 설명

- `routine numberthink addgood(...)`은 숫자를 반환하는 routine을 선언합니다.
- 매개변수에도 자료형을 명시합니다.
- `reportvalue`는 routine의 결과를 반환합니다.
- routine 정의는 `endroutine`으로 닫습니다.
- `addgood(4, 6)`처럼 이름 뒤에 괄호를 붙여 호출합니다.

---

## 06. 소수 자릿수 출력 — `06_output.think`

### 전체 코드

```newcode
// 일반 출력과 소수 자릿수 출력을 연습합니다.
newcode 0.2

thought numberthink share be 1 divide 3
speak "rounded: ", share to 2
speaknumber share to 4
```

### 문법 설명

- `divide`로 나눗셈을 수행합니다.
- `to 2`는 해당 숫자를 소수점 둘째 자리까지 반올림해 출력합니다.
- `speak`는 문자열과 숫자를 함께 출력할 수 있습니다.
- `speaknumber`는 숫자 출력에 사용하는 명령입니다.

---

## 07. 입력 — `07_input.think`

### 전체 코드

```newcode
// 숫자와 문자열을 입력받습니다.
newcode 0.2

thought numberthink amount be listennumber
thought wordthink label be listenwords

speak "amount: ", amount
speak "label: ", label
```

### 문법 설명

- `listennumber`는 숫자 입력을 받아 `numberthink` 값으로 변환합니다.
- `listenwords`는 한 줄의 문자열을 받아 `wordthink` 값으로 저장합니다.
- 잘못된 숫자를 입력하면 `INPUTCRIME`이 발생합니다.

실행 예:

```sh
printf '7\\nAlpha\\n' | python -m goodthink run "Python/example/For Beginners/07_input.think"
```

---

## 08. 기록 자료형 — `08_records.think`

### 전체 코드

```newcode
// recordthink로 이름이 있는 값을 묶습니다.
newcode 0.2

thought recordthink person be recordthink(name be "Ada", score be 10)
change person field score be 12

speak get person field name, ": ", get person field score
```

### 문법 설명

- `recordthink(...)`은 필드 이름과 값을 묶는 기록 자료형입니다.
- `name be "Ada"`처럼 필드를 작성합니다.
- `get person field name`은 `person` 기록의 `name` 필드를 읽습니다.
- `change person field score be 12`는 필드 값을 수정합니다.

---

## 09. 목록과 순회 — `09_lists.think`

### 전체 코드

```newcode
// 초보자용 세 번째 예제: 목록을 만들고 순회하고 수정합니다.
newcode 0.2

// listthink는 여러 값을 순서대로 담는 목록 자료형입니다.
thought listthink tasks be listthink("read", "practice")

// add로 목록의 마지막에 새 항목을 추가합니다.
add "review" to tasks

// foreach는 목록의 위치와 값을 차례로 꺼냅니다.
foreach position, task in tasks
    speak position, ": ", task
endforeach

// 목록의 첫 번째 항목을 삭제합니다.
remove tasks at 0
speak "remaining: ", size tasks
```

### 문법 설명

- `listthink(...)`은 여러 값을 순서대로 담는 목록입니다.
- `add 값 to 목록`은 목록의 끝에 값을 추가합니다.
- `foreach position, task in tasks`는 위치와 값을 하나씩 꺼냅니다.
- `remove tasks at 0`은 0번 위치의 값을 삭제합니다. 목록의 첫 위치는 0입니다.
- `size tasks`는 목록의 항목 개수를 반환합니다.

---

## 10. 파일 입출력 — `10_files.think`

### 전체 코드

```newcode
// 실행 폴더 아래의 텍스트 파일을 읽고 씁니다.
newcode 0.2

writefile "beginner_note.txt" be "first line"
appendfile "beginner_note.txt" be "\\nsecond line"
thought rawthink note be readfile "beginner_note.txt"

// 파일 내용은 lines로 목록으로 바꿀 수 있습니다.
thought listthink parts be lines note
speak size parts
```

### 문법 설명

- `writefile`은 파일을 새로 쓰거나 기존 내용을 덮어씁니다.
- `appendfile`은 기존 파일의 끝에 내용을 추가합니다.
- `readfile`은 텍스트 파일을 읽어 `rawthink` 값으로 가져옵니다.
- `lines`는 문자열을 줄 목록으로 바꿉니다.
- 파일 경로는 실행 폴더 아래의 상대 경로만 허용됩니다. `../`나 절대 경로는
  `FILECRIME`이 됩니다.

이 예제를 실행하면 실행 폴더에 `beginner_note.txt`가 만들어집니다.

---

## 11. 모듈 routine 정의 — `11_modules_math.think`

### 전체 코드

```newcode
// 다른 파일에서 불러올 routine을 정의하는 모듈입니다.
newcode 0.2

routine numberthink doublegood(numberthink value)
    reportvalue value times 2
endroutine
```

### 문법 설명

- 모듈은 다른 파일에서 사용할 routine을 정의하는 파일입니다.
- 모듈 파일에는 top-level 실행문을 넣지 않고 routine만 공개합니다.
- `doublegood`는 전달받은 숫자에 2를 곱해 반환합니다.

---

## 12. 모듈 호출 — `12_modules.think`

### 전체 코드

```newcode
// 같은 폴더의 모듈 routine을 이름공간으로 호출합니다.
newcode 0.2

use mathgood from "11_modules_math.think"
speak call mathgood doublegood(7)
```

### 문법 설명

- `use mathgood from "11_modules_math.think"`는 모듈을 불러오고
  `mathgood`이라는 이름공간을 붙입니다.
- `call mathgood doublegood(7)`은 해당 이름공간의 routine을 호출합니다.
- 두 파일은 같은 폴더에 있어야 하며, 순환 import는 `LOOPTHINK`가 됩니다.

---

## 13. 테스트 블록 — `13_tests.think`

### 전체 코드

```newcode
// testthink로 작은 검증을 작성합니다.
newcode 0.2

testthink "addition"
    verify 2 plus 3 same 5
        speak "test passed"
    otherthink
        speak "test failed"
    endverify
endtestthink
```

### 문법 설명

- `testthink "addition"`은 이름이 `addition`인 테스트 블록을 시작합니다.
- 테스트 안에서도 `verify` 조건문을 사용할 수 있습니다.
- 테스트는 일반 실행과 분리된 환경에서 실행됩니다.
- `test` 명령으로 테스트 블록을 실행합니다.

```sh
python -m goodthink test "Python/example/For Beginners/13_tests.think"
```

## 다음 학습 방법

1. 각 파일을 `check`로 먼저 검사합니다.
2. `run`으로 실행 결과를 확인합니다.
3. 숫자·문자열·목록 값을 직접 바꿔 봅니다.
4. 일부러 종료 단어나 자료형을 바꿔 오류 메시지를 확인합니다.
5. 오류 학습은 `../Errors/` 폴더의 예제를 참고합니다.
