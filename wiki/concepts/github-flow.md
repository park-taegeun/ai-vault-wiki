---
type: concept
modified: 2026-10-19
sources: [_private/raw/velog/졸업작품-기록/2026-05-16-졸업작품-기록-33.md, _private/raw/velog/졸업작품-기록/2026-06-15-졸업작품-기록35.md, _private/raw/velog/졸업작품-기록/2026-06-23-졸업작품-기록-37.md, _private/raw/velog/졸업작품-기록/2026-06-29-졸업작품-기록-38.md, _private/raw/notion/Backend/Session/Week01 - 기초 GitHub 다루기 2bdd8df03cab804e8d9cce940e8aa819.md, _private/raw/notion/Backend/Session/Week01 - 기초 GitHub 다루기/Conflict 과제 2bdd8df03cab8129aff8fc09a1b21726.md, _private/raw/notion/Backend/Session/Week01 - 기초 GitHub 다루기/해결 방법 2bdd8df03cab810e8f5bdd4d51799a3e.md, _private/raw/notion/Backend/세션 정리/1주차 - Git 2fbd8df03cab806ea339f402ec2904d1.md, _private/raw/notion/Backend/과제/1주차 - conflict 2fed8df03cab80299ff7fec548b383ca.md, _private/raw/notion/Backend/작업 시작 305d8df03cab80af8d97cd0531ace918.md]
tags: [git, 브랜치전략, pr, merge-conflict, commit-convention]
---

## 한 줄 정의
main에서 feature 브랜치를 따서 작업하고 PR → 리뷰 → 머지 → 브랜치 삭제로 돌아오는 단순한 브랜치 전략이다. [[띵동]]은 2026-05-18 PoC 1주차부터 squash 머지로 썼다.

## 핵심 내용
- 흐름: feat 브랜치 → 작업 → push → PR → 리뷰 → Squash 머지 → 브랜치 삭제.
- 띵동 코드 PR: #1 대시보드, #2 Flask(`37a92b3`), #3 React 연동(`cec9c9b`), #4 펌웨어(`c4c8f47`, 브랜치 `feat/firmware-fix-poc-boot`), #5 TypeScript strict(`56e44b8`), #6 접근성 B-1a.
- **웹 squash 머지 직후에는 반드시 로컬 main 동기화**: `git checkout main && git pull origin main`. 원래 "같은 로컬 머신에서는 매번 pull 안 해도 된다"는 규칙이 있었는데, 그 예외로 결정 문서와 프로젝트 지침에 넣었다.

### Git 기초 (멋쟁이사자처럼 13기 백엔드 1주차)
- **Git과 GitHub**: Git은 내 컴퓨터에서 돌아가는 버전 관리 엔진이고, GitHub는 Git으로 관리하는 프로젝트를 올려 두고 함께 쓰는 원격 저장소다.
- **4개 공간**: Working Directory(실제로 고치는 폴더) → `git add` → Staging Area(저장할 후보) → `git commit` → Local Repository → `git push` → Remote Repository(GitHub).
- **브랜치**: 특정 커밋을 가리키는 포인터다. 기존 코드에 영향을 주지 않고 기능을 따로 만들 수 있다.
- **명령어**: `git status`로 현재 상태부터 본다. `git push -u`의 `-u`는 이 브랜치를 앞으로 기본값으로 쓰겠다는 옵션이다. 되돌리기는 `git reset`은 로컬에서만 쓰고, 협업 중에는 되돌리는 커밋을 새로 만드는 `git revert`가 안전하다.

| | Git Flow | GitHub Flow |
|---|---|---|
| 브랜치 | main, develop, feature, release, hotfix | main 하나가 중심, 기능은 feature 브랜치 |
| 흐름 | 역할별 브랜치를 오가며 배포 | 기능이 끝나면 main으로 병합 |

