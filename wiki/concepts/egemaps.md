---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/AI_LAB/2026-06-16-LAB-31.md, _private/raw/velog/AI_LAB/2026-06-17-LAB-32.-임베딩openSMILE-편차-비중복-검증.md, _private/raw/velog/AI_LAB/2026-06-17-LAB-33.md, _private/raw/velog/AI_LAB/2026-07-07-LAB-49.-eGeMAPS-88차원-왜-이-4개-모델로-비교하는가.md, _private/raw/velog/AI_LAB/2026-07-08-LAB-50.md]
tags: [egemaps, opensmile, acoustic-features, hand-crafted]
---

## 한 줄 정의
eGeMAPS(extended Geneva Minimalistic Acoustic Parameter Set)는 음성 감정·어조 연구에서 표준으로 쓰는 사람이 설계한 특징 세트다. 발화 하나를 **88차원 고정 벡터**로 요약하며, [[opensmile]]로 추출한다.

## 핵심 내용
- **1단계: 프레임별 원시 특징(LLD)을 뽑는다.**
  - 10ms마다 F0, 에너지, jitter, shimmer, HNR, 포먼트, [[mfcc]] 같은 값을 잰다.
  - 결과는 발화 길이에 따라 길이가 달라지는 시계열이다.
- **2단계: 시계열을 발화 단위 통계(functionals)로 압축한다.**
  - 평균, 표준편차, 백분위, 기울기 같은 통계를 쓴다.
  - 예를 들어 F0 평균은 전체 톤의 높이를, F0 표준편차는 억양의 출렁임을, 에너지 기울기는 말소리가 점점 세지는지 죽는지를 나타낸다.
- **길이와 상관없이 88개 숫자가 나온다.** 그래서 고정 길이 입력을 받는 고전 ML(SVM, XGBoost)과 잘 맞는다. 원논문(Eyben 2016)도 Linear SVM을 썼다.
- **화자 기준 종합 편차를 만들 수 있다.** 88개를 화자 안에서 z-score로 바꿔 합치면 "평소에서 얼마나 벗어났나"를 나타내는 종합 지표가 된다. 기준값은 √88 ≈ 9.38이다.

## 언제 쓰나 (상황 예시)
- [[speech-emotion-recognition]]에서 해석 가능성이 중요할 때. 어조가 음향의 어느 차원에 담기는지 밝히려는 경우다.
- 표준 잣대로 자기 데이터 결과를 비교하고 싶을 때
- 모델 내부 표현이 음향적으로 무엇에 반응하는지 사람이 아는 말로 풀어볼 때

## 실습에서 배운 것 / 트러블슈팅
- **임베딩 편차를 88개 특징으로 분해 (LAB 33)**
  - audio_tower 임베딩 편차([[embedding-probing]])의 변동 중 0.544는 발화 길이가 설명했다. 길이를 뺀 뒤 eGeMAPS 88개가 추가로 설명한 몫은 0.072였고, 0.384는 설명되지 않았다.
  - 길이를 통제한 뒤 가장 관련 높은 상위 10개는 음질·음색 계열 8개(MFCC, 포먼트 F1~F3, shimmer, 스펙트럼 기울기, HNR)와 무성구간 길이 2개였다.
  - **F0는 상위 10개에 하나도 없었다.**
  - 다만 관련도는 최대 0.13으로 약하다. "임베딩이 음질을 본다"가 아니라 "음질 쪽으로 기운다" 정도로 읽어야 한다.
- **감정 음성 4모델 비교 (LAB 50)**
  - 4모델의 UAR 차이가 0.015밖에 나지 않았다. 성능은 모델이 아니라 **입력 특징이 결정**했다는 결론이다.
- **LogReg 계수 히트맵 (LAB 50)**
  - 피치 평균이 가장 중요한 축이었다.
  - 감정마다 의지하는 음향이 달랐다. 급함은 특정 음색, 놀람은 음량, 의심은 피치에 기댔다.
  - 표적 어조의 특징이 뚜렷한 정도는 DOUBT > DRY > TEASE 순이었다.
  - 계수는 "모델이 그렇게 배웠다"는 뜻이지 자연법칙이 아니다. 각 줄은 "그 감정 vs 나머지"를 따로 채점한 표라서 줄끼리 크기를 비교하면 안 된다.

## 관련
- [[opensmile]] · [[embedding-probing]] · [[f0-pitch]] · [[mfcc]] · [[speech-emotion-recognition]] · [[korean-emotion-speech-datasets]] · [[어조-모듈]] · [[회의-음성-어조-분석-연구]]
- 원글: [LAB 33. 임베딩 편차 음향 분해](https://velog.io/@xorms/LAB-33)
- 원글: [LAB 49. eGeMAPS 88차원, 왜 이 4개 모델로 비교하는가](https://velog.io/@xorms/LAB-49.-eGeMAPS-88%EC%B0%A8%EC%9B%90-%EC%99%9C-%EC%9D%B4-4%EA%B0%9C-%EB%AA%A8%EB%8D%B8%EB%A1%9C-%EB%B9%84%EA%B5%90%ED%95%98%EB%8A%94%EA%B0%80)
- 원글: [LAB 50. 감정 음성 데이터셋 4모델 비교 - LOSO](https://velog.io/@xorms/LAB-50)
