---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-03-27-Context7-MCP.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-27-Context7-GitHub-MCP-콤보.md]
tags: [mcp, claude-code, context7, 문서검색]
---
# Context7 MCP

## 한 줄 정의
라이브러리 공식 문서를 실시간으로 조회해 모델에 넣어 주는 MCP 서버. 학습 데이터에 없는 최신 API 때문에 생기는 할루시네이션을 줄인다.

## 핵심 내용
- 패키지 `@upstash/context7-mcp`, stdio 방식, Node.js **v18 이상** 필요.
- 프롬프트 끝에 `use context7`을 붙이면 활성화된다.
- 내부적으로 도구를 두 단계로 호출한다.
  1. `resolve-library-id` — 라이브러리 이름 → 문서 ID (예: `"React" → "/websites/react_dev"`)
  2. `query-docs` — 그 ID로 실제 문서 조회

설치:
```bash
node --version                # v18 이상
claude mcp list               # No MCP servers configured
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest
# Added stdio MCP server context7 to local config (설정은 ~/.claude.json)
claude mcp list               # context7: ... ✓ Connected
```
범용 도구라 `--scope user`로 등록하는 편이 낫다 → [[mcp-scope]].

## 언제 쓰나 (상황 예시)
| 상황 | 필요 여부 |
|---|---|
| 버전별 차이가 큰 라이브러리 API 사용법 | 필요 |
| 최신 기능 (Next.js App Router, React 19 등) | 필요 |
| 처음 쓰는 패키지 기본 사용법 | 필요 |
| 개념·원리 설명 | 불필요 |
| 알고리즘 설계, 로직 구성 | 불필요 |
| 리팩토링, 버그 수정 | 불필요 |

## 실습에서 배운 것 / 트러블슈팅
- 2026-03-27 실습: "React의 useEffect 클린업 함수 사용법 알려줘. use context7" → react.dev 기준으로 클린업 구조, 리스너/타이머/구독 해제, 호출 시점(언마운트·의존성 변경·StrictMode), AbortController 활용까지 답했다.
- [[github-mcp]]와 묶어 Express.js 최신 문서를 참조해 코드를 쓰고 PR까지 올렸다 → [[mcp-combo]].
- `401 Authentication Error` → `/login`. 첫 호출 허락 팝업 → "Yes, and don't ask again" (자세히는 [[mcp]]).

## 관련
- [[ai-산출물-검증]] — 졸업작품 [[띵동]]에서 공식 문서 조회로 1차 증거를 모은 사례
- [[mcp]]
- [[mcp-scope]]
- [[mcp-combo]]
- [[github-mcp]]
- [[notion-mcp]]
- 원글: [Context7 MCP](https://velog.io/@xorms/Context7-MCP)
- 원글: [Context7 + GitHub MCP 콤보](https://velog.io/@xorms/Context7-GitHub-MCP-%EC%BD%A4%EB%B3%B4)
