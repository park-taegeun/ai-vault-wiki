---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-10-11-Claude-Code로-Scrapling-MCP-연결하기-Cloudflare-봇-검사를-통과하는-스크래퍼를-AI에게-붙이는-법.md]
tags: [mcp, scraping, cloudflare, claude-code]
---
## 한 줄 정의
Scrapling은 웹 페이지를 가져오고(fetch) 필요한 부분만 뽑는(parse) 파이썬 오픈소스 스크래핑 라이브러리(BSD-3, GitHub 스타 8만+). MCP 서버가 내장돼 있어 Claude Code에 바로 붙일 수 있고, Cloudflare 봇 검사로 막힌 페이지도 수집한다. 실습 기준 v0.4.15.

## 핵심 내용
### Fetcher 3종 ↔ MCP 도구
| 파이썬 클래스 | MCP 도구 | 방식 | 언제 |
|---|---|---|---|
| Fetcher | `make_request` | HTTP 요청만 | 정적 페이지, 가장 빠름 |
| DynamicFetcher | `fetch` | 크로미움 실행 | JS로 그려지는 페이지 |
| StealthyFetcher | `stealthy_fetch` | 위장 브라우저 + 챌린지 풀이 | 봇 차단 사이트 |

원칙: 가벼운 것부터 쓰고, 막힐 때만 무거운 것으로 올라간다.

### 내부 의존성
- curl_cffi: 크롬 TLS 지문 흉내 → `make_request`
- playwright → `fetch`, patchright(자동화 흔적 제거판) → `stealthy_fetch`
- browserforge, apify-fingerprint-datapoints: 실제 사용자 통계 기반 브라우저 지문 생성
- markdownify(HTML→MD), protego(robots.txt), mcp(서버 SDK)

### 봇 검사 용어
- 브라우저 지문: 브라우저 버전, 헤더 순서, TLS 접속 방식, 화면 크기, 폰트 조합
- Turnstile: Cloudflare가 CAPTCHA 대신 쓰는 챌린지 (자동 통과형, interactive형 등)
- referer: 기본값이 구글 검색 유입(`https://www.google.com/`)처럼 설정됨

### 다른 웹 MCP와 비교
| 항목 | [[playwright-mcp]] | [[firecrawl-mcp]] | Scrapling MCP |
|---|---|---|---|
| 실행 위치 | 내 Mac(브라우저) | Firecrawl 클라우드 | 내 Mac(파이썬+브라우저) |
| 비용/인증 | 무료, 키 불필요 | API 키 + 크레딧 | 무료, 키 불필요 |
| 주 용도 | UI 조작(클릭, 로그인) | 대량 수집, map/crawl | 봇 차단 사이트, 정밀 추출 |
| 약점 | 봇 우회 목적 아님 | 외부 서버 경유, 크레딧 소모 | 파이썬 환경 세팅 필요 |

차별점: CSS 셀렉터로 **필요한 요소만 잘라 AI에 넘기므로 토큰을 덜 쓴다.** 광고·트래커 도메인 약 3,500개 자동 차단, 숨김 요소·HTML 주석·제로폭 문자를 이용한 프롬프트 인젝션 방어가 기본 적용된다.

## 언제 쓰나 (상황 예시)
- Cloudflare "Just a moment..." 화면(403)으로 막힌 공개 페이지 수집
- 페이지 전체가 아니라 특정 요소만 필요할 때 (예: `.quote .text`만 추출)
- 봇 차단이 없는 사이트는 `make_request`로 로컬 수집해 Firecrawl 크레딧 절약, Firecrawl로 막히는 공개 소스 보완(약관 확인 전제)

## 실습에서 배운 것 / 트러블슈팅
### 설치
- PyPI의 Requires-Python(>=3.10)은 pip 허용 최소 조건, Classifiers(3.10~3.13)는 실제 지원·테스트 버전. macOS 기본 python3는 3.9(미달), Homebrew 기본은 3.14(Classifiers 밖)라 3.11을 썼다.
```bash
python3.11 -m venv ~/.venvs/scrapling
source ~/.venvs/scrapling/bin/activate
pip install --upgrade pip
pip install "scrapling[ai]"   # [ai] = MCP 서버 포함 extras
scrapling install             # 브라우저 설치
```
- zsh에서 따옴표 없이 `scrapling[ai]`를 쓰면 대괄호를 파일 패턴으로 해석해 `no matches found` 에러.
- 브라우저는 `~/Library/Caches/ms-playwright`에 설치되어 [[playwright-mcp]]와 캐시를 공유한다.

