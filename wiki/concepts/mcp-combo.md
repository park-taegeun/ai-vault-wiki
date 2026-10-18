---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-03-27-Context7-GitHub-MCP-콤보.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-30-Playwright-GitHub-Notion-3-MCP-콤보-실습.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-30-Notion-MCP.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-31-Sequential-Thinking-GitHub-Notion-3-MCP-콤보.md, _private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Firecrawl-MCP-콤보-실습.md, _private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Memory-Playwright-Notion-GitHub-4-MCP-콤보.md, _private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Slack-MCP.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-31-Supabase-MCP.md]
tags: [mcp, claude-code, 에이전트, 워크플로우]
---
# MCP 콤보

## 한 줄 정의
여러 MCP를 한 프롬프트 안에서 같이 쓰는 방식. 도구 순서는 Claude가 스스로 정하고, 여러 단계를 한 번에 처리한다.

## 핵심 내용
- 개발자가 "어떤 도구를 언제 쓸지" 지시하지 않아도 목표만 주면 Claude Code가 도구 순서를 정한다.
- 콤보에 쓸 범용 MCP는 어느 디렉터리에서나 잡히도록 `--scope user`로 등록한다 → [[mcp-scope]].
- 역할 분담: [[context7-mcp]] 문서 참조 / [[github-mcp]] 코드 관리 / [[notion-mcp]] 기록 / [[playwright-mcp]] 브라우저 조작.

### 콤보 1 — Context7 + GitHub (2026-03-27)
- 전: 문서 검색 → 코드 작성 → git add/commit/push → PR (4단계). 후: 프롬프트 한 줄.
- GitHub MCP로 `mcp-combo-practice` 레포 생성 → 로컬 클론, `npm init -y`, `npm install express` → 한 프롬프트로 "use context7로 최신 Express.js 문서 확인 → `src/index.js`에 `GET /health`, `GET /users`, `POST /users` 작성 → `feat/express-api` 브랜치 → 커밋 → main으로 PR (main에 README.md가 없으면 먼저 커밋)".
- 호출 로그: `resolve-library-id` → `query-docs` → `create_or_update_file` → `add_issue_comment`. 마지막 코멘트는 지시하지 않은 단계로, 어떤 문서를 참조했는지 PR에 남겼다.

### 콤보 2 — Playwright + GitHub + Notion (2026-03-30)
- 목표: 내 Velog 전체 글 크롤링 → GitHub `park-taegeun/velog-backup` 레포에 마크다운 백업 → Notion 대시보드.
- 단일 프롬프트 후 사용자 개입 없이 7단계를 처리: 목록 페이지 접속 → JS로 카드 파싱 → 글 URL을 돌며 본문/태그/날짜 추출 → 레포 생성 → 글별 개별 커밋(총 11 commits) → README에 날짜/제목/태그 표 → Notion 대시보드.
- 결과: `posts/`에 `날짜-제목.md` 10개, README 표, 레포 설명까지 자동 입력. 총 **20분 9초** 걸렸다. Notion 대시보드는 백업이 끝난 뒤 별도 프롬프트로 요청했다.


### 콤보: Sequential Thinking + GitHub + Notion — 설계·구현·문서화
- 시나리오: Node.js + Express + JWT 인증 모듈 (`POST /auth/register`, `POST /auth/login`, `GET /auth/me`). 레포 `park-taegeun/chat-app-auth`.
- 흐름: [[sequential-thinking-mcp]]가 "어떻게 만들지" 6단계 설계 → [[github-mcp]]가 코드 커밋 → [[notion-mcp]]가 "무엇을 왜 만들었는지" 문서화.
- 결과: 커밋 2개(`chore: initialize repository`, `feat: add JWT auth module` 8파일), 이슈 #1에 설계 6단계 전체 기록. 설계→코드 8파일→이슈→Notion까지 **3분 55초**, 사람 입력은 프롬프트 한 번.
- 실제 서버를 띄워 curl로 세 엔드포인트 검증. 비밀번호 6자 미만이면 `{"error": "Password must be at least 6 characters"}` — 설계한 검증 규칙이 코드에 그대로 반영됨.
- 추가 실습: Sequential Thinking + GitHub + [[playwright-mcp]]로 HTML 테스트 UI를 만들고 캡처·GIF 녹화(960×540, 8프레임, 13.0초, 618KB).

### 콤보: Firecrawl + GitHub + Notion + Sequential Thinking — AI 뉴스 모니터링
- 역할: [[firecrawl-mcp]] 스크랩(Anthropic·OpenAI·HuggingFace 블로그) / Sequential Thinking 분류 / GitHub 날짜별 아카이빙 / Notion 대시보드.
- 흐름: `ai-news-monitor` 레포 생성 + README 커밋 → 뉴스 44건 스크랩 → 모델/기술·비즈니스/산업·연구/논문 3분류 → `posts/2026-04-01.md` 커밋 → Notion 메인 페이지 + 날짜별 서브페이지.

### 콤보: Memory + Playwright + Notion + GitHub — 포스팅 동기화
- 문제: 새 글마다 backup 레포 커밋, Notion 대시보드 행 추가, Memory 포스팅 수 갱신을 손으로 해야 했다.
- 역할: [[memory-mcp]] 기준점 조회·최종 갱신 / Playwright Velog 크롤링으로 실제 글 수 수집 / GitHub 마크다운 커밋 + README / Notion 신규 행.
- 7단계: Memory 조회 → 크롤링 → 수 비교 → (차이 있으면) GitHub → Notion → Memory 갱신 → 요약 리포트. 차이가 없으면 4~6단계를 스킵.
- 결과: 실행 전 Velog 11편 / GitHub·Notion·Memory 10편 → 실행 후 4곳 모두 11편.

