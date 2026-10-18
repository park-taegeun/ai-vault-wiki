---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-03-31-Supabase-MCP.md]
tags: [mcp, supabase, postgresql, database]
---
## 한 줄 정의
Claude Code가 내 Supabase(PostgreSQL 기반 BaaS) 프로젝트에 직접 접근해, 자연어만으로 스키마 설계·데이터 조작·RLS 정책 적용까지 하게 해주는 MCP 서버.

## 핵심 내용
- Supabase: PostgreSQL 기반 BaaS. REST API 자동 생성, Auth, Storage, Realtime 제공. Firebase의 오픈소스 대안.
- 동작 흐름: 자연어 입력 → Claude가 SQL로 변환 → Supabase MCP 도구 호출 → PostgreSQL 실행.
- 인증: 예전엔 PAT(Personal Access Token)를 헤더/환경변수로 넣었지만, 현재는 [[notion-mcp]]처럼 **OAuth 브라우저 인증**. 토큰을 직접 관리하지 않아도 된다.
- 등록 (원격 HTTP 서버, user 스코프 → [[mcp-scope]]):
  ```bash
  claude mcp add --transport http supabase "https://mcp.supabase.com/mcp" --scope user
  ```
  이후 `claude` 실행 → `/mcp` → `supabase · △ needs authentication` 선택 → 브라우저 로그인 → `Authentication successful. Connected to supabase.`
- 프로젝트 준비: supabase.com에서 New project 생성(실습은 Region `Northeast Asia (Seoul)`), `ACTIVE_HEALTHY` 상태가 되면 사용 가능.

## 언제 쓰나 (상황 예시)
- 프로토타이핑: "쇼핑몰 서비스에 필요한 테이블 구조 설계하고 바로 만들어줘"처럼 ERD 설계부터 SQL 실행까지 한 번에.
- 개발 중 스키마 변경: "users 테이블에 profile_image 컬럼 추가해줘".
- 디버깅: "user_id가 null인 이상한 데이터 찾아줘"처럼 이상 데이터 탐지.
- [[memory-mcp]]와의 구분: Supabase는 **애플리케이션 데이터**, Memory는 Claude 자신의 작업 맥락 저장용.

## 실습에서 배운 것 / 트러블슈팅
- 스키마 실습: users / posts(user_id FK) / comments(post_id·user_id FK) 3테이블을 자연어로 설계. FK와 `ON DELETE CASCADE`가 자동 적용되고, Schema Visualizer로 관계도 확인 가능.
- CRUD 실습: INSERT(users 3, posts 6, comments 12), SELECT+JOIN, GROUP BY(댓글 수 정렬), UPDATE(published 변경), DELETE(특정 유저 댓글 삭제) 모두 자연어로 처리.
- RLS(Row Level Security) 실습 — `posts`에 정책 3개:
  - SELECT: `published = true` (공개 글만 누구나 조회)
  - UPDATE / DELETE: `auth.uid() = user_id` (본인 글만)
  - `auth.uid()`는 현재 로그인 유저 ID를 반환하는 Supabase 내장 함수.
  - RLS 활성화 상태에서 INSERT 정책이 없으면 삽입이 막힌다.
- **트러블슈팅: PAT 방식 → Failed to connect.** 일부 문서에 남은 구버전 방식(`claude mcp add supabase -e SUPABASE_ACCESS_TOKEN=<REDACTED> -- npx ...`)은 연결 실패. 원인은 OAuth 방식으로의 변경. 위의 `--transport http` 등록 + `/mcp` OAuth로 해결.

## 관련
- [[mcp]]
- [[mcp-scope]]
- [[mcp-combo]] — 졸업 프로젝트 풀 사이클(Context7 + Supabase + GitHub + Notion) 조합
- [[notion-mcp]] — 같은 OAuth 인증 방식
- [[memory-mcp]] — 역할 비교
- [[sequential-thinking-mcp]] — 시리즈 다음 편
- 원글: [Supabase MCP](https://velog.io/@xorms/Supabase-MCP)
