---
type: tool
modified: 2026-10-19
sources: [_private/raw/notion/Vibe Coding/Claude Code/Mode 311d8df03cab80748ac5e08e90e32179.md, _private/raw/notion/Vibe Coding/Claude Code/With Antigravity 311d8df03cab8060b341e417e7f0e962.md, _private/raw/notion/Vibe Coding/Claude Code/명령어 치트 시트 311d8df03cab80138a47c25701571f3e.md, _private/raw/notion/Vibe Coding/Claude Code/생산성 Tip 312d8df03cab80f7827ee22bc49ad1eb.md, _private/raw/notion/Vibe Coding/Claude Code/에이전트 개념 사전 3f6d8df03cab813ab699d98ecb701995.md, _private/raw/notion/Vibe Coding/Terminology 311d8df03cab80c0bc0dd5799dc46b31.md, _private/raw/notion/Vibe Coding/Tools/AI 코딩 에디터 IDE 311d8df03cab80aca11fe6c538e7f9a4.md, _private/raw/notion/Vibe Coding/Tools/풀스택 프로토타입 생성 도구 계열 311d8df03cab801da7dccbdb9b6a30e2.md]
tags: [claude-code, agent, harness, cli, 바이브코딩]
---

## 한 줄 정의
Anthropic이 만든 터미널(CLI) 중심 에이전트형 코딩 도구다. 모델(LLM)에 반복 루프·도구·권한·훅·CLAUDE.md 읽기를 붙여 실제로 일하게 하는 **하네스**의 대표 예다.

## 핵심 내용
### 하네스: 모델 + 하네스 = 에이전트
- **모델**은 글을 읽고 쓰는 두뇌다. 혼자서는 파일 열기, 명령 실행, 지난 대화 기억을 못 한다.
- **하네스(harness)** 는 원래 말에 채우는 마구라는 뜻이다. AI에서는 모델이 실제로 일하게 해 주는 장치 전체를 가리킨다: 반복 루프(생각 → 도구 사용 → 결과 확인 → 다시 생각), 파일·터미널 도구, 권한 관리, 훅, `CLAUDE.md` 읽기.
- **에이전트**는 모델과 하네스 사이의 별도 층이 아니라 둘을 합친 결과물이다.
- 에이전트 여러 명을 팀으로 묶는 메타 하네스가 [[ruflo]]다.

### 모드 3종
작성 시점 기준 (날짜 미기록)

| 모드 | 동작 | 언제 |
|---|---|---|
| Plan Mode | 코드를 쓰기 전에 계획부터 세운다 | 복잡한 기능. 어려울수록 플랜 모드 |
| Normal Mode | 파일을 편집·생성할 때마다 사용자에게 확인을 받는다 | 기본 |
| Accept Edits On | 파일 편집 제안을 자동으로 수락한다. 모든 도구에 무제한 권한을 주는 것은 아니다 | 반복 리팩토링·단순 수정, 테스트 추가·코드 정리 같은 단순 자동화 |

- 모드 전환은 `shift + tab`. 원본 메모의 순환 순서는 일반 → 자동 승인 → Plan이다. 작성 시점 기준 (날짜 미기록)
- 여기서 "모드(Mode)"는 권한·작업 방식이다. Claude Code 화면과 동작을 바꾸는 확장 부품 "모드(Mod)"와는 다르다. → [[claude-code-hook]]

### 명령어
작성 시점 기준 (날짜 미기록). `/hooks`만 2026-10 기준(에이전트 개념 사전).

| 명령 | 하는 일 | 언제 |
|---|---|---|
| `claude` | Claude Code 실행 | |
| `claude --resume` | 이전 세션을 그대로 이어서 | |
| `claude --dangerously-skip-permissions` | 권한 확인을 건너뛰고 알아서 하게 하는 모드 | 격리된 환경이 아니면 주의 |
| `/init` | `CLAUDE.md` 자동 생성 | 새 프로젝트 시작 |
| `/doctor` | 환경 진단·문제 해결 | 에러가 났을 때 |
| `/model` | 모델 변경 | |
| `/compact` | 대화를 압축해 토큰 절약 | 대화가 길어졌을 때 |
| `/clear` | 대화 초기화 | 새 작업 시작 |
| `/context` | 현재 컨텍스트 윈도우 사용 현황 | |
| `/help` | 도움말 | 명령어가 기억나지 않을 때 |
| `/hooks` | 설정된 훅과 출처 확인 | → [[claude-code-hook]] |

- `/context`: 원본 노트(명령어 치트 시트)에는 "뭘 기억하는지 확인"으로 적혀 있었다. 같은 노션의 생산성 Tip에 따라 컨텍스트 윈도우 사용 현황을 보여 주는 명령으로 고쳐 썼다 (정정).

### 키보드 단축키
작성 시점 기준 (날짜 미기록). 원본 메모 그대로 옮겼다.

| 키 | 동작 |
|---|---|
| `shift + tab` | 모드 전환 (일반 → 자동 승인 → Plan) |
| `Esc` | 작업 중단 및 복구 |
| `Ctrl + C` | 강제 종료 |
| `Tab` | 자동 완성 |

