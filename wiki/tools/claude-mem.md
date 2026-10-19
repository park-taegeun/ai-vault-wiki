---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-10-14-Claude-Code에-claude-mem-붙여보기.md]
tags: [claude-code, 플러그인, ai메모리, hook]
---
# claude-mem

## 한 줄 정의
hook으로 Claude Code의 작업을 자동 기록하고 다음 세션에 그 목차를 넣어 주는 서드파티 메모리 플러그인. 실험해 보니 "자동 기억"이라기보다 **"자동 목차 + 필요 시 열람"**이었다.

## 핵심 내용
> 실습 환경: macOS(Apple Silicon), Claude Code v2.1.299, claude-mem v13.39.0, Node.js v24.7.0, Bun 1.4.3, uv 0.12.10

### 5단계 동작
1. **기록**: hook이 도구 사용(파일 읽기·쓰기, 명령 실행)을 **관찰(observation)** 한 건으로 포착. v13.39.0 기준 hook 8개(Setup, SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure, Stop, SessionEnd).
2. **정리**: 백그라운드 워커가 요약용 AI(**provider**)로 관찰을 요약하고 유형(decision, sensitive 등)을 분류.
3. **저장**: SQLite(`~/.claude-mem/claude-mem.db`) + Chroma 벡터 색인.
4. **주입**: 다음 세션 시작 때 최근 관찰을 자동 주입.
5. **검색**: 상세 내용은 MCP 도구(`get_observations` 등)로 꺼냄.

핵심 설계는 **점진적 공개(progressive disclosure)**: 매 세션엔 제목만 올리고 본문은 필요할 때 연다. 관찰이 많이 쌓여도 컨텍스트 부담이 작다.

### 기억 장치 4종 비교
| | CLAUDE.md | Claude Code auto memory | [[memory-mcp]] | claude-mem |
|---|---|---|---|---|
| 누가 기록 | 사람 | Claude가 판단해서 | 명시적으로 시킬 때만 | hook이 자동으로 |
| 무엇을 | 규칙·명령어 | 중요한 사실 한 줄 | 엔티티·관계 | 작업 이력 |
| 세션 시작 때 | 전체 주입 | 목록(MEMORY.md) 주입 | 주입 안 됨 | 제목 목록만 주입 |
| 추가 비용 | 없음 | 없음 | 없음 | 요약용 AI 토큰 |
| 형태 | 내장 | 내장 | MCP | 서드파티 플러그인 |

## 언제 쓰나 (상황 예시)
- 매일 도는 뉴스 수집처럼 세션이 많이 쌓이는 반복 파이프라인 레포의 작업 이력 타임라인
- 장기 프로젝트 복귀: "지난주에 무엇을 결정했는지"를 목차로 보고 필요한 것만 열람
- 팀 AI 도구 도입 체크리스트: 레포 민감도별 provider 선택, 텔레메트리·fallback 기본값 점검
- 쓰지 말 곳: 비밀값·미공개 설계가 있는 레포에 무료 Gemini provider

## 실습에서 배운 것 / 트러블슈팅
### 설치 전 함정 3가지 (가이드에 없던 것)
1. **유료 클라우드가 기본 선택**: `npx claude-mem install` 대화형 설치기는 유료 "CMEM Pro"(30일 체험 후 구독)를 기본으로 골라 두고, 그러면 관찰이 cmem.ai 서버를 거친다 → `/plugin` 방식으로 설치.
2. **구독 인증이 기본 provider**: 기본 provider가 claude(구독 인증)이고, 막히면 구독으로 자동 전환하는 quota fallback도 있다. 설정 문서와 Gemini 문서의 기본값 설명이 달라 fallback을 명시적으로 off.
3. **텔레메트리 기본 활성(opt-out)**: `npx` 설치기는 동의를 묻지만 `/plugin` 방식은 그 질문을 건너뛴다.

### provider는 레포 민감도로 고른다
| 선택지 | 비용 | 계정 리스크 | 데이터 행방 |
|---|---|---|---|
| Gemini 무료 키 (선택) | 무료 | 없음 | Google (무료 등급은 제품 개선에 쓰일 수 있고 사람 검토 가능) |
| Anthropic API 키 | 종량제 | 없음 | Anthropic |
| 구독 (기본값) | 구독 한도 내 | 회색지대 | Anthropic |

구독 OAuth 회색지대: Anthropic은 구독 OAuth 토큰을 Claude Code·Claude.ai 외 도구(Agent SDK 포함)에서 쓰는 걸 허용하지 않는다고 밝히면서, Agent SDK를 쓴 로컬 개발·실험은 장려한다고도 밝혔다. claude-mem 기본값은 워커가 Claude Code 로그인 토큰을 읽어 자체 Agent SDK 프로세스에 넣는 구조라 여기에 걸린다. ([[claude-code-setup]]의 OmniRoute·Headroom 제외 판단과 같은 근거)

