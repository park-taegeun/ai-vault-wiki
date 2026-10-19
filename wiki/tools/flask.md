---
type: tool
modified: 2026-10-19
sources: [_private/raw/velog/졸업작품-기록/2026-04-07-졸업작품-기록-6.md, _private/raw/velog/졸업작품-기록/2026-04-07-졸업작품-기록-7.md, _private/raw/velog/졸업작품-기록/2026-06-14-졸업작품-기록34.md, _private/raw/velog/졸업작품-기록/2026-06-15-졸업작품-기록35.md, _private/raw/velog/졸업작품-기록/2026-07-06-졸업작품-기록-42.md]
tags: [python, 웹프레임워크, api, wsgi]
---

## 한 줄 정의
Python 웹 프레임워크다. WSGI 앱이라 프로덕션에서는 Gunicorn 같은 WSGI 서버 위에서 돌린다. [[띵동]]에서는 ESP32와 React 대시보드 사이의 API 서버로 쓴다.

## 핵심 내용
- 내장 개발 서버는 싱글 스레드이고 에러가 나면 죽는다. 운영에는 [[nginx-gunicorn]] 구조를 쓴다.
- **의존성 관리**: venv로 프로젝트별 독립 공간을 만들고 `requirements.txt`에 라이브러리 목록을 적는다. 다른 머신에서 `pip install -r requirements.txt` 한 줄로 같은 환경을 재현한다.
- **app factory 패턴**: 전역 `app = Flask(__name__)` 대신 `create_app()`이 앱을 조립해 반환한다. 테스트·개발·운영 config를 갈아끼울 수 있다. `extensions.py`에 `db = SQLAlchemy()`를 따로 두고 `create_app` 안에서 `db.init_app(app)`을 부르면 순환 import를 피한다 → [[sqlalchemy]]
- **Blueprint + URL 버저닝**: `app.register_blueprint(api_v1, url_prefix="/api/v1")`. 펌웨어는 OTA 없이 못 바꾸므로 깨지는 변경은 `/api/v2`로 새로 판다.
- **띵동 API v1 엔드포인트 (PR #2)**

  | 엔드포인트 | 호출자 | 역할 |
  |---|---|---|
  | `POST /api/v1/detect` | ESP32 | 1차 추론 + 알림 저장 + `request_id`(ULID) 발급 |
  | `POST /api/v1/enrich` | ESP32 | 2차 사진·STT 채우기 |
  | `GET /api/v1/notifications` | React | 알림 리스트, cursor pagination |
  | `GET /api/v1/stats` | React | `?period=today` 집계 |

  `/detect`는 빨라야 하는 1차 알림, `/enrich`는 사진 + 추가 5초 녹음을 보내는 2차라 분리했다 → [[2단계-알림]]
- **응답 JSON은 프론트 타입이 기준**: `dashboard/src/types/*.ts`를 먼저 보고 맞춘다. cursor 메타(`next_cursor`, `has_more`)는 기존 키를 유지한 채 additive로 내렸다 → [[single-source-of-truth]]
- **인증**: Device Token과 Dashboard Token을 나누고 데코레이터로 라우트별로 건다. 토큰 비교는 `hmac.compare_digest`(상수시간)이고, 설정값이 비어 있으면 무조건 401이다. 설정 누락이 인증 우회가 되지 않게 했다.
- **rate limit**: device 기준 5초당 1회, 초과 시 `429` + `Retry-After` 헤더.
- **중복 방지**: ESP32가 발급한 `client_request_id`를 24시간 보관하고, 같은 key가 오면 이전 응답을 그대로 replay한다 → [[idempotency-key]]
- **에러 형식 통일**: HTTP 8종(200/201/400/401/404/409/429/500), 본문은 모두 `{"error": "...", "message": "..."}`.

## 언제 쓰나 (상황 예시)
- 기기에서 파일을 받아 ML 추론을 돌리고 결과를 알림·로그로 보내는 작은 API 서버.
- 펌웨어(회수 불가 클라이언트)와 웹(교체 가능한 클라이언트)이 같은 서버를 부를 때. 토큰·권한 도메인을 처음부터 나눈다.

## 실습에서 배운 것 / 트러블슈팅
- **처음 설계 (2026-04-07)**: WAV 수신 → librosa로 [[mel-spectrogram]] 변환 → [[yamnet]] 추론 → 초인종 2차 필터([[초인종-유사도-검증]]) → [[kakaotalk-message-api]] 전송 → SQLite 로그 기록.
- **curl 15종 검증**: 인증 401, 필드 누락/잘못된 enum/period 400, 정상 201·200, replay 200, rate limit 429, enrich 404·409, pagination 중복 없음, stats와 DB 직접 카운트 일치. 백엔드를 curl로 다 검증해 둔 덕에 React 연동 때 "백엔드냐 프론트냐"를 고민할 필요가 없었다 → [[react]]
- **한계**: rate limit이 in-memory `dict`라 Gunicorn 워커 2개로 띄우면 워커마다 따로 돌아 무효화된다. 배포 때 Redis로 바꿀 예정이었다.
- **macOS 5000 포트 점거**: "주소 이미 사용 중"이 나서 `lsof -i :5000`으로 보니 AirPlay 수신과 Flask 좀비 프로세스가 물고 있었다. `127.0.0.1:5000` 직접 접속은 Flask로 가는데 `localhost:5000`을 proxy로 거치면 AirTunes로 가서 403이 났다. 실마리는 응답 헤더 `Server: AirTunes`였다. 코드가 아니라 OS 설정 문제였다.
  - Spring Boot 8080 포트에서도 같은 방식(`lsof -i :8080` → `kill -9 PID`)으로 풀었다. → [[spring-boot]]
- **결정론적 시드 데이터 (기록 42)**: `server/seed.py`로 실제 DB에 5건(초인종 완료 / 노크 완료 / 노크 2차 처리중 / 화재 우회 / 초인종 미발송)을 심었다. `detected_at`을 `now - timedelta(...)`로 잡아 항상 "오늘" 필터에 걸리게 하고, `delete()` 후 `add_all`로 몇 번 돌려도 같은 상태가 되게 했다.

## 관련
- [[spring-boot]] · [[rest-api]] — 자바 쪽 백엔드와 API 설계
- [[nginx-gunicorn]] · [[aws-ec2]] · [[https-tls]] · [[sqlalchemy]] · [[react]] · [[vite]] · [[kakaotalk-message-api]] · [[2단계-알림]] · [[idempotency-key]] · [[single-source-of-truth]] · [[esp32-s3]] · [[띵동]]
- 원글: [졸업작품 기록 (6)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-6)
- 원글: [졸업작품 기록 (34)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D34)
- 원글: [졸업작품 기록 (35)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D35)
- 원글: [졸업작품 기록 (42)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-42)
