---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Memory-MCP.md, _private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Memory-Playwright-Notion-GitHub-4-MCP-콤보.md]
tags: [mcp, memory, knowledge-graph]
---
## 한 줄 정의
Claude가 정보를 로컬 파일(`memory.json`)에 Knowledge Graph(엔티티·관계) 형태로 저장하고 다음 세션에서 불러오게 해, 세션을 넘는 장기 기억을 주는 공식 MCP 서버(`@modelcontextprotocol/server-memory`).

## 핵심 내용
- 문제: Claude Code는 대화가 끝나면 맥락을 잊어 매 세션 배경 설명을 반복해야 한다.
- Knowledge Graph: **엔티티(노드)**와 **관계(엣지)**로 표현. 예: `[나] --owns--> [AI생태계탐험로그]`, `[AI생태계탐험로그] --next_practice--> [Memory_MCP]`. 문장 저장보다 특정 엔티티 기준으로 관련 정보를 빠르게 조회·추론할 수 있다.
- 역할 비교: Context7 = 외부 라이브러리 문서, [[supabase-mcp]] = 애플리케이션 DB 데이터, Memory = **Claude 자신의 작업 맥락**.
- 등록·확인:
  ```bash
  claude mcp add --scope user memory -- npx -y @modelcontextprotocol/server-memory
  claude mcp list   # memory ✓ Connected
  ```

## 언제 쓰나 (상황 예시)
- 장기 프로젝트 컨텍스트 유지(스택, 진행 상황).
- 사용자 프로필 누적(선호 스택, 작업 스타일, 완료 실습).
- 의사결정 기록(기술 선택 이유를 관계로 저장해 추적).
- **파이프라인 상태 기준점(체크포인트)**: 마지막 상태를 저장해두고 실제 상태와 비교해 차이가 있을 때만 후속 작업 실행 → [[mcp-combo]].

## 실습에서 배운 것 / 트러블슈팅
- **저장 설계 원칙**: 목적은 새 세션에서 컨텍스트를 빨리 복원하는 것. 완료 실습 목록(이름만)·진행 중 실습·프로젝트 상태는 넣고, 포스팅 제목 전체·패키지명·설치 명령어·상세 환경 정보는 뺀다(그래프만 커지고 유지보수 부담).
- 실습: `create_entities`로 노드 5개, `create_relations`로 관계 6개 생성. Claude Code를 완전히 종료·재실행 후 조회하자 전부 복원됐다.
- 트레이드오프 3가지:
  1. **수동 유지보수** — 자동 갱신 안 됨. 기존 동기화 루틴(Velog 동기화 프롬프트)에 Memory 갱신을 끼워 넣어 해결.
  2. **명시적 호출 필요** — 세션 시작 시 자동으로 읽히지 않는다. "Memory MCP에서 현재 프로젝트 상태 조회해줘"를 습관적으로 입력.
  3. **로컬 파일 의존** — `memory.json`이 로컬에 있어 기기 이전 시 직접 복사. 클라우드 동기화 없음.
- 4 MCP 콤보에서 포스팅 수 10 → 11 갱신, `Memory_MCP` 상태를 학습 중 → 완료로 갱신. 기억 저장소를 넘어 상태 관리 도구로 동작했다.

## 관련
- [[mcp]]
- [[mcp-combo]] — Memory + Playwright + Notion + GitHub 동기화 콤보
- [[supabase-mcp]] — 역할 비교
- [[firecrawl-mcp]] — 시리즈 이전 편
- [[slack-mcp]] — 시리즈 다음 편
- [[claude-mem]]
- [[notion-mcp]]
- 원글: [Memory MCP](https://velog.io/@xorms/Memory-MCP)
- 원글: [Memory + Playwright + Notion + GitHub 4 MCP 콤보](https://velog.io/@xorms/Memory-Playwright-Notion-GitHub-4-MCP-%EC%BD%A4%EB%B3%B4)
