---
type: concept
modified: 2026-10-19
sources: [_private/raw/velog/졸업작품-기록/2026-05-16-졸업작품-기록-33.md, _private/raw/velog/졸업작품-기록/2026-06-15-졸업작품-기록35.md, _private/raw/velog/졸업작품-기록/2026-06-23-졸업작품-기록-37.md, _private/raw/velog/졸업작품-기록/2026-06-29-졸업작품-기록-38.md]
tags: [git, 브랜치전략, pr]
---

## 한 줄 정의
main에서 feature 브랜치를 따서 작업하고 PR → 리뷰 → 머지 → 브랜치 삭제로 돌아오는 단순한 브랜치 전략이다. [[띵동]]은 2026-05-18 PoC 1주차부터 squash 머지로 썼다.

## 핵심 내용
- 흐름: feat 브랜치 → 작업 → push → PR → 리뷰 → Squash 머지 → 브랜치 삭제.
- 띵동 코드 PR: #1 대시보드, #2 Flask(`37a92b3`), #3 React 연동(`cec9c9b`), #4 펌웨어(`c4c8f47`, 브랜치 `feat/firmware-fix-poc-boot`), #5 TypeScript strict(`56e44b8`), #6 접근성 B-1a.
- **웹 squash 머지 직후에는 반드시 로컬 main 동기화**: `git checkout main && git pull origin main`. 원래 "같은 로컬 머신에서는 매번 pull 안 해도 된다"는 규칙이 있었는데, 그 예외로 결정 문서와 프로젝트 지침에 넣었다.

## 언제 쓰나 (상황 예시)
- GitHub 웹에서 PR을 squash 머지한 뒤 다음 feature 브랜치를 따기 직전.

## 실습에서 배운 것 / 트러블슈팅
- **PR #6 히스토리 꼬임 (기록 38)**: PR #6을 웹에서 squash 머지한 뒤 PR 화면에 "This pull request merged 2 commits into main"이 떴다. `git log`로 확인하니 이랬다.
  1. PR #5를 웹에서 squash 머지 → remote main에 새 커밋 `56e44b8`
  2. 로컬 main은 그 전 상태 그대로
  3. 그 위에서 B-1a 브랜치를 따서, squash로 사라진 PR #5 원본 커밋이 PR #6에 딸려 들어가고 merge commit까지 생김
- 복구: `git checkout main` → `git pull origin main` → `Updating e9b9879..3408d97 Fast-forward`. fast-forward라 히스토리 rewrite는 0건이었다.
- squash 머지는 remote에 새 해시를 만든다. "로컬 = remote"라는 가정은 웹 머지라는 이벤트로 깨진다 → [[single-source-of-truth]]
- PR 브랜치에만 있는 파일을 로컬 main에서 실행하면 `No module named ...`가 난다. 머지 후 pull해야 생긴다 → [[keras-savedmodel]]

- **Squash PR 사이클 번호는 PR #2부터 센다**: 기록 35는 PR #3을 "두 번째 Squash PR 사이클"(첫 번째는 PR #2)이라 했고, 기록 37은 PR #4를 "코드 PR 3번째 사이클"이라 했다. 두 기록의 기준은 같다(PR #2 = 1, #3 = 2, #4 = 3). 기록 37이 괄호 안에 PR #1까지 함께 나열해서 어긋나 보일 뿐이다. PR #1을 세지 않는 이유는 (이유 미기록).

## 관련
- [[monorepo]] · [[single-source-of-truth]] · [[react]] · [[keras-savedmodel]] · [[github-mcp]] · [[띵동]]
- 원글: [졸업작품 기록 (35)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D35)
- 원글: [졸업작품 기록 (37)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-37)
- 원글: [졸업작품 기록 (38)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-38)
