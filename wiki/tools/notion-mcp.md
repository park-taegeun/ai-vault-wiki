---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-03-30-Notion-MCP.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-30-Playwright-GitHub-Notion-3-MCP-콤보-실습.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-31-Sequential-Thinking-GitHub-Notion-3-MCP-콤보.md, _private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Firecrawl-MCP-콤보-실습.md, _private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Memory-Playwright-Notion-GitHub-4-MCP-콤보.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-31-Supabase-MCP.md]
tags: [mcp, claude-code, notion]
---
# Notion MCP

## 한 줄 정의
Notion이 공식 운영하는 원격 MCP 서버. Claude Code에서 Notion 페이지를 검색하고, 읽고, 만든다.

## 핵심 내용
- **HTTP transport + OAuth** 방식. stdio(npx) 방식인 [[context7-mcp]], [[github-mcp]]와 달리 설치할 것이 없고 토큰을 직접 관리하지 않는다 (비교표는 [[mcp]]).
- OAuth: 비밀번호 없이 특정 권한만 위임받는 개방형 인증 프로토콜. 브라우저에서 Notion에 로그인하면 Claude Code에 권한이 위임된다.
- 등록과 인증:
  ```bash
  claude mcp add --transport http --scope user notion https://mcp.notion.com/mcp
  claude          # 실행 후 /mcp
  # notion · △ needs authentication → 선택 후 Enter → 브라우저 로그인
  # Authentication successful. Connected to notion.
  ```
- 실습에서 쓴 도구: `notion-search`, `notion-create-pages`, `notion-fetch`.
- 마크다운으로 쓰면 헤딩·표·번호 목록·인라인 코드가 Notion 네이티브 블록으로 자동 변환되어 저장된다.

## 언제 쓰나 (상황 예시)
- 워크스페이스 페이지 목록 조회, 새 페이지 생성, 중첩 페이지를 읽고 요약.
- Notion에 있는 기획서·API 스펙을 읽고 바로 코드 생성.
- [[github-mcp]]와 묶어 머지된 PR을 개발 일지에 자동 기록.
- 크롤링·백업 결과를 대시보드 표로 정리 → [[mcp-combo]].

## 실습에서 배운 것 / 트러블슈팅
- 2026-03-30 실습: 3단계로 중첩된 페이지의 요약을 한 줄로 지시했더니 `notion-search → notion-search → notion-fetch` 순으로 스스로 계층을 내려갔다. 첫 검색 결과가 없으면 쿼리를 고쳐 재시도했다.
- 3 MCP 콤보에서는 "Velog 포스팅 대시보드" 페이지를 만들어 날짜/제목/태그/Velog 링크/GitHub 링크를 표로 정리했다. GitHub 백업이 끝난 뒤 **별도 프롬프트**로 요청했다.

- **콤보에서의 역할 = "무엇을 왜 만들었는지" 문서화**: JWT 인증 콤보에서 설계·구현 결과를 자동 기록.
- **대시보드 + 날짜별 서브페이지**: 뉴스 모니터링 콤보에서 "AI 뉴스 모니터링" 메인 페이지 아래 날짜별 서브페이지를 자동 생성.
- **대시보드 행 추가**: 포스팅 동기화 콤보에서 Velog 포스팅 대시보드에 신규 행만 추가. Memory 기준점 비교 덕분에 중복 행이 생기지 않았다.
- 인증 방식 참고: [[supabase-mcp]]도 Notion MCP와 같은 OAuth 브라우저 인증으로 바뀌었다.

## 관련
- [[single-source-of-truth]] — 졸업작품 [[띵동]]에서 노션을 기준이 아닌 보기 화면으로 둔 운영 체계
- [[mcp]]
- [[mcp-scope]]
- [[mcp-combo]]
- [[github-mcp]] · [[playwright-mcp]] · [[context7-mcp]]
- [[memory-mcp]]
- [[supabase-mcp]]
- [[sequential-thinking-mcp]]
- 원글: [Notion MCP](https://velog.io/@xorms/Notion-MCP)
- 원글: [Playwright + GitHub + Notion 3 MCP 콤보](https://velog.io/@xorms/Playwright-GitHub-Notion-3-MCP-%EC%BD%A4%EB%B3%B4-%EC%8B%A4%EC%8A%B5)
- 원글: [Sequential Thinking + GitHub + Notion 3 MCP 콤보](https://velog.io/@xorms/Sequential-Thinking-GitHub-Notion-3-MCP-%EC%BD%A4%EB%B3%B4)
- 원글: [Firecrawl MCP + 콤보 실습](https://velog.io/@xorms/Firecrawl-MCP-%EC%BD%A4%EB%B3%B4-%EC%8B%A4%EC%8A%B5)
- 원글: [Memory + Playwright + Notion + GitHub 4 MCP 콤보](https://velog.io/@xorms/Memory-Playwright-Notion-GitHub-4-MCP-%EC%BD%A4%EB%B3%B4)
- 원글: [Supabase MCP](https://velog.io/@xorms/Supabase-MCP)
