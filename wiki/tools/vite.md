---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/졸업작품-기록/2026-04-07-졸업작품-기록-7.md, _private/raw/velog/졸업작품-기록/2026-06-15-졸업작품-기록35.md]
tags: [프론트엔드, 번들러, cors]
---

## 한 줄 정의
설정이 거의 필요 없는 빠른 프론트엔드 번들러·개발 서버다.

## 핵심 내용
- React 프로젝트를 명령 한 줄로 만든다.
  ```bash
  npm create vite@latest dashboard -- --template react
  ```
- **dev proxy로 CORS 우회**: React(`localhost:5173`)와 Flask(`localhost:5000`)는 origin이 달라 브라우저가 fetch를 막는다. `vite.config.ts`의 `server.proxy`에 `"/api": { target: "http://localhost:5000", changeOrigin: true }`를 둔다. 클라이언트가 상대 경로(`/api/v1/...`)로 부르면 브라우저에는 모두 same-origin으로 보여 CORS도 preflight OPTIONS도 생기지 않는다. 백엔드 코드는 한 줄도 안 바뀐다.
- **환경변수**: `import.meta.env.VITE_API_BASE_URL`(기본 `/api/v1`), `VITE_DASHBOARD_TOKEN`. `.env.example`에는 토큰을 비워 두고 실제 값은 `.env.local`에 둔다. 실수로 commit해도 토큰은 새지 않는다.

## 언제 쓰나 (상황 예시)
- 빌드 설정에 시간을 쓰고 싶지 않은 작은 프론트엔드 프로젝트.
- 운영에서는 Nginx로 같은 origin이 될 예정인데 로컬 개발 중에만 CORS를 피하고 싶을 때. CORS 라이브러리를 깔면 운영까지 끌려가지만 dev proxy는 개발 환경에만 있다 → [[nginx-gunicorn]]

## 실습에서 배운 것 / 트러블슈팅
- [[띵동]] 웹 대시보드 번들러로 선택했다 (2026-04-07). 빠르고 설정이 거의 필요 없어서다.
- **한계**: dev proxy는 `vite dev` 전용이다. 프로덕션 빌드를 정적 호스팅하면 Nginx로 같은 origin을 만들거나 백엔드에 CORS를 따로 깔아야 한다.
- Playwright 미니 E2E에서 요청 origin `localhost:5173`(proxy 경유)과 CORS 에러 0건을 확인했다 → [[playwright-mcp]]

## 관련
- [[react]] · [[flask]] · [[nginx-gunicorn]] · [[playwright-mcp]] · [[띵동]]
- 원글: [졸업작품 기록 (7)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-7)
- 원글: [졸업작품 기록 (35)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D35)
