---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-03-27-Context7-MCP.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-30-Notion-MCP.md]
tags: [mcp, claude-code]
---
# MCP (Model Context Protocol)

## 한 줄 정의
Claude 같은 모델이 외부 도구(API, 문서 시스템, DB, 브라우저)를 직접 호출할 수 있게 Anthropic이 설계한 프로토콜.

## 핵심 내용
- 기존 AI는 텍스트 입력 → 텍스트 출력이었다. MCP를 붙이면 실제 시스템에 접근해 **행동(action)** 한다. 비유: Claude는 두뇌, MCP는 손발.
- 모델이 외부 시스템을 부르는 행위를 **도구 호출(tool use)** 이라 한다. 정의된 함수를 실행하고, 결과가 다시 모델로 돌아와 답에 반영된다.
- Claude Code에서는 도구 이름 옆에 `(MCP)` 표시가 뜨면 MCP 경유 호출이다. 표시 없이 Bash 명령이 돌면 MCP를 우회한 것이다.

### transport 두 가지
| 구분 | stdio | HTTP transport |
|---|---|---|
| 실행 | `npx`로 로컬 프로세스 실행 | 운영사 서버에 HTTP 연결 |
| 인증 | 환경변수로 토큰 전달 | OAuth (브라우저 로그인) |
| 설치 | npx가 자동 설치 | 설치 불필요 |
| 등록 | `claude mcp add <이름> -e TOKEN=... -- npx ...` | `claude mcp add --transport http <이름> <url>` |
| 예 | [[context7-mcp]], [[github-mcp]], [[playwright-mcp]] | [[notion-mcp]] |

### 자주 쓰는 명령
- `claude mcp list` — 연결 상태 확인 (`✓ Connected`)
- `claude mcp get <이름>` — 개별 상태
- `claude mcp remove <이름>` — 제거
- Claude Code 안에서 `/mcp` — 목록과 인증 상태 (`△ needs authentication`이면 선택 후 Enter로 OAuth)
- 등록 범위는 [[mcp-scope]] 참고

## 언제 쓰나 (상황 예시)
- 학습 데이터에 없는 최신 문서가 필요할 때 → [[context7-mcp]]
- 이슈/PR/레포 같은 원격 작업 → [[github-mcp]]
- 문서 기록 → [[notion-mcp]], 브라우저 조작 → [[playwright-mcp]]
- 여러 개를 한 프롬프트에서 같이 쓰기 → [[mcp-combo]]

## 실습에서 배운 것 / 트러블슈팅
- 처음 MCP 도구를 호출할 때 허락 팝업이 뜬다. "Yes, and don't ask again"을 고르면 이후 자동 실행.
- 오래 안 쓰다가 `401 Authentication Error`가 나면 세션 만료다. Claude Code 안에서 `/login`으로 재인증.
- 에러가 나도 Claude가 원인을 해석하고 우회해 진행하는 "에이전트적 복구"가 여러 실습에서 반복 관찰됐다 (각 도구 페이지 참고).

## 관련
- [[mcp-scope]]
- [[mcp-combo]]
- [[context7-mcp]] · [[github-mcp]] · [[notion-mcp]] · [[playwright-mcp]]
- [[firecrawl-mcp]]
- [[hwp-mcp]]
- [[memory-mcp]]
- [[nested-agent]]
- [[obsidian-local-rest-api]]
- [[photocraft-mcp]]
- [[ruflo]]
- [[scrapling-mcp]]
- [[sequential-thinking-mcp]]
- [[slack-mcp]]
- [[supabase-mcp]]
- 원글: [Context7 MCP](https://velog.io/@xorms/Context7-MCP)
- 원글: [Notion MCP](https://velog.io/@xorms/Notion-MCP)
