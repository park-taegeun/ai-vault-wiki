---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-03-27-GitHub-MCP.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-27-Context7-GitHub-MCP-콤보.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-30-Playwright-GitHub-Notion-3-MCP-콤보-실습.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-31-Sequential-Thinking-GitHub-Notion-3-MCP-콤보.md, _private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Firecrawl-MCP-콤보-실습.md, _private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Memory-Playwright-Notion-GitHub-4-MCP-콤보.md, _private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Slack-MCP.md]
tags: [mcp, claude-code, github]
---
# GitHub MCP

## 한 줄 정의
Claude Code가 GitHub API를 직접 호출하게 해 주는 MCP 서버. 레포·이슈·브랜치·PR·머지를 자연어로 처리한다.

## 핵심 내용
- 패키지 `@modelcontextprotocol/server-github`, stdio 방식, 인증은 PAT(Personal Access Token).
- **Git(로컬)과 GitHub MCP(API)의 역할 구분**

| 작업 | Git Bash (로컬) | GitHub MCP (API) |
|---|---|---|
| add, commit, push | O | X |
| 이슈 생성/조회 | X | O |
| PR 생성/머지 | X | O |
| 레포 생성 | X | O |
| 브랜치 조회/생성 | 로컬만 | 원격 브랜치 |

  예외로 `create_or_update_file`은 로컬 push 없이 API로 원격 브랜치에 파일을 바로 커밋한다.
- 실습에서 쓴 도구: `create_repository`, `create_issue`, `create_branch`, `create_pull_request`, `merge_pull_request`, `create_or_update_file`, `add_issue_comment`.
- 워크플로우: 이슈 생성 → 브랜치 → 코드 → PR → 머지 → 이슈 닫기. 혼자 하는 프로젝트라도 이슈와 PR이 남으면 "어떻게 생각하며 개발했는지"가 포트폴리오에 드러난다.

PAT 발급 (classic): https://github.com/settings/tokens → Generate new token (classic) → 권한 `repo`(전체), `read:org`, `read:user`, `gist` → 만료 90일 → 토큰 복사 (페이지를 벗어나면 다시 볼 수 없음).

등록:
```bash
claude mcp add github --scope user \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=<REDACTED> \
  -- npx -y @modelcontextprotocol/server-github
claude mcp get github   # Status: ✓ Connected
```
(처음에는 scope 없이 local로 등록했다가 user로 옮겼다 → [[mcp-scope]])

## 언제 쓰나 (상황 예시)
- 터미널 명령 없이 레포 생성 → 이슈 → 브랜치 → PR → 머지를 자연어로.
- [[context7-mcp]]와 묶어 문서 참조 → 코드 → PR을 한 줄로, PR 리뷰 코멘트 자동 등록, 커밋 조회 후 hotfix PR → [[mcp-combo]].
- [[playwright-mcp]]로 긁은 결과를 레포에 백업 (velog-backup).

## 실습에서 배운 것 / 트러블슈팅
- **토큰 중복 입력**: 명령에 `ghp_`를 직접 치고 토큰을 붙여넣으면 `ghp_ghp_...`로 저장돼 인증이 실패한다. `claude mcp remove github` 후 붙여넣기만으로 다시 등록.
- **홈 디렉터리에서 실행하면 Bash로 우회**: `~`에서 `claude`를 실행하면 MCP 대신 git 설정 명령이나 `gh api` 같은 Bash로 처리하려 한다. 프로젝트 디렉터리를 만들고 그 안에서 실행한다. `(MCP)` 표시가 없으면 실행 경로와 등록 상태부터 확인.
- **에이전트적 복구**: "Git Repository is empty" → README.md를 스스로 커밋한 뒤 브랜치 생성 재시도. "No commits between branches" → test.md를 추가한 뒤 PR 재시도.
- **`auto_init: true` 미적용**: `create_repository`에 지정해도 빈 저장소로 생길 때가 있다. 클론할 때 빈 저장소 경고가 뜨면 README.md 생성을 따로 요청해 첫 커밋을 만든다.
- 콤보 실습에서는 지시하지 않은 `add_issue_comment`로 "참조한 문서"를 PR 코멘트에 남겼다.
- 토큰은 채팅·스크린샷에 노출하지 않는다. 노출되면 즉시 무효화하고 재발급.

- **설계 히스토리를 이슈에 남기기**: JWT 인증 콤보에서 Sequential Thinking 6단계 설계 전체를 이슈 #1에 기록. 코드만 있는 레포가 아니라 "왜 이렇게 설계했는지"가 남는다.
- **커밋 분리**: `chore: initialize repository`(README) → `feat: add JWT auth module`(8파일 일괄)처럼 초기화와 기능 커밋을 나눴다.
- **날짜별 아카이빙**: 뉴스 모니터링 콤보에서 새 레포를 만들고 `posts/2026-04-01.md` 같은 날짜 파일로 커밋.
- **읽기 → 다른 MCP로 전달**: 최근 커밋 3개 조회·이슈 생성 결과를 Slack으로 보내는 알림 봇의 데이터 소스 역할.

## 관련
- [[ai-산출물-검증]] · [[single-source-of-truth]] · [[github-flow]] — 졸업작품 [[띵동]]에서 실제 동작 코드 검색, 결정 문서 commit에 쓴 사례
- [[mcp]]
- [[mcp-scope]]
- [[mcp-combo]]
- [[context7-mcp]] · [[notion-mcp]] · [[playwright-mcp]]
- [[sequential-thinking-mcp]]
- [[slack-mcp]]
- [[claude-mem]] — `ai-news-monitor` 레포를 실습 레포로 재사용
- 원글: [GitHub MCP](https://velog.io/@xorms/GitHub-MCP)
- 원글: [Context7 + GitHub MCP 콤보](https://velog.io/@xorms/Context7-GitHub-MCP-%EC%BD%A4%EB%B3%B4)
- 원글: [Playwright + GitHub + Notion 3 MCP 콤보](https://velog.io/@xorms/Playwright-GitHub-Notion-3-MCP-%EC%BD%A4%EB%B3%B4-%EC%8B%A4%EC%8A%B5)
- 원글: [Sequential Thinking + GitHub + Notion 3 MCP 콤보](https://velog.io/@xorms/Sequential-Thinking-GitHub-Notion-3-MCP-%EC%BD%A4%EB%B3%B4)
- 원글: [Firecrawl MCP + 콤보 실습](https://velog.io/@xorms/Firecrawl-MCP-%EC%BD%A4%EB%B3%B4-%EC%8B%A4%EC%8A%B5)
- 원글: [Memory + Playwright + Notion + GitHub 4 MCP 콤보](https://velog.io/@xorms/Memory-Playwright-Notion-GitHub-4-MCP-%EC%BD%A4%EB%B3%B4)
- 원글: [Slack MCP](https://velog.io/@xorms/Slack-MCP)
