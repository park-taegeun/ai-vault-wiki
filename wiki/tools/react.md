---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/졸업작품-기록/2026-04-07-졸업작품-기록-7.md, _private/raw/velog/졸업작품-기록/2026-06-15-졸업작품-기록35.md, _private/raw/velog/졸업작품-기록/2026-06-29-졸업작품-기록-38.md, _private/raw/velog/졸업작품-기록/2026-07-01-졸업작품-기록-39.md]
tags: [프론트엔드, react, typescript, 대시보드]
---

## 한 줄 정의
UI를 컴포넌트 단위로 만드는 JavaScript 프론트엔드 라이브러리다. [[띵동]]의 웹 대시보드를 만드는 데 썼다.

## 핵심 내용
- **백엔드 연동 방식 — REST API + 폴링**: React가 주기적으로 서버에 GET 요청을 보내 최신 데이터를 받아 온다.
- **shadcn/ui**: Tailwind 기반 컴포넌트 라이브러리다. 테이블·카드·배지 같은 컴포넌트가 이미 있어 로그 테이블과 상태 화면을 빨리 만들 수 있다.
- **mock → 실제 API는 "데이터 출처만" 교체 (PR #3)**: `dashboard/src/lib/api.ts`의 `fetchNotifications`/`fetchStats` signature는 그대로 두고 내부만 실제 fetch로 바꿨다. 훅·컴포넌트는 한 줄도 안 건드렸고 새 라이브러리(axios, TanStack Query, SWR)도 넣지 않았다. UI에서 버그가 나면 데이터 출처 교체 외 원인으로 격리할 수 있다.
- **`apiGet<T>` 공용 헬퍼**: Bearer 헤더, 상태 코드 검증(`!res.ok`면 `API ${status}: ${path}` 에러), JSON 파싱, base URL 끝 슬래시 방어를 한 곳에 모았다. 두 함수에 같은 코드를 반복하면 한쪽만 고치는 사고가 난다.
- **응답 타입**: `next_cursor?`, `has_more?`를 옵셔널(additive)로 추가했다. 타입은 추측이 아니라 실제 curl 응답을 보고 맞췄다 → [[flask]]
- **TypeScript strict (PR #5)**: `"strict": true`를 접근성 PR보다 먼저 별도 PR로 켰다. 빌드하니 에러 0건이었다. 그동안 null 가드·타입을 제대로 써왔다는 후행 증명이었다.
- **시스템 건강 카드**: 기존 `device_status`(`online`/`offline`/`processing`)·`device_last_seen_at`을 재사용하고 `signal_strength`만 추가했다. 상수 하드코딩 대신 타입으로 서버 mock → 카드까지 이어 "구조는 실제, 값만 mock"으로 만들었다.
- **빈 상태 vs 에러 분기**: loading → error → empty 순서를 지킨다. 실제 fetch 실패를 "정상 작동 중"으로 덮으면 더 위험한 거짓 정보가 된다 → [[화면이-아는-만큼만-말하기]]

## 언제 쓰나 (상황 예시)
- 서버 로그를 보여 주는 관리·확인용 대시보드. 프로젝트 생성은 [[vite]]로 한다.
- mock으로 검증한 UI를 실제 백엔드에 붙일 때. 데이터 계층 함수의 signature를 경계로 삼는다.

## 실습에서 배운 것 / 트러블슈팅
- **폴링 간격 3초 (2026-04-07)**: 실시간 알림은 카카오톡이 맡고 대시보드는 로그 확인용이라 폴링으로 충분하다고 판단했다. 간격은 상수 한 곳에서 관리한다.
- seed 알림을 어제 날짜로 넣었더니 `stats?period=today`가 0이었다. 엔드포인트 고장이 아니라 정의상 맞는 값이었다. 오늘 날짜로 `/detect` 1건을 주입하자 3초 뒤 폴링이 새 카드를 가져오고 stats가 0 → 1이 됐다.
- Playwright 미니 E2E: seed 11건 카드 렌더, Bearer 헤더, CORS 에러 0, 콘솔 에러 0, tsc/eslint/build 통과 → [[playwright-mcp]]
- **정적 리뷰 (기록 38)**: read-only로 `dashboard/` 55개 + `server/` 13개 소스를 봤다. 🔴 0 / 🟡 4 / 🟢 6 / deferred 6. 리뷰는 stats 폴링이 "2중"이 아니라 3중 + announcer 1 = 4중임을 실측으로 바로잡았다 → [[ai-산출물-검증]]
- **라이트 기본 테마**: 시스템 추종(`matchMedia`) 대신 `localStorage`에 값이 없으면 `"light"`로 했다. "토큰을 새로 짜야 한다"고 가정했지만 `:root`에 라이트 토큰이 이미 완비돼 기본값만 바꾸면 됐다 → [[web-accessibility]], [[design-tokens]]

## 관련
- [[vite]] · [[flask]] · [[web-accessibility]] · [[design-tokens]] · [[playwright-mcp]] · [[ai-산출물-검증]] · [[화면이-아는-만큼만-말하기]] · [[github-flow]] · [[띵동]]
- 원글: [졸업작품 기록 (7)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-7)
- 원글: [졸업작품 기록 (35)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D35)
- 원글: [졸업작품 기록 (38)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-38)
- 원글: [졸업작품 기록 (39)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-39)