| 머지 방식 | 특징 | 원본 노트의 평가 |
|---|---|---|
| Merge Commit | 히스토리를 다 남김 | 협업 흐름이 명확 |
| Squash Merge | 여러 커밋을 하나로 합침 | 히스토리가 깔끔 |
| Rebase Merge | 히스토리가 일직선 | 충돌 위험이 있어 혼자 쓰거나 숙련자용 |

- **커밋 컨벤션**: 접두어 예는 `Feat`(기능 추가), `Fix`(버그 수정), `Docs`(문서), `Refactor`(코드 개선), `Chore`.
- **머지 충돌**: 두 브랜치를 합칠 때 같은 파일의 같은 부분이 서로 다르게 바뀌었거나, 한 브랜치에서 지운 파일을 다른 브랜치에서 고쳤을 때 생긴다. 원본 노트에는 뒤쪽이 "다른 페이지에서 수정"으로 적혀 있었는데, 같은 문장의 대구에 따라 "다른 브랜치"로 고쳤다 (정정).

### 결정과 이유: 작업 시작 규칙 (본인 메모)
- **main에서 직접 작업하지 않는다.** 세션 과제가 가장 강조한 규칙이다. (이유 미기록)
- 주차별 작업 순서: 로컬 main이 GitHub와 같은지 확인하고 다르면 `git pull origin main` → 그 주차용 브랜치를 만들어 그 브랜치에서만 작업한다.
- 새 레포 시작 순서: `git init` → `git branch -m main` → `practice/`·`assignment/` 폴더와 README → 공통 `.gitignore`(`.DS_Store`, `.idea/`, `.gradle/`, `build/`) → 첫 커밋 → GitHub에서 레포를 먼저 만들고 `git remote add origin <URL>` → `git push -u origin main`.

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
- **충돌 재현 과제 (13기 백엔드 1주차)**: 개인 브랜치에서 Spring Boot 프로젝트(`com.likelion.conflicttest`)에 파일을 만들어 push → GitHub 웹에서 같은 파일을 고쳐 커밋 → 로컬 IntelliJ에서 같은 파일을 다르게 고쳐 커밋 → push.
  - 원격과 로컬이 달라 push가 거절되고 pull부터 하라는 오류가 난다.
  - `git pull`로 가져온 뒤 IntelliJ의 **Resolve Conflict**에서 남길 코드를 가운데(Result)로 옮기고 Apply한다. 세션 과제는 로컬 쪽 내용을 남기라고 했다.
  - 충돌을 해결한 결과를 **커밋한 다음** push해야 원격에 반영된다. → [[spring-boot]]
- **HTTPS push 인증 오류 (세션 안내)**: Personal Access Token(classic) 또는 SSH 키를 쓴다. 토큰은 만료일을 필요한 만큼만, 권한은 push·pull이면 `repo`만으로 충분하고, 발급 화면은 다시 뜨지 않으니 바로 보관한다. push할 때 비밀번호 자리에 토큰(`<REDACTED>`)을 넣는다.
  - `git config --global credential.helper store`를 쓰면 인증 정보가 `~/.git-credentials`에 저장돼 다시 묻지 않는다. 이 파일은 토큰을 그대로 담으므로 공유·커밋하지 않는다.

- **Squash PR 사이클 번호는 PR #2부터 센다**: 기록 35는 PR #3을 "두 번째 Squash PR 사이클"(첫 번째는 PR #2)이라 했고, 기록 37은 PR #4를 "코드 PR 3번째 사이클"이라 했다. 두 기록의 기준은 같다(PR #2 = 1, #3 = 2, #4 = 3). 기록 37이 괄호 안에 PR #1까지 함께 나열해서 어긋나 보일 뿐이다. PR #1을 세지 않는 이유는 (이유 미기록).

## 관련
- [[monorepo]] · [[single-source-of-truth]] · [[react]] · [[keras-savedmodel]] · [[github-mcp]] · [[띵동]]
- [[spring-boot]] — 충돌 재현 과제를 한 프로젝트
- 원글: [졸업작품 기록 (35)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D35)
- 원글: [졸업작품 기록 (37)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-37)
- 원글: [졸업작품 기록 (38)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-38)
