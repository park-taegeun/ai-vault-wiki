---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-04-01-Firecrawl-MCP-콤보-실습.md]
tags: [mcp, firecrawl, crawling, rag]
---
## 한 줄 정의
웹 페이지를 LLM이 바로 읽기 좋은 정제된 마크다운으로 변환해주는 웹 데이터 API(Firecrawl)를 Claude Code에서 쓰게 해주는 MCP 서버.

## 핵심 내용
- HTML은 `<div>`, `<script>` 같은 태그가 내용과 섞여 노이즈가 많다. Firecrawl은 이를 마크다운으로 바꿔 AI가 바로 소비할 수 있게 한다.
- [[playwright-mcp]]와의 차이:
  | 항목 | Playwright MCP | Firecrawl MCP |
  |---|---|---|
  | 방식 | 실제 브라우저 실행 | API 기반 크롤링(자체 서버가 대신 수집) |
  | 강점 | 로그인·클릭 등 UI 조작 | 빠른 대량 수집, 마크다운 변환 |
  | 출력 | HTML, 스크린샷 | 정제된 마크다운 |
  | 주 용도 | UI 자동화, 동적 페이지 | 문서화, RAG 데이터 수집 |
  | 인증 | 불필요 | API 키 필요 |
- 무료 플랜: 가입 시 500크레딧. 단순 scrape 1회 = 1크레딧.
- 등록 (키는 환경변수로, user 스코프 → [[mcp-scope]]):
  ```bash
  echo 'export FIRECRAWL_API_KEY="<REDACTED>"' >> ~/.zshrc
  source ~/.zshrc
  claude mcp add firecrawl-mcp --scope user \
    -e FIRECRAWL_API_KEY=$FIRECRAWL_API_KEY \
    -- npx -y firecrawl-mcp
  ```
- 핵심 도구 3개:
  | 도구 | 하는 일 | 비용 |
  |---|---|---|
  | `firecrawl_scrape` | URL 하나를 마크다운으로 | 1크레딧 |
  | `firecrawl_crawl` | 사이트를 재귀 탐색 | 페이지 수만큼 |
  | `firecrawl_map` | URL 목록만 파악(내용 수집 X) | 1크레딧 |

## 언제 쓰나 (상황 예시)
- RAG 파이프라인: 공식 문서 사이트를 크롤링 → 마크다운 → 벡터DB.
- 콘텐츠 자동화: 뉴스 수집·요약 → 카드뉴스 초안.
- 경쟁사 모니터링: map으로 구조 파악 → 변경된 페이지만 crawl → Notion 기록.
- 라이브러리 문서 스냅샷: 날짜별로 GitHub에 아카이빙해 버전별 변경 이력 관리.

## 실습에서 배운 것 / 트러블슈팅
- scrape: `https://firecrawl.dev` 스크랩에 약 33초, 태그 없는 마크다운 반환.
- **crawl 다국어 함정**: 다국어 사이트는 `/ja/`, `/fr/`, `/es/` 경로까지 재귀 탐색해 원치 않는 언어 페이지가 섞인다. `includePaths`(예: `/docs/`)로 수집 경로를 제한해야 한다.
- map: `docs.firecrawl.dev`에서 URL 890개(영어 기준 326개) 구조를 1크레딧에 파악.
- **map → crawl 패턴**: 먼저 map(1크레딧)으로 전체 구조를 보고 필요한 섹션만 crawl. 890개 전체 대신 30개만 고르면 크레딧 90% 이상 절약.
- 콤보(AI 뉴스 모니터링)에서 Anthropic·OpenAI·HuggingFace 블로그 3곳에서 뉴스 44건 스크랩 → [[mcp-combo]].

## 관련
- [[mcp]]
- [[mcp-scope]]
- [[playwright-mcp]] — 웹 도구 비교
- [[mcp-combo]] — Firecrawl + GitHub + Notion + Sequential Thinking 뉴스 모니터링
- [[sequential-thinking-mcp]]
- [[memory-mcp]] — 시리즈 다음 편(수집한 정보가 휘발되는 한계를 해결)
- [[photocraft-mcp]]
- [[scrapling-mcp]]
- 원글: [Firecrawl MCP + 콤보 실습](https://velog.io/@xorms/Firecrawl-MCP-%EC%BD%A4%EB%B3%B4-%EC%8B%A4%EC%8A%B5)
