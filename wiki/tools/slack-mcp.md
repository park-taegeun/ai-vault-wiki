---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Slack-MCP.md]
tags: [mcp, slack, notification]
---
## 한 줄 정의
Claude Code의 자연어 요청을 Slack API 호출로 바꿔, 채널 조회·메시지 전송·히스토리 읽기 등을 하게 해주는 MCP 서버(`@modelcontextprotocol/server-slack`).

## 핵심 내용
- 구조: 워크스페이스 → 채널 → 메시지 → 스레드. 채널 중심이고 GitHub·Notion·Jira 등 외부 서비스 연동이 강점.
- 요청 흐름: Claude Code → Slack MCP Server → Slack API (Bot Token) → 워크스페이스.
- **Bot Token**(`xoxb-`로 시작): Slack App을 만들어 워크스페이스에 설치하면 발급. Bot 이름으로 메시지를 보낸다.
- **OAuth Scope**: App이 할 수 있는 행동 범위. 예: `chat:write`(전송), `channels:read`(채널 목록).
- **Scope ≠ 구현 범위**: Scope는 "허용 목록"일 뿐, 실제로 쓸 수 있는지는 MCP 패키지가 그 기능을 구현했는지에 달렸다.
- 설정 순서: 워크스페이스 생성 → api.slack.com/apps에서 `Create New App → From scratch` → `OAuth & Permissions`에서 Bot Token Scopes 추가 → `Install to Workspace → Allow`로 토큰 발급 → MCP 등록.
- 실습에서 쓴 Scope: `channels:history channels:read chat:write groups:history groups:read im:history im:read im:write users:read search:read.im search:read.mpim search:read.public`
- 등록:
  ```bash
  claude mcp add slack-mcp \
    -s user \
    -e SLACK_BOT_TOKEN=<REDACTED> \
    -e SLACK_TEAM_ID=<REDACTED> \
    -- npx -y @modelcontextprotocol/server-slack
  ```
  Team ID는 브라우저 주소 `https://app.slack.com/client/<TEAM_ID>/...`에서 `T`로 시작하는 값. 재실행 후 `/mcp`에서 `slack-mcp · ✔ connected` 확인.

## 언제 쓰나 (상황 예시)
- 배포 알림 봇: PR 머지 감지 → `#deploy` 알림.
- 이슈 트래킹: GitHub 이슈 생성·업데이트 시 담당자 DM.
- 일일 리포트: 커밋 현황 요약을 팀 채널에.
- 온콜 알림: 특정 키워드 감지 시 즉시 알림.

## 실습에서 배운 것 / 트러블슈팅
- 채널 목록 조회 ✅, 메시지 전송 ✅, 메시지 히스토리·멤버 조회 ✅, **메시지 검색 ❌**.
- **`not_in_channel` 에러**: Bot이 채널에 참여하지 않아서. 채널에서 `/invite @<봇이름>`으로 초대하면 해결.
- **Scope 이름 변경**: 예전 단일 `search:read`가 지금은 `search:read.im`, `search:read.mpim`, `search:read.public` 3개로 세분화. 옛 가이드대로 찾으면 목록에 없다.
- **검색 미동작**: search Scope를 넣어도 `@modelcontextprotocol/server-slack`이 검색을 구현하지 않아 쓸 수 없었다(패키지 한계).
- GitHub + Slack 알림 봇 콤보 → [[mcp-combo]].

## 관련
- [[mcp]]
- [[mcp-scope]] — `-s user`
- [[github-mcp]] — 알림 봇 콤보
- [[mcp-combo]]
- [[memory-mcp]] — 시리즈 이전 편
- [[nested-agent]] — 시리즈 다음 편
- [[hwp-mcp]]
- 원글: [Slack MCP](https://velog.io/@xorms/Slack-MCP)