### 등록 — 가상환경 실행 파일은 절대 경로로
```bash
claude mcp add scrapling --scope user -- "$(which scrapling-mcp)"
claude mcp list   # scrapling: ~/.venvs/scrapling/bin/scrapling-mcp - ✔ Connected
```
- Claude Code는 내가 venv를 켰는지 모르므로 절대 경로가 필요하다. `$(which ...)`는 입력 순간 절대 경로로 저장되므로 **venv를 켠 상태에서 등록**해야 한다. 이후엔 venv를 끈 터미널에서도 동작.
- 참고 가이드엔 `--scope user`가 빠져 local scope로 등록됐다 → [[mcp-scope]]
- `/mcp`의 User MCPs(`~/.claude.json`) 그룹에 도구 13개가 보이면 완료.

### Cloudflare 통과 비교 (`https://nopecha.com/demo/cloudflare`)
| 방법 | 상태 | 제목 | 시간 |
|---|---|---|---|
| curl | 403 | - | 즉시 |
| StealthyFetcher `solve_cloudflare=False` | 403 | 잠시만 기다리십시오… | 6.3초 |
| StealthyFetcher `solve_cloudflare=True` | 200 | NopeCHA - CAPTCHA Demo | 6.6초 |
- 지문 위장만으론 부족하고 챌린지를 풀어야 통과. Turnstile interactive가 약 3초 만에 해결됐고, 통과 후 307 리다이렉트로 `/demo`에서 200.
- 참고 가이드는 약 48초였는데 실측 6.6초. 원인은 단정 못 함(챌린지 종류·IP·네트워크 추정).
- `make_request` + `.quote .text`(quotes.toscrape.com)로 브라우저 없이 명언 10개만 추출. 두 요청 합쳐 24초.

### AI가 도구 결과를 오해한 사례
- `stealthy_fetch(solve_cloudflare=true)` 결과를 보고 Claude가 "챌린지가 나타나지 않았다"고 판단. AI는 **최종 결과(최종 URL /demo, 200, 본문)만** 받고, Turnstile 감지·해결·307 같은 중간 과정은 서버 로그에만 남기 때문.
- 해결: `solve_cloudflare=false`로 대조 실험(403, 리다이렉트 없음)을 시키자 Claude가 스스로 판단을 정정했다.
- 교훈: AI의 해석은 AI가 볼 수 있는 정보까지만 정확하다. 중요한 판단은 대조군을 두고 검증한다.

### 한계와 윤리
- 대응 범위는 Cloudflare Turnstile까지. Akamai, DataDome, Kasada 같은 기업용 방어는 대상 아님.
- 챌린지 해제를 켜면 느리다. 막히지 않는 사이트는 `make_request`.
- 기술적으로 가능한 것과 가져가도 되는 것은 별개. robots.txt, 이용약관, 개인정보, 서버 부하 확인. 실습은 테스트용 데모 페이지로만 진행.

## 관련
- [[mcp]]
- [[mcp-scope]]
- [[playwright-mcp]]
- [[firecrawl-mcp]]
- [[hwp-mcp]]
- 원글: [Claude Code로 Scrapling MCP 연결](https://velog.io/@xorms/Claude-Code%EB%A1%9C-Scrapling-MCP-%EC%97%B0%EA%B2%B0%ED%95%98%EA%B8%B0-Cloudflare-%EB%B4%87-%EA%B2%80%EC%82%AC%EB%A5%BC-%ED%86%B5%EA%B3%BC%ED%95%98%EB%8A%94-%EC%8A%A4%ED%81%AC%EB%9E%98%ED%8D%BC%EB%A5%BC-AI%EC%97%90%EA%B2%8C-%EB%B6%99%EC%9D%B4%EB%8A%94-%EB%B2%95)
