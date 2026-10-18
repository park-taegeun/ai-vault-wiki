---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI-생태계-탐험-로그/2026-10-14-AI가-만든-포토샵을-AI가-조작한다.md]
tags: [mcp, photocraft, 이미지편집, 카드뉴스, 자동화]
---
# photocraft-mcp

## 한 줄 정의
Photoshop을 클린룸 방식으로 다시 만든 오픈소스 이미지 편집기 PhotoCraft를 MCP로 조종하는 도구. 명령 500개 이상을 MCP 도구 25개로 부른다.

## 핵심 내용
- **배경**: ArtCraft 창업자 Brandon Thomas가 Claude Opus 5.5로 만든 Adobe 클론 앱 7개 중 하나. 순수 Rust, 첫 커밋 2026-09-30, MIT/Apache-2.0. 실습 버전 v0.8.2 (early alpha).
- **클린룸 구현**: 원본 코드·에셋 없이 공개 스펙과 겉으로 보이는 동작만 보고 새로 만듦. 그래서 포토샵의 "변수·데이터 세트" 같은 기능이 그대로 있다.
- **명령 레지스트리**: 기능 500개 이상이 하나의 명령 레지스트리에 있고 UI·CLI·MCP가 같은 명령을 호출한다. MCP 도구는 25개뿐(`command_list`로 찾고 `command_run`으로 실행, 예: `type.create`). 기능마다 도구를 만드는 방식보다 도구 설명이 작아 컨텍스트 토큰이 적게 든다.
- **조종 방식 2가지**: 헤드리스(화면 없이 엔진만, 자동화용) / 브리지(켜진 앱을 원격 조종, 같이 보며 편집용). `ui_*` 도구는 브리지 모드 전용.
- **폴더 출입증**: `--automation-read-root`, `--automation-write-root`로 지정한 폴더 안에서만 파일을 읽고 쓴다. 지정하지 않으면 파일을 전혀 못 다룬다.
- **파일 형식**: `.pcraft`는 레이어가 살아 있는 원본(.psd 대응), `.png`는 합쳐진 결과물. 템플릿은 .pcraft, 결과물만 PNG.
- **데이터 세트**: 변수 = 레이어 이름표, CSV 헤더 = 이름표 이름, CSV 한 줄 = 이미지 한 장. 같은 디자인에 내용만 다른 이미지를 한 번에 찍어낸다.

### 설치·등록 (macOS)
```bash
shasum -a 256 ~/Downloads/photocraft-cli-0.8.2-macos-universal.zip   # 릴리스 페이지 값과 비교
mkdir -p ~/tools/photocraft
ditto -x -k ~/Downloads/photocraft-cli-0.8.2-macos-universal.zip ~/tools/
mv ~/tools/photocraft-cli-0.8.2-macos-universal/photocraft-cli ~/tools/photocraft/
spctl --assess --type install -vv ~/tools/photocraft/photocraft-cli   # accepted, Notarized Developer ID

mkdir -p ~/cardnews
claude mcp add photocraft --scope user -- \
  ~/tools/photocraft/photocraft-cli mcp \
  --automation-read-root ~/cardnews \
  --automation-write-root ~/cardnews
```
- 알파 실행 파일이라 sha256 해시와 Apple 공증을 먼저 확인했다.
- 실행 파일을 버전 번호 없는 고정 경로에 두면 새 버전으로 바꿔도 MCP를 다시 등록하지 않아도 된다.
- 필요한 명령이 있는지 `photocraft-cli commands | grep -i -E "type|text"`로 미리 확인 (`type.create`, `type.edit`, `edit.findAndReplaceText`, `image.variables.define`, `file.export.dataSetsAsFiles`).

## 언제 쓰나 (상황 예시)
- AI 뉴스 인스타그램 카드뉴스 자동 생성 ([[firecrawl-mcp]]로 수집 → CSV → 데이터 세트로 표지 1장 + 뉴스 5장)
- 블로그 썸네일·시리즈 표지를 제목만 바꿔 통일감 있게 생성
- 이벤트 카드, 명찰, 인증서처럼 디자인은 같고 내용만 다른 대량 이미지

