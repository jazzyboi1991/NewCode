# Newcode 0.6 Examples

`24_user_recordthink.think` demonstrates a top-level user-defined
`recordthink`, named constructors, nested records, `maybe` fields, and field
reads and updates.

```sh
python3 -m goodthink check "example/v0.6/24_user_recordthink.think"
python3 -m goodthink run "example/v0.6/24_user_recordthink.think"
```

Every declared field is required when constructing a record, and constructor
arguments may appear in any order. Unknown fields and type mismatches produce
`THINKLOGIC ERROR` and `THINKTYPE ERROR` respectively.

## 한국어

`24_user_recordthink.think`는 최상위 사용자 정의 `recordthink`, 이름 있는
생성자, 중첩 기록, `maybe` 필드, 필드 읽기와 수정을 보여 줍니다.

모든 선언 필드는 생성 시 제공해야 하며 생성자 인자의 순서는 선언 순서와 달라도
됩니다. 정의되지 않은 필드와 자료형 오류는 각각 `THINKLOGIC ERROR`와
`THINKTYPE ERROR`로 진단됩니다.