### 설치 순서
- **설정 파일을 설치보다 먼저** 만들어 첫 세션이 기본값(구독)으로 요약을 시작하지 않게 했다. 키는 클립보드에서 바로 읽어 화면·셸 기록에 남기지 않음, 기존 파일 덮어쓰기 방지, 권한 600, 앞 4자리만 마스킹 출력, 끝나면 클립보드 비우기(`pbcopy < /dev/null`).
  ```json
  {
    "CLAUDE_MEM_PROVIDER": "gemini",
    "CLAUDE_MEM_GEMINI_API_KEY": "<REDACTED>",
    "CLAUDE_MEM_QUOTA_FALLBACK_PROVIDER": "off"
  }
  ```
- 키 검증은 URL이 아니라 **헤더**(`x-goog-api-key`)로 models API를 호출(URL은 로그에 남기 쉬움). 모델 50개 조회로 정상 확인. 키가 `AIza…`가 아닌 `AQ.…` 형식이었지만 추측하지 않고 실제 호출로 검증.
- 실습 레포: `park-taegeun/ai-news-monitor` (예전에 [[github-mcp]]로 원격에만 만든 레포라 로컬에 클론해서 씀)
- Bun 필요: `brew install oven-sh/bun/bun` (`/plugin` 방식은 Bun을 자동 설치하지 않음)
- local scope 설치:
  ```
  /plugin marketplace add thedotmack/claude-mem
  /plugin install claude-mem@thedotmack
  ```
  `/plugin` → Installed 탭에서 Scope: local 확인. 구성은 skills 24개, hooks 8개, MCP 1개(mcp-search). 스킬 24개의 이름·설명이 매 세션 컨텍스트를 조금씩 먹는다.
- 텔레메트리 끄기: `npx claude-mem telemetry disable` → `npx claude-mem telemetry status`로 `DISABLED` 확인.

### 데이터 경로 검증
- `curl -s http://127.0.0.1:37701/api/health`로 보니 provider는 gemini인데 authMethod에 "Claude Code OAuth token"이 표시됐다. `CLAUDE_MEM_CLAUDE_AUTH_METHOD`를 `api-key`로 넣고 재시작해도 그대로(효과 불명).
- 그래서 키를 마스킹한 로그를 grep: 요약은 전부 "using Gemini", Anthropic·OAuth 관련 줄 0건. 그대로 쓰되 Claude를 직접 부를 수 있는 스킬(`/learn-codebase`, knowledge-agent)은 쓰지 않기로.
- 셸 히스토리 때문에 붙어 있던 `--dangerously-skip-permissions`를 뺐다. 외부 웹을 긁는 레포라 프롬프트 인젝션 위험이 있고 서드파티 스킬이 24개다. 이 옵션은 인터넷이 막힌 컨테이너 같은 격리 환경용이고, 반복 승인이 번거로우면 Shift+Tab(accept edits·auto 모드)이나 `permissions.allow`가 낫다.

### 탐침 실험 — 무엇이 기억되나
- 세션 1에 지어낸 탐침 2개를 심음: A "카테고리가 겹치면 모델/기술 우선"(파일에 기록), B "다음 주 DeepMind 소스 추가, 미확정"(대화로만, "파일엔 적지 마").
- **혼입 변수**: Claude가 B를 Claude Code auto memory(`~/.claude/projects/<project>/memory/`)에도 저장해 둠 → 세션 2 동안 폴더를 `memory.off`로 치워 변인 통제.
- 세션 2 자동 주입 목차: `#1 decision` 카테고리 규칙, `#2 sensitive` DeepMind 추가 계획(“미확정, 적지 마” 맥락 때문에 sensitive로 분류).
- 테스트 1(도구 금지, 주입 맥락만): A 세부 모름, B 존재는 앎, "다음 주" 모름, 미확정 여부는 "Planned"로 짐작.
- 테스트 2(`get_observations`만 허용): 전부 정답. Claude는 "기록에 근거했지만 파일로 검증하진 않았다"고 구분해 답했다.
- **결론**: 기억 여부를 가른 건 "파일에 썼냐 말로 했냐"가 아니라 **"관찰 제목에 들어갔냐"**. 1층 자동 목차 + 2층 필요 시 열람 구조.
- 덤: 다른 레포용 MCP가 user scope로 등록돼 있어 이 레포 세션에도 안내문이 들어왔고, Claude가 엉뚱한 레포 파일을 근거 후보로 언급했다 → [[mcp-scope]] 설계가 중요한 이유.

