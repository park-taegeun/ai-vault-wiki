---
type: concept
modified: 2026-10-23
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-03-27-Context7-GitHub-MCP-콤보.md, _private/raw/velog/AI-생태계-탐험-로그/2026-10-14-Claude-Code에-claude-mem-붙여보기.md, _private/raw/velog/AI-생태계-탐험-로그/2026-03-30-Playwright-MCP-Server.md, _private/raw/velog/AI-생태계-탐험-로그/2026-10-11-Claude-Code로-Scrapling-MCP-연결하기-Cloudflare-봇-검사를-통과하는-스크래퍼를-AI에게-붙이는-법.md, _private/raw/velog/AI-생태계-탐험-로그/2026-10-12-Claude-Code로-hwp-mcp-연결하기.md, _private/raw/velog/AI-생태계-탐험-로그/2026-08-02-Claude-Desktop에-Obsidian-볼트-연결.md, _private/raw/velog/AI-생태계-탐험-로그/2026-10-11-Claude-Code에-Ruflo-붙여보기.md]
tags: [mcp, claude-code, 설정]
---
# MCP scope

## 한 줄 정의
`claude mcp add`로 MCP를 등록할 때 정하는 적용 범위 (local / user / project).

## 핵심 내용
| scope | 적용 범위 | 옵션 |
|---|---|---|
| local | 현재 프로젝트만 | 기본값 (옵션 없음) |
| user | 내 계정 전체 (모든 프로젝트) | `--scope user` |
| project | 팀 공유 (`.mcp.json`) | `--scope project` |

user scope 등록 여부는 `~/.claude.json`의 최상위 `mcpServers` 키로 확인한다. `{}`이면 user scope MCP가 없다.
```bash
cat ~/.claude.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
print('글로벌 mcpServers:', json.dumps(d.get('mcpServers', {}), indent=2))
"
```

### Claude Code의 scope
- `claude mcp add`에 `--scope`를 빼면 **현재 폴더에서만 쓰이는 local scope**로 등록된다. 모든 프로젝트에서 쓰려면 `--scope user`. ([[scrapling-mcp]] 실습에서 참고 가이드에 빠져 있던 부분)
- user scope로 등록한 서버는 `/mcp` 화면의 **User MCPs(`~/.claude.json`)** 그룹에 보인다.
- 예: `claude mcp add hwp-mcp --scope user -- npx -y hwp-mcp@latest` ([[hwp-mcp]])
- 프로젝트 단위 서버는 `.mcp.json`에 들어간다. [[ruflo]]는 init 시 `.mcp.json`에 `claude-flow`라는 이름으로 서버를 넣으므로, 수동으로 `ruflo`를 또 등록하면 중복된다.
- 등록 후에는 세션을 새로 시작해야 도구가 로드된다.

### 클라이언트마다 등록이 따로
- Claude Code(CLI)와 Claude Desktop(GUI)은 MCP 등록이 별도다. claude.ai 웹에서는 로컬 MCP가 동작하지 않는다. ([[hwp-mcp]])
- Claude Desktop은 `claude_desktop_config.json`의 `mcpServers`에 등록하고, 수정 후 앱을 완전히 재시작한다. HTTP 방식 MCP는 직접 지원하지 않아 `mcp-remote` 브리지가 필요하다. ([[obsidian-local-rest-api]])

### 같은 원리 — 저장 위치가 곧 적용 범위 (훅)
Claude Code 훅도 저장 위치가 적용 범위를 정한다. ([[ruflo]])
| 위치 | 범위 |
|---|---|
| `~/.claude/settings.json` | 전체 |
| `.claude/settings.json` | 프로젝트 공유 |
| `.claude/settings.local.json` | 나만 |
| 플러그인 `hooks.json` | 플러그인 |
현재 적용된 훅은 `/hooks`로 확인한다. 전역 파일(`~/.claude/CLAUDE.md`, `~/.claude/settings.json`)을 건드리는 도구는 설치 옵션(예: Ruflo `--no-global`)으로 막는다.

## 언제 쓰나 (상황 예시)
- 어느 프로젝트에서나 쓰는 범용 MCP([[context7-mcp]], [[github-mcp]]) → `--scope user`
- 특정 DB 접속 정보, 팀 전용 Slack 연동처럼 프로젝트에 묶인 것 → `local`

