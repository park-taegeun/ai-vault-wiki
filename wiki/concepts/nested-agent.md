---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Claude-Code-Nested-Agent.md]
tags: [agent, claude-code, subagent, parallel]
---
## 한 줄 정의
메인 에이전트가 작업을 나눠 서브에이전트를 만들고 각자에게 위임해 병렬로 처리한 뒤 결과를 모으는 구조. 팀장이 팀원에게 일을 나눠주는 방식.

## 핵심 내용
- 단일 에이전트: Claude → A → B → C (순차). Nested Agent: 메인 → 서브 A·B·C 동시 실행 → 결과 통합.
- **Task Tool**: 메인이 서브에이전트를 만드는 내부 도구.
  - 서브에이전트마다 **독립된 컨텍스트 윈도우(약 200K 토큰)**, 메인 세션과 분리.
  - 끝나면 전체 내용이 아니라 **요약(summary)만** 메인에 반환.
  - 최대 10개 동시 실행.
- **병렬/순차 판단 기준**:
  | 구분 | 조건 |
  |---|---|
  | 병렬 가능 | 작업 3개 이상 + 파일 겹침 없음 + 공유 상태 없음 |
  | 순차 필요 | 작업 간 의존성, 같은 파일 수정, DB→API→프론트 같은 선후관계 |
- **커스텀 에이전트(Custom Subagent)**: `.claude/agents/`에 마크다운 파일로 역할을 미리 정의. 프론트매터에 `name`, `description`, `tools`, `model`을 두면 메인이 `description`을 보고 위임 대상을 고른다.
- **비용 최적화**: `export CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-4-5` — 메인은 Opus로 판단·위임, 서브는 Sonnet으로 실행. "판단은 비싸게, 실행은 저렴하게."

## 언제 쓰나 (상황 예시)
- 서로 다른 파일을 각자 만드는 독립 작업이 3개 이상일 때.
- 프롬프트에는 **서브에이전트 수**와 **각자의 작업 범위(파일 단위)**를 명시한다. 예: "use 3 parallel sub-agents … Each agent works on its own file only. Do not share state between agents."
- 의존성이 있으면 순차로 하거나, 메인이 별도 통합 단계를 돌린다.

## 실습에서 배운 것 / 트러블슈팅
- 포트폴리오 사이트를 서브에이전트 3개(index.html / style.css / README.md)로 병렬 생성: `Running 3 agents…`, 각 7.8K 토큰 컨텍스트, 총 42초(순차 대비 약 3배 빠름).
- **독립 컨텍스트의 한계**: HTML 90줄, CSS 810줄이 생성됐지만 CSS 클래스가 HTML에 반영되지 않는 미스매치. B는 A의 HTML 구조를 모른다 — 병렬의 장점이자 한계.
- **트러블슈팅 — 수동 생성 에이전트 미인식**: `.claude/agents/`에 파일을 직접 만들었더니 `/agents`에서 "No agents found". 알려진 버그(GitHub Issue #4728, #11205, #20931). `/agents → Create new agent → Project (.claude/agents/)`로 TUI에서 만들면 정상 인식. 교훈: 문서보다 실제 동작을 먼저 확인.

## 관련
- [[mcp]] — 여러 MCP를 에이전트들에 분산하는 구조적 기반
- [[mcp-combo]] — 단일 에이전트로 여러 MCP를 엮는 방식과 대비
- [[slack-mcp]] — 시리즈 이전 편
- [[photocraft-mcp]]
- [[ruflo]]
- 원글: [Claude Code Nested Agent](https://velog.io/@xorms/Claude-Code-Nested-Agent)
