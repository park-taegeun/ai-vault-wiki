---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-10-12-Claude-Code로-hwp-mcp-연결하기.md]
tags: [mcp, hwp, hwpx, claude-code, 한글문서]
---
## 한 줄 정의
hwp-mcp(treesoop)는 맥에서도 한컴오피스 없이 AI가 한글 문서(HWP/HWPX)를 읽고, 마크다운으로 바꾸고, 양식의 빈칸을 채우게 해주는 MCP 서버다. 실습 시점 npm 버전 0.3.0.

## 핵심 내용
- Claude 채팅에 공식 업로드 가능한 형식(PDF, DOCX, CSV, TXT, HTML, ODT, RTF, EPUB, JSON, XLSX)에 **HWP는 없다.** PDF 변환은 수정 결과를 한글로 못 돌려받고, 즉석 코드 해석은 매번 결과가 다르고 저장 시 파일이 깨질 위험이 있다. MCP는 언제 꺼내도 같은 방식으로 동작하는 검증된 도구다.
- **HWP**: 한컴의 예전 바이너리 포맷(전용 파서 필요). **HWPX**: ZIP 안에 XML이 든 구조(.docx와 같은 방식).
- 그래서 **읽기는 둘 다, 쓰기는 .hwpx만** 지원. 수정할 문서는 .hwpx로 시작한다.
- 구조: 엔진 **rhwp**(Edward Kim, Rust + WebAssembly) + 어댑터 **hwp-mcp**(MCP 계층). 기존 HWP 자동화는 대부분 한컴 COM API 기반이라 Windows 전용이었는데, WebAssembly 덕분에 맥에서도 동작한다.
- 도구 35개: 읽기/변환, 메타 조회, 페이지 렌더링(SVG), 텍스트 쓰기, 구조 편집, 서식, 이미지/표/신규 생성.
- 쓰기 도구는 기본적으로 원본을 덮어쓰지 않고 새 이름 파일(`_appended` 등)로 저장해 원본 양식을 보호한다.

### hwpx-mcp와 비교
| 항목 | hwp-mcp (treesoop) | hwpx-mcp (Dayoooun) |
|---|---|---|
| 엔진 | rhwp (Rust+WASM) | TypeScript XML 직접 파싱 |
| .hwp 읽기 | O | X |
| 쓰기 | .hwpx만 | .hwpx만 |
| 도구 수 | 35 | 77 |
| 설치 | npx 한 줄 | git clone 후 빌드 |
| 작업 방식 | 파일 넣으면 결과 파일(일회성) | 문서 열고 여러 번 편집 후 저장(세션형) |
| 강점 | 읽기, 마크다운 변환, 템플릿 채우기 | 세밀한 서식, 각주, 수식, Undo/Redo |

내용 파악·양식 채우기는 hwp-mcp, 문서 꾸미기는 hwpx-mcp.

## 언제 쓰나 (상황 예시)
1. 공고문 요약: 공모전·정부지원사업 공고문에서 마감일, 지원 자격, 제출 서류만 뽑기
2. 신청서 자동 작성: `{{}}` 템플릿 양식에 값만 바꿔 반복 생성 (채운 뒤 다시 읽어 검증 필수)
3. 문서 아카이빙: 학교·공공 문서를 마크다운으로 변환해 Notion이나 Obsidian에 정리

## 실습에서 배운 것 / 트러블슈팅
### 설치·등록 (Node 20 이상)
```bash
node --version   # v24.7.0
claude mcp add hwp-mcp --scope user -- npx -y hwp-mcp@latest
claude mcp list | grep hwp-mcp   # hwp-mcp: npx -y hwp-mcp@latest - ✔ Connected
```
- `@latest`를 붙인 이유: npx 캐시에 옛 버전(v0.2.0, 서버가 조용히 종료되는 버그)이 남아 있으면 그걸 실행할 수 있다.
- 등록 후 **세션을 새로 시작해야** 도구가 로드된다. `/mcp`에서 도구 35개 확인.
- Claude Code(CLI)와 Claude Desktop(GUI)은 MCP 등록이 별도이고, claude.ai 웹에서는 로컬 MCP가 동작하지 않는다 → [[mcp-scope]]