### 콤보: GitHub + Slack — 커밋 알림 봇
- 프롬프트 한 줄로 4단계: 레포 최근 커밋 3개 조회 → [[slack-mcp]]로 채널에 현황 전송 → GitHub 이슈 생성 → 이슈 URL 포함 완료 알림.
- 배포 알림 봇, PR 리뷰 요청 자동화와 구조가 같다.

### 조합 아이디어: 졸업 프로젝트 MCP 풀 사이클
- Context7(라이브러리 최신 문서) + [[supabase-mcp]](DB 스키마·테이블) + GitHub(커밋·PR) + Notion(진행 기록).

## 언제 쓰나 (상황 예시)
- 사이드 프로젝트: "Prisma로 User 모델 만들고 CRUD API" → Context7이 최신 문법 확인, GitHub MCP가 브랜치·커밋·PR.
- 버그 대응: 최근 커밋 조회 → 올바른 API 사용법 확인 → hotfix 브랜치와 PR.
- 팀 협업: PR diff 조회 → 분석 → 리뷰 코멘트 등록.
- 풀 사이클: 문서 참조 → 코드 → PR → 개발 일지 기록 (Context7 + GitHub + Notion).
- 테스트 파이프라인 구상: 테스트 실패 → 스크린샷 → 이슈 생성 → Notion 기록 (Playwright + GitHub + Notion).
- 최신화: "velog-backup 최신화해줘" 한 줄로 GitHub와 Notion을 같이 갱신. 매일 자동 실행이 필요하면 GitHub Actions에 Playwright 코드를 올려 Claude Code 없이 돌릴 수 있다.

## 실습에서 배운 것 / 트러블슈팅
- **조건은 처음 프롬프트에**: 크롤링이 시작된 뒤 "특정 시리즈는 제외해줘"를 덧붙였지만 적용되지 않고 전체가 포함됐다. 제외 조건은 최초 프롬프트에 넣는다.
- **`--dangerously-skip-permissions`**: `claude --dangerously-skip-permissions` → 경고에서 "Yes, I accept". 세션 단위라 종료 후 `claude`로 다시 켜면 승인 모드로 돌아온다. 읽기 전용 크롤링·백업처럼 되돌리기 쉬운 반복 작업에만 쓰고, 프로덕션 DB 수정·배포 자동화에는 쓰지 않는다.
- **긴 작업 중 진행 확인**: 장시간 작업 중에는 "Slithering..." 상태가 뜬다. 작업을 멈추지 않고 `/btw 얼마나 남았어?`로 진행 상황을 볼 수 있다 (7/10 완료 시점에 사용).
- MCP가 등록돼 있지 않으면 Claude가 `git checkout`, `curl -X POST` 같은 Bash로 우회한다. 기능은 될 수 있지만 콤보 실습의 의미가 없어지므로 `(MCP)` 표시를 확인한다.

- **중간 승인 없이 한 번에**: 연속 커밋·페이지 생성이 이어지는 콤보는 `claude --dangerously-skip-permissions`로 실행했다(세 콤보 모두).
- **변화 감지(체크포인트) 패턴**: Memory에 마지막 상태를 저장하고 매 실행마다 실제와 비교해 차이가 있을 때만 후속 작업 → 자주 돌려도 중복 커밋·중복 Notion 행이 안 생긴다. 유튜브 영상 수, 커밋 수, 노션 페이지 수 등 어디에나 적용 가능.
- **에이전트 vs 스크립트**: 스크립트는 정해진 순서만 실행하지만, Sequential Thinking을 쓴 에이전트는 user enumeration 방지 같은 보안 고려나 CORS 문제를 시키지 않아도 설계 단계에서 챙겼다.

## 관련
- [[mcp]]
- [[mcp-scope]]
- [[context7-mcp]] · [[github-mcp]] · [[notion-mcp]] · [[playwright-mcp]]
- [[sequential-thinking-mcp]], [[firecrawl-mcp]], [[memory-mcp]], [[slack-mcp]], [[supabase-mcp]]
- [[nested-agent]] — 여러 MCP 작업을 서브에이전트로 분산하는 다음 단계
- [[photocraft-mcp]]
- 원글: [Context7 + GitHub MCP 콤보](https://velog.io/@xorms/Context7-GitHub-MCP-%EC%BD%A4%EB%B3%B4)
- 원글: [Playwright + GitHub + Notion 3 MCP 콤보](https://velog.io/@xorms/Playwright-GitHub-Notion-3-MCP-%EC%BD%A4%EB%B3%B4-%EC%8B%A4%EC%8A%B5)
- 원글: [Notion MCP](https://velog.io/@xorms/Notion-MCP)
- 원글: [Sequential Thinking + GitHub + Notion 3 MCP 콤보](https://velog.io/@xorms/Sequential-Thinking-GitHub-Notion-3-MCP-%EC%BD%A4%EB%B3%B4)
- 원글: [Firecrawl MCP + 콤보 실습](https://velog.io/@xorms/Firecrawl-MCP-%EC%BD%A4%EB%B3%B4-%EC%8B%A4%EC%8A%B5)
- 원글: [Memory + Playwright + Notion + GitHub 4 MCP 콤보](https://velog.io/@xorms/Memory-Playwright-Notion-GitHub-4-MCP-%EC%BD%A4%EB%B3%B4)
- 원글: [Slack MCP](https://velog.io/@xorms/Slack-MCP)
- 원글: [Supabase MCP](https://velog.io/@xorms/Supabase-MCP)
