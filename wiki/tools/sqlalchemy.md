---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/졸업작품-기록/2026-04-07-졸업작품-기록-6.md, _private/raw/velog/졸업작품-기록/2026-04-07-졸업작품-기록-7.md, _private/raw/velog/졸업작품-기록/2026-04-07-졸업작품-기록-8.md, _private/raw/velog/졸업작품-기록/2026-06-14-졸업작품-기록34.md]
tags: [orm, sqlite, python, flask]
---

## 한 줄 정의
SQL을 직접 쓰지 않고 파이썬 코드로 DB를 조작하게 해 주는 ORM이다. Flask에서는 Flask-SQLAlchemy로 연동한다.

## 핵심 내용
```python
# SQL
SELECT * FROM logs WHERE sound_type = '초인종'
# SQLAlchemy ORM
Log.query.filter_by(sound_type='초인종').all()
```
- SQLite와 함께 쓰면 별도 DB 서버 없이 파일 하나(예: `logs.db`)로 동작한다.

| | CSV/JSON 파일 | SQLite |
|---|---|---|
| 구현 난이도 | 쉬움 | 보통 |
| 동시 쓰기 | 충돌 위험 | 안전 |
| 조회 속도 | 데이터가 많아지면 느림 | 빠름 |
| 필터링 | 파이썬 코드로 직접 | SQL 한 줄 |
| 별도 서버 | 불필요 | 불필요 |

## 언제 쓰나 (상황 예시)
- 작은 서버에서 로그를 날짜별·종류별로 필터링해 보여 줘야 할 때.
- 외부 클라이언트(펌웨어·웹)가 응답 형태에 묶여 있어서, DB 스키마 변경이 API 변경으로 번지면 안 될 때.

## 실습에서 배운 것 / 트러블슈팅
- **처음 선택 (2026-04-07)**: [[띵동]]은 분류 로그(시각, 소리 종류, 신뢰도, 알림 전송 여부)를 SQLite + Flask-SQLAlchemy에 저장하기로 했다. 대시보드에서 날짜·종류별 필터링이 필요하고, [[aws-ec2]]에 추가 설치가 필요 없고, 라이브러리 하나로 연동이 끝나기 때문이다. 같은 DB에 카카오 토큰과 초인종 템플릿도 둔다.
- **API v1 모델 (기록 34)**
  - 모델은 둘이다. `notifications`(알림 1건 = 한 행, 대시보드 응답과 1:1)와 `idempotency_keys`(24시간 TTL, `client_request_id` 기준 중복 차단) → [[idempotency-key]]
  - `notifications` 주요 컬럼: `predicted_class` enum(초인종/노크/화재경보), `client_request_id`(ESP32 발급), `request_id`(서버가 ULID로 발급, 시간순 정렬 가능), `created_at`, `confidence`, `image_url`·`transcript`(2차 알림에서 채워지므로 nullable) → [[2단계-알림]]
- **DB 행과 응답 JSON의 경계**: 모델이 곧 응답이면 컬럼 추가가 바로 외부 API 변경이 된다. 모델에 `to_dict()`를 두고 외부로 나갈 때는 반드시 이 직렬화를 거친다.
- **타임존**: SQLite는 타임존을 모른다. 저장은 UTC로 통일하고, 응답 직렬화 시점에만 KST로 바꾼다. 로컬과 EC2(서울 리전) 사이 시간 표현이 어긋나는 사고를 막는다.
- 세션은 "한 요청 = 한 세션"으로 잡고, 응답 직전에 `commit`, 예외 시 `rollback`하는 패턴으로 통일했다.
- `db`는 `extensions.py`에 두고 `create_app`에서 `init_app`한다. 순환 import를 피하는 방법이다 → [[flask]]

## 관련
- [[flask]] · [[aws-ec2]] · [[kakaotalk-message-api]] · [[idempotency-key]] · [[2단계-알림]] · [[띵동]]
- 원글: [졸업작품 기록 (6)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-6)
- 원글: [졸업작품 기록 (34)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D34)
