---
description: Obsidian 안에서 늘 보이는 프로젝트·취업 대시보드(.base) 만들기
---
obsidian-bases 스킬(kepano/obsidian-skills)의 `.base` 문법을 따라 `_private/대시보드.base`를 만들어. 이미 있으면 내용을 보여주고 고칠지 물어봐.

- 대상: 볼트 전체에서 프론트매터 `type`이 `project` 또는 `career`인 노트
- 열: 파일 이름, `status`, `priority`, `deadline`, `modified`, 폴더
- 뷰 (표 형식, 탭으로):
  1. **진행중** — `status`가 진행중, `deadline` 오름차순
  2. **마감 2주 이내** — `deadline`이 오늘부터 14일 이내이고 `status`가 완료가 아님
  3. **오래 안 건드림** — `status`가 진행중이고 `modified`가 14일 넘게 지남
  4. **보류·대기**

`.base`는 노트의 프론트매터를 Obsidian이 실시간으로 읽어 그리는 파일이라, 한 번 만들면 다시 갱신할 필요가 없어. 만든 뒤 Obsidian에서 `_private/대시보드.base`를 열어 보라고 안내해. obsidian-bases 스킬이 설치돼 있지 않으면 만들지 말고 설치 방법만 알려줘.
