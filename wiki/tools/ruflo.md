---
type: tool
modified: 2026-10-19
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-10-11-Claude-Code에-Ruflo-붙여보기.md, _private/raw/notion/Vibe Coding/Claude Code/에이전트 개념 사전 3f6d8df03cab813ab699d98ecb701995.md]
tags: [claude-code, agent, harness, hook, 검증]
---
## 한 줄 정의
Ruflo(옛 이름 Claude Flow, MIT)는 Claude Code 위에 훅·MCP·메모리·에이전트 정의를 얹어 에이전트 여러 명을 "팀(스웜)"으로 운영한다는 **메타 하네스**다. 실습 기준 3.56.5.

## 핵심 내용
### 모델 · 하네스 · 에이전트
- 모델(LLM): 두뇌. 혼자서는 파일·명령·기억을 못 한다.
- 하네스: 모델이 실제로 일하게 하는 장치 전체(루프, 파일·터미널 도구, 권한, 훅, CLAUDE.md 읽기). Claude Code가 대표적.
- 에이전트 = 모델 + 하네스. Ruflo는 그 위에 한 층 더 얹는다.

### 구성요소
| 구성요소 | 의미 |
|---|---|
| 스웜(swarm) | 에이전트 팀 |
| 토폴로지 | 팀 조직도 (hierarchical 위계형, mesh 수평형) |
| 퀸(queen) | 팀장 에이전트 |
| 라우터 | 일을 어느 에이전트에게 줄지 배분 |
| 벡터 메모리 | 뜻으로 찾는 업무 일지 |
| 데몬 | 백그라운드 상주 프로그램 |

- Ruflo가 만든 설정 문서에 직접 "실행은 Claude Code의 Agent 도구, 조정은 Ruflo MCP 도구"라고 적혀 있다. Ruflo는 일을 직접 하지 않는다.
- "AI 직원 100명"은 동시 작업 인원이 아니라 에이전트 카탈로그(정의 목록) 수다. Claude 사용량은 그대로 차감된다.
- 처음엔 에이전트 **4~8개**로 시작하는 것을 권장한다(개념 사전 2026-10-11 기준).
- **벡터 메모리 예시**: "기능 변경 뒤 단위 테스트와 린트를 모두 실행한다"로 저장해 두면 "기능 변경 뒤 검증"으로 검색해도 찾아진다는 것이 원리 설명이다. 한국어에서 이 검색이 실패한 실측은 아래 "메모리 — 한국어 의미 검색의 함정".
- 설치하면 생기는 파일

| 파일·폴더 | 정체 |
|---|---|
| `CLAUDE.md` | Ruflo 사용법이 적힌 매뉴얼 |
| `.claude/settings.json` | 훅과 모드 설정 |
| `.claude/agents/` | 에이전트 직무 기술서 (개념 사전에 "설치 후 확인 필요"로 적힘) |
| `.claude/skills/` | 스킬 |
| `.claude-flow/` | Ruflo 자체 데이터 (메모리 저장소 등) |

### Claude Code 확장 부품 — 실행을 누가 정하나
| 부품 | 실행 결정 |
|---|---|
| CLAUDE.md | Claude가 판단 (보장 X) |
| MCP | Claude가 판단 |
| 훅(Hook) | 이벤트 발생 시 무조건 |
| 서브에이전트 | Claude 판단 또는 지시 |
| 스킬 | 호출 또는 Claude 판단 |
| 플러그인 | 위 부품 묶음 |
- **훅만 무조건 실행된다.** 구조는 이벤트 → 매처 → 핸들러. SessionStart, UserPromptSubmit, PreToolUse(차단 가능), PostToolUse, Stop 등 30개 이상.
- 차단하려면 **exit 2**. exit 1은 차단되지 않는다(함정).
- Claude Code 2.1.287부터 모드(Mod, 내부 JS 함수 + UI)가 생겼는데 샌드박스 없이 무조건 실행된다.
- 훅 저장 위치 = 적용 범위 → [[mcp-scope]]. 훅 개념 전체는 [[claude-code-hook]].