## 실습에서 배운 것 / 트러블슈팅
- **한국어 줄바꿈**: PhotoCraft는 한글을 글자 단위로 줄바꿈해서 단어 중간이 잘린다(어절 단위 옵션 없음). 글자 수 제한 규칙만으로는 안 막혔고, 글자 레이어를 **포인트 텍스트**(자동 줄바꿈 없음)로 바꾸고 CSV에 줄바꿈을 직접 넣어 해결. Pretendard Bold 한글 1자 폭을 0.864em으로 실측해 변수별 "최대 줄 수 / 한 줄 최대 글자 수" 규칙 파일을 만들었다.
- **레이어 위치 고정**: 데이터 세트는 레이어 위치가 고정이라 "제목 2줄 고정" 같은 카피 규칙으로 맞췄다.
- **역할 분담**: Claude는 규칙을 지키며 카피 쓰기, PhotoCraft는 받은 글자를 그대로 찍어내기.
- **왕복 검증**: 템플릿 저장 후 다시 열어 자리표시자(`{{제목}}` 등)가 살아 있는지 확인 ([[hwp-mcp]]에서 얻은 "저장 완료를 믿지 말고 다시 읽어라" 교훈).
- **디자인 개선 루프**: 위계·썸네일 가독성·여백·대비·타이포·색·시리즈 일관성·정보 밀도 8개 기준(각 10점, 80점 만점)을 주고, 제작 과정을 모르는 서브에이전트에게 PNG만 줘서 블라인드 채점([[nested-agent]] 활용). 검토자는 360px 축소본을 만들고 픽셀 색으로 WCAG 대비비를 계산했다. 점수는 49/46/50 → 52 → 56으로 올랐지만 시간은 약 7분 → 약 17분으로 늘어 수확 체감. 검토자가 바뀌면 1~2점은 흔들려서 점수보다 지적 내용이 더 쓸모 있었다.
- **레퍼런스**: 웹 검색·[[firecrawl-mcp]]로 트렌드 글을 모으고 [[playwright-mcp]]로 스크린샷을 찍어 공통 패턴을 뽑았다. 인스타그램(로그인 필요)·Behance(차단)는 AI가 못 봐서, 사람의 역할은 취향 선택·레퍼런스 제공·최종 팩트체크로 정리.
- **팩트 안전장치**: "핵심 수치" 같은 highlight 변수를 일부러 빼서 숫자를 지어낼 여지를 없앰. 카드별 근거 문장·링크를 `facts.md`에 기록. 검증에서 걸린 카드는 Claude가 스스로 고쳐 다시 내보냄(4번 카드 1회 수정).

| 문제 | 해결 |
|---|---|
| 폴더 출입증 미지정 시 파일 접근 불가 | read/write root 지정, 배경 이미지 같은 소재도 그 폴더로 복사 |
| `type.fonts`로 한글 지원 여부를 알 수 없음 | `fc-list :lang=ko`와 교차 확인, PNG를 직접 열어 □ 깨짐 확인 |
| PNG 저장 시 "layer(s) flattened" 경고 | 템플릿은 .pcraft, 결과물만 PNG |
| 큰 페이지 번호가 탁한 회색으로 보임 | Normal 9% → Overlay 블렌드 |
| 변수 이름 인코딩 문제 우려 | 변수 이름은 영어(`title`, `body`, `source`) |
| Claude Code가 영어로 답변 | `~/.claude/CLAUDE.md`에 "항상 한국어로 답변할 것" 추가 |
| v3 템플릿 약 4.7MB (v2 약 0.2MB) | 빛 번짐·그레인이 픽셀 레이어라서 생긴 차이, 감안하고 사용 |

## 관련
- [[mcp]]
- [[mcp-scope]] — `--scope user`로 등록
- [[mcp-combo]] — Firecrawl 수집 + PhotoCraft 생성 콤보
- [[firecrawl-mcp]]
- [[playwright-mcp]]
- [[hwp-mcp]] — 바로 전 실습(문서 → 이미지로 이어짐)
- [[nested-agent]] — 블라인드 검토자
- [[claude-code-setup]] — 다음 편
- 원글: [AI가 만든 포토샵을 AI가 조작한다](https://velog.io/@xorms/AI%EA%B0%80-%EB%A7%8C%EB%93%A0-%ED%8F%AC%ED%86%A0%EC%83%B5%EC%9D%84-AI%EA%B0%80-%EC%A1%B0%EC%9E%91%ED%95%9C%EB%8B%A4)
