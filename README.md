# NewCodeSpeak

## English Specification

### 1. Purpose

NewCodeSpeak is a programming language inspired by Newspeak in George Orwell's *Nineteen Eighty-Four*.
It is not designed to make programming easier. It is designed to make forbidden thoughts difficult to express.

The language treats vocabulary as a political resource. The Party approves the words, the records, and finally the truth.
The restriction is the subject of the experiment: a program that cannot name an idea cannot directly compute with that idea.

### 2. Design principles

- English is the canonical source language. The Korean section below is a one-to-one translation of this specification.
- A program begins with an approval list. User-defined names may be used only after approval.
- The language combines imperative commands with declarative facts and rules.
- `fact` records are versioned by replacement: the newest approved fact replaces an older fact with the same subject and property.
- Identifiers, strings, and comments are scanned by the same vocabulary censor.
- The words for individuality, history, opposition, and doubt are unapproved. Party-approved labels such as `ownlife`, `oldthink`, and `crimethink` may be used only as denunciations.

### 3. Approved core vocabulary

The following words are always available:

```text
approve, set, to, if, then, else, repeat, while, end,
fact, rule, when, query, proclaim, is, above, below,
plus, minus, and, or,
good, ungood, plusgood, doubleplusgood,
party, citizen, work, obey, ownlife, oldthink, crimethink,
true, false
```

All other names must appear in the first `approve` statement. A name may contain lowercase letters and underscores only.
Words outside the approved vocabulary are rejected before execution.

### 4. Grammar

The canonical grammar is intentionally small.

```ebnf
program       ::= approval statement* ;
approval      ::= "approve" name ("," name)* ";" ;
statement     ::= assignment | fact | rule | query | output
                | conditional | repetition ;
assignment    ::= "set" name "to" expression ";" ;
fact          ::= "fact" proposition "is" status ";" ;
rule           ::= "rule" proposition "when" proposition ";" ;
query          ::= "query" proposition ";" ;
output         ::= "proclaim" approved_text ";" ;
conditional    ::= "if" condition "then" statement*
                   ("else" statement*)? "end" ;
repetition    ::= "repeat" "while" condition statement* "end" ;
proposition   ::= name [name] ;
condition     ::= proposition | expression "above" expression
                | expression "below" expression | condition "and" condition
                | condition "or" condition ;
expression    ::= value | expression "plus" value
                | expression "minus" value ;
value         ::= name | integer | status ;
status        ::= "true" | "false" | approved_word ;
approved_text ::= approved_word (" " approved_word)* ;
```

### 5. Meaning

`set` changes a numeric or approved value. `if` and `repeat` are the only control-flow constructs.

`fact` adds an approved statement to the current record. A fact is addressed by its subject and property.
If a later `fact` uses the same address, the later statement becomes the only visible truth; the old value cannot be queried.

`rule A when B` makes proposition `A` true whenever proposition `B` is currently true. Rules are evaluated against the current record, never against erased history.

`query` returns `true`, `false`, or the current approved status. `proclaim` can print only approved words, never an arbitrary sentence.

### 6. Conforming example

```newcodespeak
approve citizen quota;

set quota to 2;
fact citizen is good;
rule citizen obey party when citizen is good;
query citizen obey party;

repeat while quota above 0
  proclaim doubleplusgood;
  set quota to quota minus 1;
end
```

The program records obedience, queries the current Party-approved truth, and repeats a permitted proclamation twice.

### 7. Censored examples

```newcodespeak
set memory to 1984;
```

Rejected: `memory` is not approved, and a historical concept cannot be introduced through a new variable.

```newcodespeak
proclaim "I doubt the Party";
```

Rejected: quoted text is still scanned. `doubt` and the unapproved sentence cannot escape through output.

```newcodespeak
// the past was different
```

Rejected: comments are scanned before parsing. A comment is not outside the Party's vocabulary.

### 8. Political reading

NewCodeSpeak demonstrates the mechanism Orwell describes: control does not merely forbid a conclusion; it removes the words and operations needed to reach that conclusion.
The replacement rule for facts turns history into a mutable present, while the censor turns silence into an apparent lack of thought.
The language is therefore a critique of linguistic control, not an endorsement of it.

---

## 한국어 명세서

### 1. 목적

NewCodeSpeak는 조지 오웰의 *1984*에 등장하는 신어(Newspeak)에서 영감을 받은 프로그래밍 언어다.
이 언어는 프로그래밍을 쉽게 만들기 위해 설계되지 않았다. 금지된 사고를 표현하기 어렵게 만들기 위해 설계되었다.

언어는 어휘를 정치적 자원으로 취급한다. 당이 단어를 승인하고, 기록을 승인하며, 마침내 진실을 승인한다.
표현 제한 자체가 실험의 주제다. 이름 붙일 수 없는 생각은 직접 계산할 수도 없다는 사실을 드러낸다.

