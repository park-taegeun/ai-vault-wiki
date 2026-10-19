---
type: concept
modified: 2026-10-19
sources: [_private/raw/notion/Backend/세션 정리/3주차 - API 명세의 이해와 Annotation 305d8df03cab80d9893cf645c6f4274b.md, _private/raw/notion/Backend/세션 정리/3주차 - API 명세의 이해와 Annotation/실습/Swagger Controller 305d8df03cab806389c5c8dc0346784d.md, _private/raw/notion/Backend/세션 정리/4주차 - Entity, Controller, Swagger 알아보기/실습 30bd8df03cab806dabc4fc1d4fa8452d.md, _private/raw/notion/Backend/Session/Week09 - JSON Web Token 2bdd8df03cab80fdacd0e621df4c5070.md, 비공개 원본]
tags: [api, http, rest, json, 멋쟁이사자처럼]
---

## 한 줄 정의
URL로 대상(자원)을 가리키고 HTTP 메서드로 할 일을 정해, 주로 JSON으로 데이터를 주고받는 API 방식이다. API는 서로 다른 애플리케이션이 소통하는 인터페이스다. 멋쟁이사자처럼 13기 백엔드 트랙 3주차 내용이다.

## 핵심 내용
### API 명세서 작성법
1. **기본 정보**: API 이름과 짧은 설명, 버전(v1, v2), 기본 URL.
2. **인증 방식**: 헤더에 무엇을 넣는지까지 구체적으로 쓴다.
3. **엔드포인트와 HTTP 메서드** (명세의 핵심): 경로(`/users`, `/users/{id}`), 메서드, 하는 일.
4. **요청 파라미터**: Path Variable(`/users/{id}`), Query Parameter(`/users?id=1`), Header(`Content-Type: application/json`, `Authorization: Bearer <REDACTED>`), Request Body(JSON, 필수·선택 여부까지).
5. **응답 구조**: 형식(보통 JSON), 상태 코드(200, 201, 404), 실제 반환 예시. 예시는 꼭 넣는다.
6. **오류 처리**: 생길 수 있는 오류(400, 401, 500)와 오류 응답 모양.

명세를 코드에서 뽑는 도구는 [[swagger]]다.

### CRUD와 HTTP 메서드
4주차 게시글 API에서는 이렇게 짝지었다.

| 작업 | 메서드 | 경로 예 |
|---|---|---|
| 생성 | POST | `/api/v1/posts` |
| 전체 조회 | GET | `/api/v1/posts` |
| 단일 조회 | GET | `/api/v1/posts/{id}` |
| 수정 | PUT (전체) / PATCH (일부) | `/api/v1/posts/{id}` |
| 삭제 | DELETE | `/api/v1/posts/{id}` |

### PUT과 PATCH: 멱등성 차이
- **PUT**은 리소스 전체를 요청 본문으로 통째로 덮어쓴다. 같은 요청을 몇 번 보내도 결과가 같으므로 멱등하다.
- **PATCH**는 일부 필드만 바꾸고 바꾸는 방식을 정할 수 있다. "age를 1 올려라"라는 PATCH는 보낼 때마다 25 → 26 → 27 → 28로 결과가 달라진다. 그래서 PATCH는 멱등하지 않을 수도 있다.
- 원본 노트에는 "멱동성"으로 적혀 있었다 (정정).
- 멱등하지 않은 요청이 재전송될 때 중복 처리를 막는 방법은 [[idempotency-key]].

### Soft Delete vs Hard Delete

| | Hard Delete (물리 삭제) | Soft Delete (논리 삭제) |
|---|---|---|
| 방식 | DB에서 행을 실제로 지움 | 지우지 않고 `is_deleted` 같은 컬럼으로 "삭제됨" 표시만 함 |
| 장점 | 저장 공간 확보 | 데이터가 남음 |
| 단점 | 복구 불가, 이력 추적이 어려움 | (원본에 정리 없음) |

### JSON과 Jackson
- JSON은 자바스크립트의 객체 표기법에서 온 형식으로, 여러 언어가 데이터를 주고받을 때 쓴다.
- Java에서는 Jackson 라이브러리가 객체 ↔ JSON 변환(직렬화·역직렬화)을 맡는다. 컨트롤러에서 `@RequestBody`로 JSON 본문을 객체로 받는 것도 이 위에서 이뤄진다. → [[spring-data-jpa]]

### 공통 응답 형식 (Week09 실습)
모든 응답을 `success`·`code`·`message`·`data` 네 필드의 `BaseResponse`로 통일하고, 예외는 `@RestControllerAdvice`에서 같은 형식으로 바꿔 내려보낸다. → [[jwt]]

## 언제 쓰나 (상황 예시)
- 프론트엔드·앱과 서버가 주고받을 약속을 정할 때 명세서부터 쓴다.
- 수정 API를 PUT으로 할지 PATCH로 할지 정할 때. 재시도가 잦은 환경이면 멱등성을 따진다.
- 삭제 기능에서 복구·이력 추적이 필요한지에 따라 Soft/Hard Delete를 고를 때

## 실습에서 배운 것 / 트러블슈팅
- 3주차 실습에서 POST·GET·PATCH·PUT·DELETE 테스트 엔드포인트를 하나씩 만들어 [[swagger]] 화면에 메서드별로 뜨는 것을 확인했다.
- 4주차에는 게시글 API 다섯 개를 위 표대로 설계했다. 아직 Service 없이 문자열만 돌려주는 뼈대 단계다.

## 관련
- [[swagger]] · [[spring-boot]] · [[spring-data-jpa]] · [[idempotency-key]] · [[jwt]] · [[flask]]
