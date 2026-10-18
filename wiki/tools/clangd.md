---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/졸업작품-기록/2026-05-08-졸업작품-기록-26.md]
tags: [c++, ide, 언어서버, 임베디드]
---

## 한 줄 정의
C/C++ 코드 자동완성·경고를 주는 언어 서버다. `compile_commands.json`으로 컴파일 옵션을 읽는다.

## 핵심 내용
- 설정 파일은 `.clangd`, 컴파일 정보는 `compile_commands.json`(CompilationDatabase)이다.
- ESP32 크로스 컴파일 플래그 중 일부는 clangd가 인식하지 못해 `Unknown argument` 류 경고가 난다.

## 언제 쓰나 (상황 예시)
- [[platformio]] 펌웨어 프로젝트를 VS Code 등에서 편집할 때.

## 실습에서 배운 것 / 트러블슈팅
[[띵동]] 펌웨어에서 IntelliSense 경고 15건 정비 (2026-05-08):
1. `.clangd` 추가 (commit `70c0664`) → 15건 → 11건.
2. CompilationDatabase 경로 추가 (commit `d801e01`) → 효과 없음, 11건.
3. `compile_commands.json`을 `.gitignore`에 추가 (commit `db38da0`). 경고 대책이 아니라 로컬 환경 종속 파일이 레포에 올라가는 걸 막는 조치였다.
- 결론: ESP32 + clangd + ArduinoJson 7.x + Arduino-ESP32 core 3.x 조합은 clangd 인식 한계다. 컴파일로 동작 영향이 없음을 확인했으니 남은 11건은 무시했다. clangd 끄기나 ArduinoJson 다운그레이드는 더 큰 불편이었다.
- 교훈: 환경 정비 작업은 시작 전에 시간 박스와 "어디까지 되면 성공, 안 되면 언제 멈출지"를 정한다. IDE 설정·`.gitignore` 같은 코드 외 커밋도 같은 검증 절차를 거친다.

## 관련
- [[platformio]] · [[esp32-s3]] · [[띵동]]
- 원글: [졸업작품 기록 (26)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-26)