## 실습에서 배운 것 / 트러블슈팅
- **"있는데 없는 것처럼"**: 이전 프로젝트 디렉터리에서 등록한 MCP가 새 디렉터리의 `claude mcp list`에 안 떴다. 기본값 local로 등록했기 때문이다. `claude mcp remove` 후 `--scope user`로 재등록해 해결.
  ```bash
  claude mcp remove context7
  claude mcp remove github
  claude mcp add context7 --scope user -- npx -y @upstash/context7-mcp@latest
  claude mcp add github --scope user -e GITHUB_PERSONAL_ACCESS_TOKEN=<REDACTED> -- npx -y @modelcontextprotocol/server-github
  ```
- **user scope가 다른 레포에 끼어든 사례**: 띵동용으로 만든 [[decisions-rag]] MCP를 user scope로 등록해 두었더니, 상관없는 ai-news-monitor 세션에도 그 안내문이 들어왔다. 그래서 Claude가 엉뚱한 레포 파일을 근거 후보로 언급했다. 특정 프로젝트에 묶인 MCP는 local로 등록해야 한다. ([[claude-mem]] 실험 중 발견)
- user scope로 등록한 것은 `claude mcp remove <이름> --scope user`처럼 scope를 맞춰 지운다 ([[playwright-mcp]] 재등록 때 사용).

- venv 안의 실행 파일은 절대 경로로 등록한다. `"$(which scrapling-mcp)"`는 입력 순간 경로가 고정되므로 venv를 켠 상태에서 등록해야 한다. ([[scrapling-mcp]])

## 관련
- [[mcp]]
- [[claude-code-hook]] — 훅도 저장 위치가 곧 적용 범위
- [[mcp-combo]]
- [[context7-mcp]] · [[github-mcp]] · [[notion-mcp]] · [[playwright-mcp]]
- [[scrapling-mcp]]
- [[hwp-mcp]]
- [[obsidian-local-rest-api]]
- [[ruflo]]
- [[claude-code-setup]]
- [[claude-mem]]
- [[decisions-rag]] — user scope로 등록해 상관없는 세션에 끼어든 MCP
- [[firecrawl-mcp]]
- [[photocraft-mcp]]
- [[slack-mcp]]
- [[supabase-mcp]]
- 원글: [Context7 + GitHub MCP 콤보](https://velog.io/@xorms/Context7-GitHub-MCP-%EC%BD%A4%EB%B3%B4)
- 원글: [Playwright MCP Server](https://velog.io/@xorms/Playwright-MCP-Server)
- 원글: [Claude Code로 Scrapling MCP 연결](https://velog.io/@xorms/Claude-Code%EB%A1%9C-Scrapling-MCP-%EC%97%B0%EA%B2%B0%ED%95%98%EA%B8%B0-Cloudflare-%EB%B4%87-%EA%B2%80%EC%82%AC%EB%A5%BC-%ED%86%B5%EA%B3%BC%ED%95%98%EB%8A%94-%EC%8A%A4%ED%81%AC%EB%9E%98%ED%8D%BC%EB%A5%BC-AI%EC%97%90%EA%B2%8C-%EB%B6%99%EC%9D%B4%EB%8A%94-%EB%B2%95)
- [[ai-vault]] — 볼트 폴더를 옮기자 project scope 스킬이 옛 경로에 묶여 사라진 사례
- 원글: [Claude Code로 hwp-mcp 연결하기](https://velog.io/@xorms/Claude-Code%EB%A1%9C-hwp-mcp-%EC%97%B0%EA%B2%B0%ED%95%98%EA%B8%B0)
- 원글: [Claude Desktop에 Obsidian 볼트 연결](https://velog.io/@xorms/Claude-Desktop%EC%97%90-Obsidian-%EB%B3%BC%ED%8A%B8-%EC%97%B0%EA%B2%B0)
- 원글: [Claude Code에 Ruflo 붙여보기](https://velog.io/@xorms/Claude-Code%EC%97%90-Ruflo-%EB%B6%99%EC%97%AC%EB%B3%B4%EA%B8%B0)
