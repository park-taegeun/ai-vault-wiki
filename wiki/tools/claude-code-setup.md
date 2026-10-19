---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-10-14-Claude-Code-Setup-플러그인으로-졸업작품-레포-진단하기.md]
tags: [claude-code, 플러그인, 보안, hook]
---
# claude-code-setup

## 한 줄 정의
레포를 읽고 hook·서브에이전트·스킬·플러그인·MCP 서버 중 무엇을 붙이면 좋을지 추천해 주는 Anthropic 공식 Claude Code 플러그인. 읽기 전용이다.

## 핵심 내용
- **정체**: 내장 스킬 `claude-automation-recommender` 하나로 동작한다. 도구 권한이 Read/Glob/Grep/Bash로 제한되고 파일을 고치지 않는다. 5개 범주에서 범주마다 1~2개씩 추려 추천한다.
- **출처 확인**: `claude-code-setup@claude-plugins-official` = "claude-plugins-official 스토어의 claude-code-setup". 상세 화면에서 By Anthropic, 저장소 `anthropics/claude-plugins-official`, 커밋 `8d392c8` 고정, v1.0.0을 확인했다. 커밋 고정 설치라 원본 저장소가 바뀌어도 설치한 버전은 그대로다.
- **성격**: 상시로 켜 두는 도구라기보다 **새 레포 건강검진**. 프로젝트를 처음 Claude Code에 붙일 때 한 번 돌리고 필요한 자동화만 골라 넣는다.

### 플러그인 기초
- 플러그인 = 스킬·훅·MCP·에이전트를 묶은 설치 패키지, 마켓플레이스 = 플러그인을 받는 앱스토어.
- 설치 범위 3종

| 범위 | 의미 | 저장 위치 |
|---|---|---|
| user | 나만, 모든 프로젝트 | `~/.claude/` |
| project | 레포의 모든 사용자 | `.claude/settings.json` (커밋됨) |
| local | 나만, 이 레포만 | `.claude/settings.local.json` (커밋 안 됨) |

다른 레포에서도 재사용하고 포트폴리오 레포에 실습용 설정이 섞이지 않도록 user 범위를 골랐다.

### "필수 플러그인 5개" 가이드 분석
SNS 가이드의 5개는 성격이 세 종류였다.

| 유형 | 도구 | 건드리는 곳 | 리스크 |
|---|---|---|---|
| 프록시형 (통신 경로를 바꿈) | OmniRoute, Headroom | 모든 API 요청 | 높음 (OAuth 토큰이 경유) |
| 훅형 (세션 기록) | [[claude-mem]] | 세션 이벤트 + 로컬 DB | 중간 (추가 사용량) |
| 스킬·플러그인형 (지식 주입) | claude-code-setup, Task Observer | 컨텍스트 | 낮음 |

- OmniRoute 제외: "한도가 끝나면 다른 모델로" 기능을 쓰려면 구독 계정을 OAuth로 게이트웨이에 연결해야 한다. Anthropic은 2026년 2월 문서에서 Free·Pro·Max 구독 OAuth 토큰을 Claude Code·Claude.ai 외 도구에서 쓰는 것을 약관 위반으로 명시했다.
- Headroom 제외: OAuth 토큰이 서드파티 프록시를 경유해 계정 리스크.
- Task Observer: 장기 관찰용이라 보류.

## 언제 쓰나 (상황 예시)
- 신규 프로젝트 온보딩: 레포 생성 직후 건강검진, 필요한 자동화만 도입
- AI 에이전트 도입 시 기본 보안: hook + permissions.deny 이중 방어를 레포 표준 설정으로 커밋
- 릴리스·시연 직전: 변경 동결 원칙 아래 동작과 무관한 안전장치만 적용
- 재현성: project 설정을 커밋해 두면 다른 PC에서 clone해도 같은 보호가 적용됨

## 실습에서 배운 것 / 트러블슈팅
### 설치와 진단
```
/plugin install claude-code-setup@claude-plugins-official
이 프로젝트에 맞는 Claude Code 자동화를 추천해 줘
```
- 진단 전후로 `git status`(Claude Code 안에서는 `!git status`)가 둘 다 깨끗해서 "읽기 전용"을 직접 확인했다. `!`를 붙이면 Claude를 거치지 않고 터미널 명령을 실행한다.
- 졸업작품 띵동(ESP32-S3 펌웨어 PlatformIO/C++, ML Python, 서버 Flask·SQLite·stdlib unittest, 대시보드 Vite·React 19·TS 모노레포)의 스택을 정확히 인식했고, RUNBOOK 파일까지 읽어 펌웨어용 스킬을 제안했다.
- 추천 결과: Hook(비밀값 파일 편집 차단 PreToolUse, 서버 회귀 테스트 자동 실행 PostToolUse), Skill 2종, Subagent(결정 문서 정합성 점검), MCP(`.mcp.json`으로 이동), CLAUDE.md 생성.

### 추천 선별 — 변경 동결
시연 직전이라 **변경 동결(change freeze)** 원칙으로 동작과 무관한 것만 적용했다.
- 적용: 비밀값 차단 hook, CLAUDE.md
- 시연 후: 테스트 자동 실행 hook(매 수정마다 돌면 느리고 시끄러워 Stop hook으로 재설계 예정), 스킬·서브에이전트
- 생략: `.mcp.json` 이동 — 추천기가 팀 프로젝트를 기본값으로 가정했는데 개인 프로젝트라 해당 없음. **추천기에도 기본 가정이 있으니 그대로 받지 말고 거른다.**