### /context로 본 기본 비용 (Opus 5.5 환경)
- 1M 중 66k(7%) 사용, 화면 칸 하나 약 5k. 대화 전 기본요금(System prompt·tools·MCP tools·Skills 등) 약 42k.
- MCP 도구 227개가 등록돼 있어도 MCP tools는 6.7k(필요할 때 불러오는 방식으로 추정). Skills가 9.9k로 더 컸다 → 토큰을 아끼려면 MCP보다 안 쓰는 플러그인 정리가 효과적일 수 있다.
- 에이전트는 세션 시작 때 읽은 도구 설명서와 요청을 비교해 도구를 스스로 고른다. "hello.hwpx 읽어줘"만으로 `read_hwp`가 호출됐다.

### 요약 — 없는 정보는 없다고 답함
실제 안내문(.hwp)에서 "마감일, 지원 자격, 제출 서류만" 요청 → 지원 자격만 정리하고 마감일·제출 서류는 "문서에 없다"고 답했다. 항목을 구체적으로 지정하면 빈 항목이 바로 드러난다.

### 마크다운 변환이 뭉개진 이유
- `convert_hwp_markdown` 결과가 2열 표 한 칸에 본문 전체가 한 줄로 들어갔다. 한국 공문서는 테두리를 치려고 문서 전체를 표 한 칸에 넣는 경우가 많고, 마크다운 표 칸엔 줄바꿈이 안 되기 때문.
- 해결: MCP는 정확한 추출, Claude는 재구성으로 역할을 나눔. 프롬프트 예: "제목·소제목·목록 형태로 다듬어줘. 원본 내용은 하나도 빠뜨리지 말고, 표는 진짜 표 데이터일 때만 써줘"

### 템플릿 채우기의 조용한 실패
| 단계 | 도구 | 결과 |
|---|---|---|
| 양식 만들기 | create_hwpx_document | 성공 (4줄이 문단 1개에 줄바꿈으로 들어감) |
| 채우기 | fill_hwp_template | "저장 완료" 메시지, 그러나 0건 치환 |
| 검증 | read_hwp_text | `{{이름}}` 등이 그대로 남음 |
| .hwp 쓰기 | replace_hwp_text | 실패 (.hwp 쓰기 미지원 에러) |
- 에러 없이 성공처럼 끝났지만 실제론 아무 일도 안 한 **조용한 실패(silent failure)**. 반면 .hwp 쓰기 실패는 원인과 해결책(.hwpx로 저장 후 시도)을 알려준 친절한 실패. 에러 문구엔 "v0.2"라 나오지만 `npm view hwp-mcp version`은 0.3.0.
- 가설: 채우기 도구가 한 문단에 섞인 `{{…}}`를 못 찾는다. 검증: 한 줄 양식 생성 → `append_hwp_paragraph`로 줄마다 별도 문단 추가 → 채우기 → **3건 치환 성공**, 다시 읽어 확인. (내부 동작은 XML 구조를 보고 한 추정)
- 한컴오피스에서 양식을 만들 때도 `{{이름}}`은 한 번에 이어서 입력한다. 중간에 서식을 바꾸면 파일 속에서 글자가 쪼개져 찾기가 실패할 수 있다.
- 교훈: 도구의 "성공" 메시지는 결과가 아니다. **결과를 다시 읽어 확인하는 단계를 프롬프트에 넣는다.** [[slack-mcp]]에서 `SLACK_TEAM_ID`가 빠졌을 때 원인을 바로 알려주지 않던 것과 같은 유형.

## 관련
- [[mcp]]
- [[mcp-scope]]
- [[scrapling-mcp]]
- [[slack-mcp]]
- [[photocraft-mcp]]
- 원글: [Claude Code로 hwp-mcp 연결하기](https://velog.io/@xorms/Claude-Code%EB%A1%9C-hwp-mcp-%EC%97%B0%EA%B2%B0%ED%95%98%EA%B8%B0)
