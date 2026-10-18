---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-08-02-Claude-Desktop에-Obsidian-볼트-연결.md]
tags: [mcp, obsidian, claude-desktop, 트러블슈팅]
---
## 한 줄 정의
Obsidian 커뮤니티 플러그인 "Local REST API"(coddingtonbear). v4.0부터 MCP 서버를 내장했고 v4.1.1에서 이름이 "Local REST API with MCP"로 바뀌었다. 별도 서버 설치 없이 볼트를 [[mcp]]로 Claude에 연결할 수 있다.

## 핵심 내용
- 연결 구조: 볼트(.md) ↔ Obsidian + 플러그인(MCP 서버) ↔ Node.js 브리지(`mcp-remote`) ↔ Claude Desktop ↔ 모델
- MCP 서버가 플러그인 안에서 돌기 때문에 **Obsidian이 꺼지면 연결도 끊긴다.**
- Claude Desktop은 HTTP 방식 MCP를 직접 지원하지 않는다. `mcp-remote`가 HTTP를 stdio로 바꿔주며 Node.js 위에서 실행된다.
- 기본은 HTTPS(자체 서명 인증서). 설정에서 HTTP 서버를 켜고 `http://127.0.0.1:27123/mcp/`를 쓰면 인증서 문제를 피할 수 있다.
- 글 작성 시점 기준 2,600+ 스타, 다운로드 630k. 처음 시도한 istefox "MCP Connector"(17k)보다 레퍼런스가 훨씬 많았다.

`claude_desktop_config.json` (기존 내용은 두고 `mcpServers`만 추가):
```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://127.0.0.1:27123/mcp/",
        "--header",
        "Authorization: Bearer <REDACTED>"
      ]
    }
  }
}
```
키 자리에는 플러그인 설정의 API Key를 넣는다. 수정 후 Claude Desktop을 완전히 재시작한다.

## 언제 쓰나 (상황 예시)
- Claude Desktop(GUI)에서 Obsidian 볼트를 읽고 쓰게 하고 싶을 때
- 볼트를 프로젝트 관리 레이어로 써서 Claude가 여러 프로젝트 상태를 가로질러 조회하게 할 때

## 실습에서 배운 것 / 트러블슈팅
| 증상 | 원인 | 해결 |
|---|---|---|
| "Could not attach to MCP server Obsidian MCP Connector" 반복 | istefox 플러그인과 현재 Claude Desktop 빌드의 호환성 문제로 판단. 로그상 연결은 성공했고 60초 뒤 유휴 타임아웃으로 끊김(`notifications/cancelled`) | Local REST API로 교체 |
| 도구 목록에 Obsidian 없음 | `.mcpb` 확장은 등록됐지만 세션에 노출 안 됨 | `.mcpb` 드래그 대신 config 파일을 직접 편집 |
| 호출이 10분씩 지연 | `mcp-remote@latest`가 호출마다 최신 버전 확인 | `@latest` 제거 |
| `{"files": []}` 빈 목록 | 볼트에 `.md` 파일이 하나도 없었음. 빈 폴더는 목록에 안 나옴 (버그 아님) | 테스트 파일 생성 후 정상 |

원인 배제에 쓴 점검: `lsof -i :27200`(포트 LISTEN), `curl -i http://127.0.0.1:27200/`(404 = 서버 살아 있음), `node --version`(v24.7.0), `which node`, Claude 로그 `mcp-server-....log`.

API 직접 확인:
```bash
curl -s -H "Authorization: Bearer <REDACTED>" http://127.0.0.1:27123/vault/
```

교훈
- 설치·서버·환경이 다 정상인데 연결만 실패하면 도구 궁합 문제일 수 있다. 한 도구에 매달리지 말고 검증된 대안으로 갈아탄다.
- 추측하지 말고 Claude를 거치지 않고 `curl`로 API를 직접 찔러 본다.
- Claude Code(CLI)와 Claude Desktop은 MCP 등록이 따로다 → [[mcp-scope]]

## 관련
- [[mcp]]
- [[llm-wiki]] — 볼트 폴더를 Claude Code가 직접 읽고 쓰는 다른 접근
- [[mcp-scope]]
- 원글: [Claude Desktop에 Obsidian 볼트 연결](https://velog.io/@xorms/Claude-Desktop%EC%97%90-Obsidian-%EB%B3%BC%ED%8A%B8-%EC%97%B0%EA%B2%B0)