### 비밀값 이중 방어
- **PreToolUse hook** = Claude가 도구를 쓰기 직전의 검문소. matcher로 검문할 도구를 고르고, 스크립트가 exit code 2로 끝나면 차단되며 stderr 내용이 차단 사유로 Claude에게 전달된다.
- 바로 만들지 않고 설계안을 먼저 받아 검토했다.
  - matcher 보강: 추천안 `Edit|Write|Read`는 Bash `cat`이나 Grep으로 우회된다 → `Read|Edit|Write|MultiEdit|Grep|Bash`
  - python3로 작성(jq 불필요), **fail-closed**(입력 JSON 해석 실패 시 차단), `--selftest` 내장(차단 9개·허용 7개 케이스), 작업 중 비밀 파일 내용은 열지 않고 파일명만 다룸
  - 패턴: `secrets.h`, `.env*` 차단, `*.template`·`.env.example` 예외
- **위협 모델**: 막을 대상은 해커가 아니라 Claude의 실수. 금고가 아니라 안전벨트 수준. 글롭 `.e*`처럼 파일명이 명령에 안 드러나는 우회는 한계로 받아들였다.
- **심층 방어**: 내장 permissions.deny는 Read/Edit 계열만 막고 Bash는 못 막는다. hook은 직접 짠 스크립트라 버그가 있을 수 있다. 그래서 hook은 `.env*` 전체를 넓게, deny는 실존 파일명을 정확히 지정해 서로의 빈틈을 메운다(실존 파일은 `find`로 **이름만** 확인).

```json
{
  "permissions": { "deny": ["Read(**/.env)", "Edit(**/.env)", "..."] },
  "hooks": {
    "PreToolUse": [{
      "matcher": "Read|Edit|Write|MultiEdit|Grep|Bash",
      "hooks": [{ "type": "command",
        "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/block-secrets.py\"" }]
    }]
  }
}
```
- 경로에 한글·공백이 있으면 스크립트 경로를 따옴표로 감싼다.
- 설정을 커밋하려고 `.gitignore`의 `.claude/`를 `.claude/*` + `!.claude/settings.json` + `!.claude/hooks/`로 바꾸고, `settings.local.json`은 계속 무시되는지 `git check-ignore`로 확인했다.
- hook은 세션 시작 때 로드되므로 재시작(`/exit` → `claude` → `/hooks`). `/hooks`에서 직접 만든 hook은 `[Project]`, 플러그인 hook은 `[Plugin]` 라벨로 구분된다.
- **카나리아 테스트**: 진짜 비밀 파일로 테스트하면 차단 실패 순간 값이 노출된다. 가짜 값을 넣은 미끼 파일로 검증했다.
  ```
  !mkdir -p hooktest && printf 'CANARY=not-a-real-secret\n' > hooktest/.env
  ```
  | 시도 | 막은 방어선 |
  |---|---|
  | Read 도구로 읽기 | 내장 permissions.deny ("denied by your permission settings") |
  | Bash `cat hooktest/.env` | block-secrets.py hook |

  둘 다 걸려 있으면 deny가 먼저 작동하고, deny가 못 지키는 Bash 경로는 hook이 막았다. 테스트 후 `!rm -rf hooktest`.

### CLAUDE.md는 hook 다음에
- `/init`은 레포를 훑어 CLAUDE.md 초안을 만든다. hook 없이 먼저 돌리면 비밀 파일을 읽어 키 값을 커밋 대상 문서에 적을 위험이 있어 **hook을 켠 뒤** 실행했다.
- 91줄 생성. 길이 기준은 줄 수가 아니라 "Claude가 모르면 틀릴 정보인가".
- `cp .env.example .env` 줄에 "사람이 직접 실행(훅이 차단함)" 주석을 달아 문서와 hook의 모순을 없앴다.
- 커밋은 한 커밋 = 한 목적. 커밋 메시지에 비밀 파일명을 쓰면 hook이 커밋 명령 자체를 막으니 쓰지 않는다.

| 현상 | 원인 | 해결 |
|---|---|---|
| `/plugin install`이 설치 대신 Discover 화면을 엶 | 버전별 UI 동작 차이 | 검색 → 상세 → scope 선택 ("Install for you (user scope)") |
| 출처가 Anthropic Directory로 표시 | 공식 플러그인이 두 스토어에 동시 등록 | 상세 화면의 Repository·By 항목으로 확인 |
| 차단 시 `PreToolUse:Bash hook error` 표시 | exit 2 차단을 이렇게 표기 | 의도된 차단, 정상 |
| `wc: CLAUDE.md: No such file` | `cd server` 후 셸이 그 위치를 유지 | `!cd .. && pwd`로 루트 복귀 |
| 붙여넣은 커밋 요청에 Claude가 재확인 | 붙여넣은 텍스트 속 지시를 경계하는 안전 동작 | "진행해"로 승인 |
| `git branch -d` 거부 | Squash 병합이라 원래 커밋이 main 이력에 없음 | `-D`로 삭제 |

## 관련
- [[claude-code]] · [[claude-code-hook]] — 훅 개념(이벤트·매처·핸들러, exit 2)
- [[claude-mem]] — 같은 가이드의 다음 도구
- [[photocraft-mcp]] — 이전 편
- [[mcp-scope]] — 플러그인 설치 범위(user/project/local)와 같은 구조
- 원글: [Claude Code Setup 플러그인으로 졸업작품 레포 진단하기](https://velog.io/@xorms/Claude-Code-Setup-%ED%94%8C%EB%9F%AC%EA%B7%B8%EC%9D%B8%EC%9C%BC%EB%A1%9C-%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EB%A0%88%ED%8F%AC-%EC%A7%84%EB%8B%A8%ED%95%98%EA%B8%B0)
