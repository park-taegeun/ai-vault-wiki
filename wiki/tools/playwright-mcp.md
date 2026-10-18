---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-03-30-Playwright-MCP-Server.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-30-Playwright-GitHub-Notion-3-MCP-콤보-실습.md, _private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Firecrawl-MCP-콤보-실습.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-31-Sequential-Thinking-GitHub-Notion-3-MCP-콤보.md, _private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Memory-Playwright-Notion-GitHub-4-MCP-콤보.md, _private/raw/velog/졸업작품-기록/2026-05-06-졸업작품-기록-22.md, _private/raw/velog/졸업작품-기록/2026-05-07-졸업작품-기록-23.md, _private/raw/velog/졸업작품-기록/2026-05-16-졸업작품-기록-33.md, _private/raw/velog/졸업작품-기록/2026-06-15-졸업작품-기록35.md, _private/raw/velog/졸업작품-기록/2026-06-29-졸업작품-기록-38.md]
tags: [mcp, claude-code, playwright, 브라우저자동화]
---
# Playwright MCP

## 한 줄 정의
Microsoft의 브라우저 자동화 프레임워크 Playwright를 MCP 서버로 감싼 것. 자연어 지시로 실제 브라우저를 열어 탐색·클릭·입력·캡처한다.

## 핵심 내용
- Playwright는 Chromium, Firefox, WebKit(Safari) 세 엔진을 지원한다.
- API를 부르는 다른 MCP와 달리 실제 브라우저가 동작하므로, JS로 렌더링되는 SPA나 API가 없는 서비스에도 접근할 수 있다.
- 패키지 `@playwright/mcp@latest`, stdio 방식. **최신 버전은 headed가 기본값**이고 headless는 `--headless` 플래그로 켠다.
  ```bash
  claude mcp add playwright --scope user -- npx -y @playwright/mcp@latest
  # headless로 바꾸기
  claude mcp remove playwright --scope user
  claude mcp add playwright --scope user -- npx -y @playwright/mcp@latest --headless
  ```

| | Headless | Headed |
|---|---|---|
| 브라우저 창 | 없음 | 보임 |
| 속도/리소스 | 빠름/적음 | 느림/많음 |
| 용도 | CI/CD, 서버 자동화 | 디버깅, 개발 중 확인, 시연 |

- 도구 계열 (2026-03 글 기준 이름): 탐색 `browser_navigate`, `browser_go_back`, `browser_go_forward` / 읽기 `browser_snapshot`, `browser_screenshot` / 인터랙션 `browser_click`, `browser_type`, `browser_hover`, `browser_select_option`, `browser_drag` / 제어 `browser_wait`, `browser_press_key`.

| | browser_snapshot | browser_screenshot |
|---|---|---|
| 반환 | 텍스트 (접근성 트리) | 이미지 |
| 처리 | 구조 파악 후 요소 특정 | vision으로 분석 |
| 속도 | 빠름 | 느림 |
| 용도 | 클릭/입력할 요소 찾기 | 결과 시각 확인 |

  기본 흐름: `navigate → snapshot(구조 파악) → click/type → screenshot(결과 확인)`.

- [[firecrawl-mcp]]와 비교: Playwright는 실제 브라우저를 띄워 로그인·클릭 같은 UI 조작과 동적 페이지에 강하고 인증(API 키)이 필요 없다. Firecrawl은 API 기반으로 대량 수집·마크다운 변환에 강하다. 출력도 Playwright는 HTML·스크린샷, Firecrawl은 정제된 마크다운.

## 언제 쓰나 (상황 예시)
- E2E 테스트(로그인 → 상품 검색 → 장바구니 → 결제)를 자연어로.
- SPA 스크래핑·모니터링 (경쟁사 가격, 채용공고 알림 등).
- 콤보: UI 테스트 실패 → [[github-mcp]]로 이슈 생성 → [[notion-mcp]]에 기록 → [[mcp-combo]].
- 한계: Cloudflare, reCAPTCHA 같은 봇 감지가 있는 사이트는 접근이 제한된다. 실행마다 새 브라우저 세션이 시작돼 쿠키·세션이 유지되지 않는다. 대량 스크래핑보다 테스트·정보 추출에 맞다.