## 언제 쓰나 (상황 예시)
- 작은 기능 단위 작업이라면 **Ruflo 없이** Claude Code 기본 서브에이전트 + 잘 짠 프롬프트(역할·제약·검증·관찰 기록)로 같은 역할 분담이 가능했다. → [[nested-agent]]
- 큰 다파일 작업, hive-mind, 백그라운드 워커에서의 이점은 아직 검증하지 않았다.

## 실습에서 배운 것 / 트러블슈팅
환경: node v24.7.0, claude 2.1.296. 참고 가이드는 2026-08-06 기준 v3.32.x.

### 안전 설치 레시피
```bash
# 빈 폴더에 git 기준점부터
mkdir ruflo-starter && cd ruflo-starter
git init && git commit --allow-empty -m "init: empty practice folder"

# ① 전역 파일·모드 없이 버전 고정 설치
npx ruflo@3.56.5 init --no-global --no-mods
# ② 런타임 파일 git 제외 (Ruflo의 .gitignore엔 메모리 DB가 빠져 있음)
printf '\n.swarm/\nruvector.db\n' >> .gitignore
git check-ignore -v .swarm/ ruvector.db
# ③ settings.json env에 RUFLO_NO_AUTO_ENABLE=1, RUFLO_FUNNEL=0
# ④ .mcp.json과 CLAUDE.md의 @latest(16곳)를 @3.56.5로 고정
# ⑤ 자동 허용 목록(permissions) 재검토
```
- 위저드(init wizard)는 `--no-global` 처리 코드가 없어 전역 `~/.claude/CLAUDE.md`에 Ruflo 블록을 무조건 추가하고, 모드도 질문 없이 설치한다. Full 프리셋은 로그인이 필요한 클라우드 MCP 2개까지 추가.
- `RUFLO_NO_AUTO_ENABLE=1`: 첫 세션에 전역 `~/.claude/settings.json`에 홍보성 스피너 문구 추가를 막음. `RUFLO_FUNNEL=0`: 매 세션 funnel.ruv.io에서 홍보 메시지 다운로드, 사용 한도 도달 시 홍보 문구 삽입을 막음.
- MCP 서버 이름은 `ruflo`가 아니라 `claude-flow`. 가이드대로 수동 등록하면 중복 등록된다.
- 설치 요약은 "110개"였지만 git으로 세면 파일 253개, 55,310줄(에이전트 17, 스킬 30, 명령어 16). 요약 메시지보다 git 숫자가 정확하다.
- 커밋 9개 중 실제 작업물은 1개, 나머지 8개는 안전하게 쓰기 위한 정리였다.

### 뜯어보기
- 설치 메시지는 훅 "7종"이었지만 실제로는 이벤트 10종에 실행 항목 16개. 그중 6개(pre-edit, post-bash, compact-manual/auto, status, notify)는 빈 껍데기.
- 의미 있는 훅: pre-bash(`rm -rf /` 같은 위험 명령을 exit 2로 차단), route(UserPromptSubmit에서 매 프롬프트마다 추천 에이전트 표를 컨텍스트에 삽입 = "라우터"의 실체).
- 권한: 자동 허용 4개(`mcp__claude-flow__*` 등), 차단 2개(`.env` 읽기). 환경변수로 Agent Teams 실험 기능을 켠다.
- 세션 시작 때 `statusline.cjs`가 자동 갱신됨(패키지 원본에 3.32.8 하드코딩). Claude는 되돌리자고 했지만 무결성 검사가 서명된 원본과 해시를 비교해 다시 덮어쓰는 구조라 수용했다. 갱신 중지 스위치는 `.claude/helpers/.LOCKED`. **AI의 제안도 소스로 검증한다.**

### 컨텍스트 비용
- claude-flow 하나가 도구 358개 등록(기존 MCP 11개 합계 192개의 약 2배). 하지만 MCP 도구는 on-demand라 도구 수 비용은 거의 0. 대화 0회 `/context`는 48.6k / 1M(5%), MCP 도구 항목 7k.
- 실제 매 요청 부담: Ruflo CLAUDE.md 3.7k + 스킬 목록 약 4.5k(추정) + 에이전트 17개 약 0.7k = 약 9~10k(1M 창의 약 1%).

