---
type: concept
modified: 2026-10-20
sources: [_private/raw/notion/Vibe Coding/Claude Code/에이전트 개념 사전 3f6d8df03cab813ab699d98ecb701995.md, _private/raw/notion/Vibe Coding/Terminology 311d8df03cab80c0bc0dd5799dc46b31.md, _private/raw/velog/AI-생태계-탐험-로그/2026-10-20-LLM-Wiki-운영편-2-정규식이-놓친-비밀번호-숫자는-맞는데-남은-1편-부탁을-강제로-바꾸는-운영.md]
tags: [claude-code, hook, harness, 보안]
---

## 한 줄 정의
[[claude-code]]가 일하는 흐름 중 정해진 시점(이벤트)에 **조건이 맞으면 무조건** 실행되는 자동 장치다. 비유하면 사람이 나가면 알아서 꺼지는 센서등이다.

## 핵심 내용
작성 시점 기준 (2026-10): 2026-10-11, Claude Code v2.1.296. 이벤트 수·핸들러 종류는 버전에 따라 바뀔 수 있으니 [공식 문서](https://code.claude.com/docs/en/hooks)로 다시 확인한다.

### 실행 여부를 누가 정하나

| 부품 | 실행 여부를 누가 정하나 | 비유 |
|---|---|---|
| `CLAUDE.md` | Claude가 읽고 따를지 판단 | 벽 포스터 |
| MCP | Claude가 쓸지 말지 판단 | 공구함 |
| **훅** | **이벤트가 생기면 무조건** | 센서등 |

- **`CLAUDE.md`는 보장이 아니다.** 대부분 지키지만 100%는 아니다. "파일을 수정할 때마다 반드시 검사"처럼 꼭 지켜야 하는 규칙은 훅으로 건다.

### 3단 구조: 이벤트 → 매처 → 핸들러
1. **이벤트(Event)**: 언제? 예: 도구 실행 직후
2. **매처(Matcher)**: 어떤 경우에만? 예: 파일을 쓰거나 고칠 때만 (`Edit|Write`)
3. **핸들러(Handler)**: 무엇을 실행? 예: 검사 스크립트

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "/path/to/lint-check.sh" }
        ]
      }
    ]
  }
}
```
읽는 법: PostToolUse(도구 실행 직후)에 → Edit나 Write 도구일 때만 → 이 스크립트 실행.

### 대화 한 번에 훅이 끼어드는 지점

| 이벤트 | 언제 | 대표 용도 |
|---|---|---|
| `SessionStart` | 세션이 열리거나 이어질 때 | 현재 브랜치, 열린 이슈 같은 상황 정보 넣기 |
| `UserPromptSubmit` | 프롬프트가 Claude에게 가기 직전 | 관련 기록을 찾아 함께 붙이기 |
| `PreToolUse` | 도구 실행 직전 | 위험한 명령 차단. 여기서 막을 수 있다 |
| `PostToolUse` | 도구 실행 직후 | 파일 수정 후 자동 검사·정리 |
| `Stop` | 답변을 마칠 때 | 결과 기록, 알림 |

- 전체 이벤트는 30개가 넘는다. `SubagentStart`/`SubagentStop`처럼 세밀한 시점도 있다.

### 핸들러 5종

| 종류 | 하는 일 |
|---|---|
| `command` | 셸 명령 실행 |
| `http` | 지정한 주소로 HTTP 요청 |
| `mcp_tool` | MCP 도구 호출 |
| `prompt` | 모델에게 한 번 판단을 맡김 |
| `agent` | 서브에이전트가 조건을 확인 |

- **훅이 MCP를 부를 수 있다.** 훅과 MCP는 경쟁 관계가 아니라 조합하는 관계다. MCP는 Claude가 필요할 때 꺼내 쓰는 공구함이고, 훅은 그 공구를 정해진 시점에 무조건 쓰게 만들 수 있다. → [[mcp]]

### 막는 방법: 종료 코드
- `exit 0`은 통과, `exit 2`는 차단이다(PreToolUse라면 도구 실행이 막힌다).
- **함정: `exit 1`은 막지 않는다.** 보통 "실패"를 뜻하는 코드지만 훅에서는 차단이 아니다. 확실히 막으려면 `exit 2`.

### 저장 위치 = 적용 범위
`~/.claude/settings.json`(내 모든 프로젝트), `.claude/settings.json`(프로젝트, git으로 팀 공유), `.claude/settings.local.json`(프로젝트, 나만), 플러그인 `hooks/hooks.json`(플러그인이 켜져 있을 때). MCP·플러그인과의 비교는 [[mcp-scope]]. 설정된 훅과 출처는 `/hooks`로 확인한다.

### 훅과 비슷한 부품: 모드(Mod)
- 모드는 Claude Code 안에서 도는 JavaScript/TypeScript 함수다. 설정 훅은 바깥에서 스크립트를 실행하지만, 모드는 안에서 돌아서 화면(옆 패널, 프롬프트 위 띠)도 그릴 수 있다. 요구 버전 v2.1.287 이상.
- 모드는 내 권한으로, 샌드박스 없이 실행된다. 믿을 수 있는 출처만 설치한다.

| | 모드 | 설정 훅 | 스킬 | MCP |
|---|---|---|---|---|
| 정체 | Claude Code 안에서 도는 함수 | 이벤트 때 도는 스크립트 | 지시서 | 외부 도구 서버 |
| 화면 그리기 | 가능 | 불가 | 불가 | 불가 |
| 언제 쓰나 | 패널·명령 추가, 이벤트 가로채기 | 막기·허용·기록 | 반복 지시 저장 | 외부 시스템 연결 |

## 언제 쓰나 (상황 예시)
- 비밀값 파일 읽기·위험 명령을 **도구 실행 전에** 막을 때 (PreToolUse + exit 2) → [[claude-code-setup]], [[ai-vault]]
- 파일 수정 뒤 자동 린트·검사 (PostToolUse)
- 세션 기록을 자동으로 남길 때 → [[claude-mem]]
- 매 프롬프트에 추천 정보를 끼워 넣을 때 (UserPromptSubmit) → [[ruflo]]의 라우터 훅

## 실습에서 배운 것 / 트러블슈팅
훅 실습 기록은 각 도구 페이지에 있어서 여기서는 링크만 둔다.
- [[claude-code-setup]]: 비밀값 차단 PreToolUse 훅, 훅 + `permissions.deny` 이중 방어, 훅은 세션 시작 때 로드되므로 재시작 필요
- [[ai-vault]]: 파일을 쓰는 순간의 가드 훅. 훅은 도구 호출만 보므로 스크립트로 직접 쓴 파일은 검사 밖이었던 사례
- [[ai-vault]] (2026-10-20): Write/Edit 매처만 걸어 둔 가드는 Bash 도구의 `sed -i`·리다이렉트·`tee` 쓰기를 못 본다. Bash 호출의 명령 문자열도 검사해, 보호 구역을 대상으로 한 셸 쓰기를 exit 2로 막았다(차단 8개·허용 6개 명령으로 시험 후 적용).
- [[ruflo]]: 설치 메시지의 "훅 7종"과 실제 구성의 차이, pre-bash 차단 훅과 route 훅
- [[claude-mem]]: 훅으로 작업을 자동 기록하는 플러그인

## 관련
- [[claude-code]] · [[mcp]] · [[mcp-scope]] · [[claude-code-setup]] · [[claude-mem]] · [[ruflo]] · [[ai-vault]]
- 출처: [Claude Code 훅 공식 문서](https://code.claude.com/docs/en/hooks)