### 비용과 지연
| 항목 | 값 |
|---|---|
| 세션 시작 목차 읽기 (주입 화면 추정) | 335토큰 |
| 테스트 2 본문 열람 추가 토큰 | 약 326토큰 |
| 원래 작업 토큰 | 7,296토큰 |
| 관찰 생성 (Gemini) | 입력 약 9.2K + 출력 약 1.5K ≈ 1만 토큰 |
| 기록 지연 | 약 7분 (13:59 작업 종료 → 14:06 저장) |

주입 화면의 "95% 절약"은 **Claude 컨텍스트 기준**이고, 기록을 만드는 비용(이번엔 Gemini 약 1만 토큰)은 따로 든다. 무료 Gemini가 "Gemini paused on transient"를 반복해 기록이 늦었다 → 작업 직후 새 세션을 열면 방금 한 일이 아직 기억에 없을 수 있다.

### 뒷정리 (가짜 정보 3곳)
1. 레포: 탐침 파일 삭제 후 `git status` 확인
2. auto memory: 세션 2가 빈 `memory/`를 새로 만든 상태에서 `mv memory.off memory`를 하자 `memory/memory.off`로 **안에 중첩 이동**됨(대상 폴더가 있으면 `mv`는 그 안으로 옮김). 내용 확인 후 삭제.
3. claude-mem DB: 워커를 멈추고 `.worker-clean-shutdown` 확인 후 `claude-mem.db`, `-shm`, `-wal`, `chroma`, `chroma-sync-state.json`, `state`를 백업 폴더로 이동. `-wal`은 아직 본 DB에 반영 안 된 변경이라 같이 옮겨야 하고, `state/`는 대기 중 기록이 새 DB로 흘러드는 걸 막으려고 옮김. 새 세션에서 "This project has no memory yet" 확인 후 백업 삭제.

| 현상 | 원인 | 해결 |
|---|---|---|
| 설치기가 유료 CMEM Pro를 기본 선택 | 설치기 기본값 | `/plugin` 방식 설치 |
| `bun: command not found` | `/plugin`은 Bun 자동 설치 안 함 | `brew install oven-sh/bun/bun` |
| Gemini 키가 `AQ.` 형식 | 새 형식으로 추정 | models API 호출로 검증 |
| SessionStart `Executable not found in $PATH: "claude-mem"` | Setup hook이 실행 파일(`~/.local/bin/claude-mem`, 약 70MB)을 만드는 중에 SessionStart가 먼저 실행된 첫 실행 경합. 파일 생성 시각이 첫 세션 시작 시각과 같아 확정 | 재시작 |
| `--dangerously-skip-permissions`가 계속 붙음 | 셸 히스토리(↑) 재사용 | `claude`만 입력 |
| authMethod에 OAuth 표시 유지 | 표시 의미 불명 | 로그·문서로 확인 + Claude 호출 스킬 미사용 |
| 실험에 auto memory 혼입 | Claude Code 자체 기억 | 폴더 일시 이동으로 변인 통제 |
| 복구한 memory 폴더 안에 memory.off 중첩 | 대상 폴더가 있으면 `mv`는 안으로 이동 | 이름이 아니라 내용까지 `ls`로 확인 |

참고: 설치된 13.39.0의 hooks.json은 `claude-mem` 실행 파일을 직접 호출하지만 GitHub main 브랜치는 `node` 스크립트 방식이라 형태가 달랐다.

### 판정: 조건부 유지 (뉴스 수집 레포 한정, 3주 시험)
- 장점: 명시적 호출 없이 자동 기록([[memory-mcp]]의 한계 해결), 2층 구조라 평소 부담 작음, 관찰 유형 분류, provider를 바꿔 구독 미사용 가능
- 단점: 기본값에 숨은 설치 함정이 많음, "자동 기억"은 사실 "자동 목차", 무료 Gemini는 느리고 데이터 조건이 있음, 내장 auto memory와 역할이 겹침(auto memory는 "미확정, 적지 말 것"까지 한 줄로 매 세션 전달했다)
- 3주 후 기준: `get_observations`가 실제로 쓰였나, 재설명 시간이 줄었나
- 다음 실험 후보: 프롬프트마다 관련 관찰을 붙이는 `CLAUDE_MEM_SEMANTIC_INJECT`

## 관련
- [[claude-code]] · [[claude-code-hook]] — 기록에 쓰는 훅의 개념
- [[memory-mcp]] — 명시적 저장 방식의 비교 대상
- [[claude-code-setup]] — 같은 "필수 플러그인 5개" 가이드, 이전 편
- [[mcp-scope]] — user scope MCP가 다른 레포 세션에 섞인 사례
- 원글: [Claude Code에 claude-mem 붙여보기](https://velog.io/@xorms/Claude-Code%EC%97%90-claude-mem-%EB%B6%99%EC%97%AC%EB%B3%B4%EA%B8%B0)