## 실습에서 배운 것 / 트러블슈팅
- **모델 지식이 구버전**: Claude가 "headless로 구성돼 창이 안 보인다"고 안내했지만 실제로는 창이 열렸다. 학습 데이터가 구버전 기준이었던 것으로 판단.
- **토큰 한도 초과를 스스로 우회**: 포털에서 날씨를 검색하던 중 `browser_type` 결과가 140,203자로 토큰 한도를 넘었다. Claude가 Bash + Python3으로 파일을 읽고 필요한 값만 파싱해 답을 냈다.
- 스크린샷 저장: `browser_navigate → browser_screenshot`으로 실제 이미지 파일이 저장됐다.
- 연속 호출이 많은 작업은 `claude --dangerously-skip-permissions`로 세션 동안 승인을 건너뛴다 (주의점은 [[mcp-combo]]). 이 모드에서 JS 실행으로 Velog 글 9개의 제목·작성일을 표로 추출했다.

- **UI 테스트 + GIF 녹화**: AI가 만든 HTML 테스트 UI에서 회원가입 → 로그인 → 내 정보 조회 흐름을 캡처하고 GIF로 녹화(960×540, 8프레임, 13.0초, 618KB).
- **상태 수집기**: 포스팅 동기화 콤보에서 Velog 글 목록 페이지를 크롤링해 실제 포스팅 수(11편)를 세어 Memory 기준점과 비교하는 역할.
- **졸업작품 [[띵동]]에서 쓴 곳**
  - **JS 렌더링 부품몰 조사 (2026-05-06)**: 상세 페이지가 JavaScript로 렌더링돼 일반 검색으로는 정보가 안 긁혔다. playwright + [[firecrawl-mcp]]로 부품 9개의 직링크·가격·재고를 조사하게 맡기고, 결제 전 스크린샷으로 7건을 직접 다시 확인했다. 재고는 있는데 납기가 해외 1주일로 뜨는 모순처럼 페이지로 풀 수 없는 건 판매처에 문의했다.
  - **라이브러리 호환성 사전 검증 (2026-05-07)**: firecrawl + playwright + context7 조합으로 GitHub 사례·Issue·블로그 글을 추적했다 → [[ai-산출물-검증]]
  - **동적 로딩 명단 확인 (2026-05-16)**: 학생 크레딧 프로그램 자격 확인에서 공식 참여 기관 명단(32개)이 동적으로 로딩돼 일반 검색으로는 한계가 있었다. playwright로 명단을 확인해 12분 만에 결론을 냈다.
  - **미니 E2E (기록 35)**: Flask와 Vite dev를 함께 띄우고 카드 렌더, Bearer 헤더, CORS 에러 0건, 요청 origin(proxy 경유), 콘솔 에러 0건을 확인했다 → [[react]], [[vite]]
  - **육안으로 안 보이는 접근성 버그 (기록 38)**: radix Dialog drawer를 닫을 때 포커스 복원이 조용히 실패하는 것을 실측으로 잡았다 → [[web-accessibility]]

## 관련
- [[mcp]]
- [[mcp-scope]]
- [[mcp-combo]]
- [[github-mcp]] · [[notion-mcp]]
- [[firecrawl-mcp]]
- [[photocraft-mcp]]
- [[scrapling-mcp]]
- [[띵동]] · [[ai-산출물-검증]] · [[react]] · [[vite]] · [[web-accessibility]]
- 원글: [졸업작품 기록 (22)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-22)
- 원글: [졸업작품 기록 (33)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-33)
- 원글: [Playwright MCP Server](https://velog.io/@xorms/Playwright-MCP-Server)
- 원글: [Playwright + GitHub + Notion 3 MCP 콤보](https://velog.io/@xorms/Playwright-GitHub-Notion-3-MCP-%EC%BD%A4%EB%B3%B4-%EC%8B%A4%EC%8A%B5)
- 원글: [Firecrawl MCP + 콤보 실습](https://velog.io/@xorms/Firecrawl-MCP-%EC%BD%A4%EB%B3%B4-%EC%8B%A4%EC%8A%B5)
- 원글: [Sequential Thinking + GitHub + Notion 3 MCP 콤보](https://velog.io/@xorms/Sequential-Thinking-GitHub-Notion-3-MCP-%EC%BD%A4%EB%B3%B4)
- 원글: [Memory + Playwright + Notion + GitHub 4 MCP 콤보](https://velog.io/@xorms/Memory-Playwright-Notion-GitHub-4-MCP-%EC%BD%A4%EB%B3%B4)
