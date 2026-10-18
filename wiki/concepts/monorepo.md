---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/졸업작품-기록/2026-05-07-졸업작품-기록-23.md]
tags: [레포구조, git, 프로젝트관리]
---

## 한 줄 정의
여러 구성 요소(펌웨어·서버·대시보드·ML)를 레포 하나에 폴더로 나눠 함께 관리하는 방식이다.

## 핵심 내용
[[띵동]] 레포 구조 (2026-05-07):
```
ddingdong/
├── firmware/      ← 지금 작업
├── server/        ← 11주차 진입 시
├── dashboard/     ← 15주차 진입 시
├── ml/            ← 8주차 진입 시
├── docs/
│   ├── decisions.md        ← SSoT
│   ├── decisions-log.md
│   └── git-convention.md   ← 한국어 + 이모지 14종
└── README.md
```
- 당장 쓰는 건 `firmware/`뿐이었다. 그래도 나중에 합류할 트랙 자리를 미리 잡아 두는 게 나중에 구조를 바꾸는 것보다 낫다고 판단했다.
- 커밋 메시지는 한국어 + 이모지 규칙이다(예: `🔧 Settings: ...`).

## 언제 쓰나 (상황 예시)
- 한 사람(또는 작은 팀)이 여러 도메인을 함께 굴리고, 결정 기록을 코드와 같은 곳에 두고 싶을 때 → [[single-source-of-truth]]

## 실습에서 배운 것 / 트러블슈팅
- 펌웨어 빌드 설정은 `firmware/` 안의 [[platformio]] 프로젝트로 둔다. 모듈별 env는 whitelist로 격리해야 다른 모듈 파일이 빨려 들어오지 않는다.
- 브랜치 운용은 [[github-flow]] 참고.

## 관련
- [[띵동]] · [[single-source-of-truth]] · [[platformio]] · [[github-flow]]
- 원글: [졸업작품 기록 (23)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-23)
