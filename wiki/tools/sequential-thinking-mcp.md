---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-03-31-Sequential-Thinking-MCP.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-31-Sequential-Thinking-GitHub-Notion-3-MCP-콤보.md, _private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Firecrawl-MCP-콤보-실습.md]
tags: [mcp, reasoning]
---
## 한 줄 정의
AI가 복잡한 문제를 풀 때 생각을 명시적인 단계로 나눠 순서대로(필요하면 되돌아가 수정하며) 전개하게 만드는 MCP 서버. 다른 MCP가 "무엇을 할 수 있는지"를 넓힌다면, 이건 "어떻게 생각하는지"를 바꾼다.

## 핵심 내용
- 제공 도구는 `sequentialthinking` 하나. 호출 시 속성:
  | 속성 | 역할 |
  |---|---|
  | `thought` | 현재 단계의 생각 |
  | `thoughtNumber` | 몇 번째 생각인지 |
  | `totalThoughts` | 예상 총 단계 수 (도중에 늘어날 수 있음) |
  | `nextThoughtNeeded` | 다음 단계가 필요한지 |
  | `isRevision` | 앞 단계 생각을 수정하는지 |
- `isRevision` 덕분에 추론 중 스스로 오류를 교정할 수 있고, `totalThoughts`는 고정값이 아니다.
- 등록:
  ```bash
  claude mcp add sequential-thinking --scope user -- npx -y @modelcontextprotocol/server-sequential-thinking
  ```
  확인은 `~/.claude.json`의 `mcpServers`에서 `"sequential-thinking": { "type": "stdio", "command": "npx", ... }` 항목. 트러블슈팅 없이 바로 동작했다.

## 언제 쓰나 (상황 예시)
답이 하나로 정해지지 않는, 트레이드오프가 있는 의사결정:
- 아키텍처 설계 ("이 서비스에 어떤 DB?")
- 버그 원인 분석 ("왜 이 API가 500을 반환하지?")
- 복잡한 리팩토링 계획 (변경 범위·순서 정리)
- 선택지 비교 ("Redis vs Supabase")
- 콤보에서 "판단" 담당: 수집한 데이터의 분류 등 ([[mcp-combo]])

## 실습에서 배운 것 / 트러블슈팅
- **단독 실습 (Node.js vs Python, 실시간 채팅 졸업 프로젝트)**: 7단계로 전개. 1) 평가 기준 5개(실시간 처리, 생산성, 생태계, 성능, 포트폴리오 가치)부터 정의 → 2) Node.js 분석 → 3) Python 분석 → 4) 실시간 채팅 관점 비교 → 5) 지시하지 않은 질문 "이 앱이 AI 기능을 원하는가?"를 스스로 제기 → 6) 시나리오 3개(순수 채팅 / 채팅+AI / Python 익숙)로 분기 → 7) 검증 후 추천, `nextThoughtNeeded: false`. 일반 응답이면 3~4단계에서 결론을 냈을 장면.
- **콤보 실습(JWT 인증 모듈 설계)**: 6단계 설계 중 보안 단계에서 요청하지 않은 `bcrypt saltRounds=10`과 **user enumeration 방지**(이메일 없음/비밀번호 틀림을 같은 에러 메시지로)를 스스로 포함.
- **실행 전 문제 예측**: HTML 테스트 UI 설계 Step 1에서 `file://`로 열면 CORS 제약이 생긴다는 걸 미리 발견하고 `express.static` 추가를 설계에 넣었다.
- **분류 판단**: Firecrawl 콤보에서 뉴스 44건을 모델/기술, 비즈니스/산업, 연구/논문 3개로 분류하며 판단 근거를 단계별로 로그에 남겼다(키워드 매칭이 아님).
- 정리: 핵심 가치는 답을 빨리 내는 게 아니라 **문제를 미리 발견하는 것**. 사고 과정이 투명하게 드러난다.

## 관련
- [[ai-산출물-검증]] — 졸업작품 [[띵동]]에서 결론 단계의 거짓 안심을 막는 데 쓴 사례
- [[mcp]]
- [[mcp-combo]]
- [[github-mcp]], [[notion-mcp]] — 3 MCP 콤보
- [[firecrawl-mcp]] — 뉴스 모니터링 콤보에서 분류 담당
- [[supabase-mcp]] — 시리즈 이전 편
- 원글: [Sequential Thinking MCP](https://velog.io/@xorms/Sequential-Thinking-MCP)
- 원글: [Sequential Thinking + GitHub + Notion 3 MCP 콤보](https://velog.io/@xorms/Sequential-Thinking-GitHub-Notion-3-MCP-%EC%BD%A4%EB%B3%B4)
- 원글: [Firecrawl MCP + 콤보 실습](https://velog.io/@xorms/Firecrawl-MCP-%EC%BD%A4%EB%B3%B4-%EC%8B%A4%EC%8A%B5)
