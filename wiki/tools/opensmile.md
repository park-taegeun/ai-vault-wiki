---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/AI_LAB/2026-06-16-LAB-31.md, _private/raw/velog/AI_LAB/2026-06-17-LAB-32.-임베딩openSMILE-편차-비중복-검증.md, _private/raw/velog/AI_LAB/2026-06-17-LAB-33.md, _private/raw/velog/AI_LAB/2026-07-08-LAB-50.md]
tags: [opensmile, acoustic-features, egemaps]
---

## 한 줄 정의
음성에서 피치, 음량, 발화속도, 음질 같은 음향 특징을 신호 처리로 **수치화**하는 도구다. 이 연구에서는 [[egemaps]] 88개 특징을 뽑는 데 썼다.

## 핵심 내용
- **고른 이유 (LAB 31)**
  - eGeMAPS는 감정·어조 분석용 표준 특징셋이다.
  - 신호 처리 기반이라 언어를 가리지 않는다. 한국어 지원을 걱정할 필요가 없다.
  - 감정 음성 연구에서 사실상 기본 비교 기준(baseline)으로 쓰인다.
- **[[gemma-4]]의 음성 서술과 비교 (LAB 31, 긴 발화 5개)**

| 특징 | 최소 | 최대 | Gemma 서술 |
|---|---|---|---|
| 평균 피치 (semitone) | 22.7 | 30.8 | 5개 모두 "중저음~중음" |
| 억양 변화폭 (semitone) | 5.14 | 8.16 | "약간 상승/하강", 방향만 언급 |
| 평균 음량 | 0.277 | 0.434 | 5개 모두 "중간" |
| 발화속도 (voiced seg/s) | 2.13 | 2.93 | 3개를 똑같이 "느리고 차분" |

  openSMILE 수치는 발화 유형에 따라 뚜렷하게 달랐다. Gemma는 다섯 발화를 같은 형용사로 묘사했다.
- **화자 기준 편차 os_dev (LAB 32)**
  - 88개 특징을 화자 안에서 z-score로 바꾼다. 그 값을 종합해서 "이 발화가 그 화자의 평소에서 몇 SD 벗어났나"를 숫자 하나로 만든다.
  - 세션 S000010의 os_dev 중앙값은 8.09였다. 이론 기준값 √88 ≈ 9.38에 가까워서 정규화가 제대로 됐다고 봤다.

## 언제 쓰나 (상황 예시)
- 같은 화자 안에서 상대적으로 얼마나 변했는지를 수치로 잡아야 할 때. 예: "이 발화는 평소보다 음량이 낮다"
- LLM이 음성을 서술한 결과를 정량적으로 검증할 때
- 길이가 제각각인 발화를 고전 ML에 넣을 고정 길이 벡터로 바꿀 때. 발화 하나가 88차원 벡터 하나가 된다.

## 실습에서 배운 것 / 트러블슈팅
- **os_dev는 발화 길이에 영향을 받는다**: S000010에서 발화 길이와의 상관이 −0.612였다. 짧은 발화일수록 편차가 크게 나오므로 편차를 비교할 때는 길이를 통제해야 한다. → [[embedding-probing]]
- **임베딩 편차와는 길이 통제 후 약하게만 겹쳤다**: 그래서 음향 수치를 임베딩과 별도의 입력으로 넣을 근거가 생겼다. → [[어조-모듈]]
- **감정 음성 데이터에 적용 (LAB 50)**
  - [[korean-emotion-speech-datasets]]의 균형 서브샘플 17,497개에서 88차원을 추출했다.
  - 처음에는 화자 1명으로 스모크 테스트를 하고, 그다음 여러 화자로 넓혔다. → [[speech-emotion-recognition]]

## 관련
- [[egemaps]] · [[gemma-4]] · [[embedding-probing]] · [[f0-pitch]] · [[mfcc]] · [[kconfspeech]] · [[speech-emotion-recognition]] · [[sarcasm-detection]] · [[어조-모듈]] · [[회의-음성-어조-분석-연구]]
- 원글: [LAB 31. Gemma4 음성특징 스모크 + openSMILE 비교](https://velog.io/@xorms/LAB-31)
- 원글: [LAB 32. 임베딩·openSMILE 편차 비중복 검증](https://velog.io/@xorms/LAB-32.-%EC%9E%84%EB%B2%A0%EB%94%A9openSMILE-%ED%8E%B8%EC%B0%A8-%EB%B9%84%EC%A4%91%EB%B3%B5-%EA%B2%80%EC%A6%9D)
- 원글: [LAB 50. 감정 음성 데이터셋 4모델 비교 - LOSO](https://velog.io/@xorms/LAB-50)