### 생산성 팁
- **`@` 파일 지정**: `@파일명` 또는 `@폴더명`으로 대상을 콕 집어 수정·리팩토링·의존성 추가를 시킨다.
- **`/model`**: 원본 메모 기준으로 기본값은 가장 비싸고 똑똑한 Opus라 기본 작업엔 과하고, Pro 요금제면 Sonnet을 추천했다. 작성 시점 기준 (날짜 미기록)
- **`/compact` 먼저, `/clear`는 나중**: `/clear`는 컨텍스트를 전부 지운다. `/compact`는 이전 대화를 압축해 남기므로 먼저 써 본다.
- **`/context`**: 지금 컨텍스트 윈도우를 얼마나 쓰고 있는지 본다. 실측 예는 [[ruflo]]의 "컨텍스트 비용".
- **`!` 접두사**: 명령 앞에 `!`를 붙이면 Claude를 거치지 않고 셸에서 바로 실행한다(예: `!ls`, `!git status`). 안 붙이면 Claude가 읽고 의도를 파악해 실행 여부를 판단하므로 토큰과 시간이 든다. 파일 목록·git 상태처럼 결과만 빠르게 볼 때 쓴다.
- **메시지 큐**: Claude가 작업하는 중에 다음 명령을 입력하면 대기열에 쌓였다가 작업이 끝나는 대로 이어서 시작한다.
- **PDF 읽기**: 파일을 터미널에 드래그 앤 드롭하고 "읽고 텍스트만 추출해줘"라고 하면 텍스트를 뽑아 지식 베이스 재료로 쓸 수 있다.

### 컨텍스트 윈도우
- AI가 한 번에 펼쳐 놓고 볼 수 있는 작업 책상의 크기다. 비용과 컨텍스트 윈도우는 토큰 단위로 잰다.
- 책상이 꽉 차면 오래된 내용을 요약해서 치운다. 이것이 **압축(compaction)** 이다. 서브에이전트([[nested-agent]])와 메모리가 필요한 이유도 "책상이 좁아서"다.
- 원본 노트(Terminology)에는 "대화가 길어지면 오래된 내용부터 잊음"으로만 적혀 있었다. 같은 노션의 에이전트 개념 사전에 따라 요약해 치우는 압축도 함께 적었다 (정정).

### Rule File과 Skill의 구분
- **Rule File**(Claude Code에선 `CLAUDE.md`): "이렇게 행동해"라는 **전체 행동 규칙**이다. 세션 시작 때 읽어 두지만 100% 지킨다는 보장은 없다.
- **Skill**(`SKILL.md`): "이 작업은 이렇게 해"라는 **특정 업무 절차서**다. 매번 붙여 넣던 긴 프롬프트를 저장해 두고 `/이름`으로 불러 쓴다.
- 반드시 지켜야 하는 규칙은 둘 다 아니고 **훅**으로 건다. → [[claude-code-hook]]

### IDE 계열 vs CLI 계열 (원본 분류)

| | IDE 계열 (Cursor, Google Antigravity) | CLI 계열 (Claude Code, OpenAI Codex) |
|---|---|---|
| 인터페이스 | GUI | 터미널 |
| 주 사용자 | 프론트엔드, 일반 개발자 | 백엔드, DevOps |
| 자동화 | 상대적으로 낮음 | 높음 |
| 작업 흐름 | 상호작용 중심 | 스크립트 중심, 자동화 파이프라인에 통합 가능 |

- 이 밖에 문장 하나로 서비스 뼈대 전체를 만들어 주는 풀스택·프로토타입 생성 계열(Lovable, v0, Replit, Bolt)이 있다. MVP·프로토타입용이다.

## 언제 쓰나 (상황 예시)
- 여러 파일에 걸친 수정·리팩토링, 테스트를 돌리고 실패하면 고쳐 다시 돌리는 반복 작업
- 어렵고 큰 기능은 Plan Mode로 계획부터, 단순 반복 수정은 Accept Edits로
- 다른 에이전트 도구와 역할을 나눠 서로 검증하게 할 때 (아래 워크플로)

## 실습에서 배운 것 / 트러블슈팅
### Antigravity와 함께 쓰는 워크플로
유튜브 영상을 보고 정리한 흐름이다. 계획을 세우는 쪽과 검증하는 쪽을 다른 도구로 나눈다.
1. **Antigravity가 계획 작성**: 문제 해결 계획을 세워 `work-plan` 폴더에 문서로 저장한다.
2. **Claude Code가 계획 검증**: 문서를 검토해 보완사항을 알려 준다. 이때 **기존 문서를 덮어쓰지 않고 문서 아래에 덧붙인다.** 원래 계획과 보완 내용이 한 문서에 함께 남는다. (이유 미기록)
3. **Antigravity가 코드 수정**: 보완 내용을 확인하고 코드를 고친다.
4. **최종 리포트를 Claude Code에 전달**: Claude Code가 수정 사항이 제대로 반영됐는지 점검한다.
5. **TestSprite MCP로 테스트**: 마지막에 MCP 기반 테스트 도구로 확인한다. → [[mcp]]

## 관련
- [[claude-code-hook]] · [[ruflo]] · [[nested-agent]] · [[mcp]] · [[mcp-scope]] · [[claude-code-setup]] · [[claude-mem]] · [[ai-vault]]
- 출처: [With Antigravity 워크플로 영상](https://www.youtube.com/watch?v=TjSkQkNWJ3E&t=186s)