### 메모리 — 한국어 의미 검색의 함정
- 임베딩 모델 `Xenova/all-MiniLM-L6-v2`(영어 위주)가 코드에 하드코딩되어 설정으로 못 바꾼다. 기본 임계값 0.3.
```bash
npx ruflo@3.56.5 memory store --key "test-rule" --value "..." --namespace project
npx ruflo@3.56.5 memory search --query "..." --namespace project --threshold 0
```
| 언어 | 관련 있는 검색 | 관련 없는 검색 | 판정 |
|---|---|---|---|
| 한국어 | 0.48(단어 안 겹침) / 0.85(겹침) | 0.64(점심 메뉴) | 실패 |
| 영어 | 0.25~0.30 | 0.00~0.02 | 성공 |
| 한↔영 | 0.00~0.09 | — | 실패 |
- 기본 임계값 0.3이면 영어 정답(0.25)은 빠지고 한국어 오답(0.64)은 통과한다. 한국어 사용자는 영어로 저장·검색하거나 키로 직접 조회.
- 가이드 키 예시 `--key "project/test-rule" --namespace project`는 `project/project/test-rule`로 중복 저장된다.
- 메모리는 `memory.db`(CLI)와 `agentdb-memory.db`(MCP) 두 곳에 저장(삭제는 둘 다 한 번에).

### 스웜 — 실제로 일한 건 Claude Code
```bash
npx ruflo@3.56.5 swarm init --topology hierarchical --max-agents 8 --strategy specialized
```
- maxAgents 8이 적용됐지만 설정 파일 곳곳엔 15가 남음. 스웜 생성만으로는 아무것도 실행 안 됨(에이전트 0, 작업 0).
- `slugify` 함수+테스트 작업: researcher는 메인이 직접, coder/tester/reviewer는 Claude Code 서브에이전트(general-purpose), 화면엔 Teammate/team-lead(Agent Teams). 라우터는 한국어 프롬프트에 "tester 60%" 추천(test 키워드 매칭). Ruflo 장부(agent list)는 내내 Idle, 작업 0, 메시지 0.

### Ruflo vs plain (같은 프롬프트, `/usage`)
| 항목 | Ruflo 재실행 | plain |
|---|---|---|
| 추정 비용 | $2.21 | $1.70 |
| output / cache read | 15.2k / 2.6M | 12.1k / 1.5M |
| 메인 요청 수 | 13 | 9 |
- 역할 분담은 같았는데 비용 약 30%, cache read 73% 증가. Ruflo CLAUDE.md·스킬이 매 요청 로드되고, Agent Teams는 팀원마다 CLAUDE.md·MCP·스킬을 각자 로드하기 때문으로 추정. 라우터는 재실행에도 같은 추천(학습 효과 안 보임).
- 결과물: Ruflo 재실행은 테스트 13/13 통과했지만 리뷰 에이전트가 찾은 버그를 안 고쳐 `नमस्ते`→`नमसत`, `ガギ`→`カキ`처럼 글자를 조용히 바꿨다. **테스트 통과 ≠ 정확함.** 3번 실행에서 설계가 3가지로 나와 도구 차이보다 실행마다의 편차가 컸다.
- 한계: 작은 단일 작업을 조건별 1~2회 실행한 관찰, 비용은 `/usage` 추정치. 결론은 "쓸모없다"가 아니라 "이 규모에서는 이점이 안 보였다".

### 도구 검증 방법론
1. 가이드 대신 패키지 소스를 직접 읽기
2. git 기준점으로 모든 변경 추적
3. 대조군 있는 실험(영어/한국어, Ruflo/plain)
4. AI의 제안도 소스로 검증

## 관련
- [[claude-code]] · [[claude-code-hook]]
- [[nested-agent]]
- [[mcp]]
- [[mcp-scope]]
- 원글: [Claude Code에 Ruflo 붙여보기](https://velog.io/@xorms/Claude-Code%EC%97%90-Ruflo-%EB%B6%99%EC%97%AC%EB%B3%B4%EA%B8%B0)