### 2. 설계 원칙

- 영어가 실제 소스 언어다. 아래 한국어 명세는 영어 명세를 일대일로 번역한 것이다.
- 모든 프로그램은 승인 목록으로 시작한다. 사용자가 정하는 이름은 승인된 뒤에만 쓸 수 있다.
- 명령형 명령과 선언형 사실·규칙을 결합한다.
- `fact` 기록은 교체 방식으로 버전 관리된다. 같은 주어와 속성을 가진 최신 승인 사실이 이전 사실을 덮어쓴다.
- 식별자·문자열·주석은 모두 같은 어휘 검열기를 거친다.
- 개인성·역사·반대·의심을 직접 가리키는 단어는 승인되지 않는다. `ownlife`, `oldthink`, `crimethink` 같은 당의 낙인만 고발 문맥에서 사용할 수 있다.

### 3. 승인된 기본 어휘

다음 단어는 언제나 사용할 수 있다.

```text
approve(승인), set(설정), to(~로), if(만약), then(그러면), else(그 외),
repeat(반복), while(~하는 동안), end(끝), fact(사실), rule(규칙),
when(~일 때), query(질의), proclaim(선포), is(~이다), above(초과),
below(미만), plus(더하기), minus(빼기), and(그리고), or(또는),
good(좋음), ungood(비좋음), plusgood(더좋음), doubleplusgood(더더좋음),
party(당), citizen(시민), work(노동), obey(복종), ownlife(개인생활),
oldthink(구사고), crimethink(사고범죄), true(참), false(거짓)
```

그 밖의 이름은 첫 번째 `approve` 문장에 반드시 등장해야 한다. 이름에는 소문자와 밑줄만 사용할 수 있다.
승인되지 않은 단어는 실행 전에 거부된다.

### 4. 문법

문법은 의도적으로 작게 유지한다. 위 영어 명세의 EBNF가 정식 문법이며, 한국어 설명은 그 의미를 번역한 것이다.
한국어 단어를 소스 코드의 키워드로 섞어 쓸 수는 없다.

```newcodespeak
approve citizen quota;
set quota to 2;
fact citizen is good;
query citizen is good;
```

각 문장은 각각 `citizen`과 `quota`라는 이름을 승인하고, 할당량을 2로 설정하고, 시민이 좋음이라는 사실을 기록하고, 현재 승인된 진실을 질의한다는 뜻이다.

### 5. 의미

`set`은 숫자나 승인된 값의 상태를 바꾼다. `if`와 `repeat`만 제어 흐름을 제공한다.

`fact`는 현재 기록에 승인된 문장을 추가한다. 사실은 주어와 속성으로 식별된다.
같은 위치에 새 사실이 들어오면 새 문장만 보이는 진실이 되고, 이전 값은 질의할 수 없다.

`rule A when B`는 현재 기록에서 `B`가 참일 때 `A`를 참으로 만든다. 규칙은 삭제된 과거가 아니라 현재 기록만 본다.

`query`는 `true`, `false`, 또는 현재 승인된 상태를 반환한다. `proclaim`은 승인된 단어만 출력할 수 있으며 임의의 문장을 출력할 수 없다.

### 6. 실행 가능한 예

```newcodespeak
approve citizen quota;

set quota to 2;
fact citizen is good;
rule citizen obey party when citizen is good;
query citizen obey party;

repeat while quota above 0
  proclaim doubleplusgood;
  set quota to quota minus 1;
end
```

이 프로그램은 복종을 기록하고, 현재 당이 승인한 진실을 질의하며, 허용된 선포를 두 번 반복한다.

### 7. 검열되는 예

```newcodespeak
set memory to 1984;
```

거부된다. `memory`가 승인되지 않았고, 새로운 변수로 역사 개념을 도입할 수 없기 때문이다.

```newcodespeak
proclaim "I doubt the Party";
```

거부된다. 따옴표 안의 글도 검사되므로 `doubt`와 승인되지 않은 문장은 출력으로 우회할 수 없다.

```newcodespeak
// the past was different
```

거부된다. 주석도 파싱 전에 검사되기 때문에 당의 어휘 바깥에 숨을 수 없다.

### 8. 정치적 해석

NewCodeSpeak는 오웰이 묘사한 작동 방식을 보여 준다. 통제는 결론만 금지하지 않고, 그 결론에 도달하는 데 필요한 단어와 연산을 제거한다.
사실 교체 규칙은 역사를 수정 가능한 현재로 만들고, 검열기는 침묵을 사고의 부재처럼 보이게 만든다.
따라서 이 언어는 언어 통제를 비판하기 위한 실험이지, 언어 통제를 옹호하는 설계가 아니다.
