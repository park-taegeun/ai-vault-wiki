---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/졸업작품-기록/2026-03-19-졸업작품-기록4.md, _private/raw/velog/졸업작품-기록/2026-03-27-졸업작품-기록5.md, _private/raw/velog/졸업작품-기록/2026-04-27-졸업작품-기록12.md, _private/raw/velog/졸업작품-기록/2026-04-27-졸업작품-기록-13.md, _private/raw/velog/졸업작품-기록/2026-04-28-졸업작품-기록-14.md, _private/raw/velog/졸업작품-기록/2026-07-01-졸업작품-기록-40.md, _private/raw/velog/졸업작품-기록/2026-07-01-졸업작품-기록-41.md, _private/raw/velog/졸업작품-기록/2026-07-08-졸업작품-기록-44.md]
tags: [오디오, 사전학습, 분류, tensorflow]
---

## 한 줄 정의
Google이 VGGish 이후에 만든 오디오 분류용 사전학습 CNN이다. MobileNetV1 기반(2019)이고, AudioSet 521개 클래스로 학습했다.

## 핵심 내용
- **VGGish와 비교**: VGGish는 이미지 모델 VGG를 오디오용으로 바꾼 모델(2017)이다. YAMNet은 그 뒤에 나왔고 더 가볍고 추론이 빠르다.
- **Depthwise Separable Conv**: 일반 Conv가 한 번에 하던 일을 두 단계로 나눈다. 채널마다 따로 특징을 뽑고(Depthwise), 1×1 필터로 채널을 조합한다(Pointwise). 연산량이 크게 줄어든다.
- **입력은 raw waveform**(16kHz mono)이다. 내부에서 64-bin 멜 스펙트로그램을 스스로 만든다. librosa로 뽑은 멜 스펙트로그램을 넣으면 동작하지 않는다. 3초 클립 = 48,000 samples.
- **프레임워크**: TensorFlow가 공식 지원한다(PyTorch는 비공식).
- 학습 데이터 AudioSet은 YouTube에서 추출한 북미/유럽 환경음이 압도적으로 많다.

## 언제 쓰나 (상황 예시)
- 학습 데이터가 적은 소리 분류 문제에서 [[transfer-learning]]/Fine-tuning의 출발점으로.
- 서버 추론 비용·지연 시간을 줄여야 할 때.

## 실습에서 배운 것 / 트러블슈팅
- **고른 이유 (기록 4)**: [[띵동]]은 YAMNet + Fine-tuning, TensorFlow + Keras로 확정했다. 가벼워서 "감지 후 5초 이내 알림"에 유리하고, AudioSet에 초인종·노크·화재경보가 모두 있고, 서버 비용이 낮다. YAMNet이 "초인종"이라고 해도 우리 집 초인종인지는 모른다 → [[초인종-유사도-검증]]
- **pre-trained 그대로는 한국 현관 소리를 못 잡는다** (2026-04-27 사전 테스트, 실제 WAV 클래스당 10개) → [[구현-전-사전-테스트]]

  | 클래스 | Top-1 정확도 | 평균 신뢰도 | 70% 임계값 통과율 |
  |---|---|---|---|
  | 초인종 | 30.0% | 0.187 | 0.0% |
  | 노크 | 40.0% | 0.313 | 20.0% |
  | 화재경보 | 20.0% | 0.267 | 20.0% |

  - 원인은 **도메인 불일치**다. 한국 아파트 초인종은 400~800Hz 단음("딩동")인데 AudioSet 초인종은 멜로디형 차임벨이다. 한국 단독경보형 감지기의 간헐적 비프(삐-삐-삐)도 AudioSet의 연속 사이렌과 시간 패턴이 다르다. 노크는 충격음이라 문화권과 무관하게 파형이 비슷하다.
  - 오탐률 0%는 좋은 결과가 아니었다. 신뢰도가 임계값에 닿지 않아 **아무 알림도 보내지 않은 상태**였다.
  - 지연: 로컬 M4 100회 측정에서 추론 평균 35.1ms(파이프라인의 57%), 최대 117.5ms. 첫 추론은 웜업으로 느리다 → [[nginx-gunicorn]]
- **예비 학습 (2026-07-01, 기록 40)**
  - 구조: YAMNet(hub, frozen) → 1024차원 임베딩 → `Dense(128, relu)` → `Dropout(0.5)` → `Dense(3, softmax)`. 학습 파라미터 131,587개, backbone 약 3.7M.
  - 클래스 불균형: doorbell이 436개로 가장 적었다. `class_weight`는 doorbell 2.10 / knock 1.31 / fire_alarm 0.57.
  - 30 epoch, early stopping이 epoch 18을 골랐다(val_accuracy 0.9016, val_macro_f1 0.8564).
  - **test set (n=424)**: accuracy **0.887**, macro F1 **0.848**.

  | 클래스 | F1 | recall |
  |---|---|---|
  | doorbell | 0.736 | 0.742 |
  | knock | 0.881 | 0.889 |
  | fire_alarm | 0.927 | 0.921 |

  - 사전 테스트 대비 초인종 30% → 74%, 노크 40% → 89%, 화재경보 20% → 92%(이번은 recall). Fine-tuning이 왜 필요한지 숫자로 답할 수 있게 됐다.
  - confusion matrix가 다음 할 일을 정했다. doorbell → fire_alarm 오분류가 10건으로 최다였고 데이터도 가장 적어서, 직접 녹음은 초인종 90클립을 1순위로 잡았다 → [[현관-소리-학습-데이터]]
  - 오분류 방향은 안전 쪽이었다. doorbell을 fire로 착각하는 건 과알림이고, 진짜 위험한 fire → doorbell 놓침은 8건뿐이었다.
- **저장 문제 (기록 41)**: frozen hub backbone을 Lambda 클로저로 감싸면 SavedModel 저장 시 `untracked resource`가 난다 → [[keras-savedmodel]]
- **서버 조기경보 (기록 44, 2GB 인스턴스 기준)**

  ```
  메모리: peak 489MB / 2048MB (약 24%)
  지연:   p95 6.74ms / 5000ms (예산의 0.13%)

  기본 파이썬      36MB
  + AI 프레임워크 376MB  ← 대부분
  + 모델 로드      52MB
  추론 시 peak    489MB
  ```

  메모리 대부분은 모델이 아니라 프레임워크 런타임이었다. 여유가 커서 TFLite 변환 같은 경량화는 필요 없다고 확정했다. 실제 인스턴스를 띄운 숫자는 아니지만, 메모리는 기기 종류를 덜 타는 지표라 조기경보로는 충분했다.
- 이후 재학습과 새 모델 비교는 [[모델-교체-판단]] 참고.

## 관련
- [[cnn]] · [[mel-spectrogram]] · [[transfer-learning]] · [[data-augmentation]] · [[keras-savedmodel]] · [[구현-전-사전-테스트]] · [[현관-소리-학습-데이터]] · [[모델-교체-판단]] · [[초인종-유사도-검증]] · [[2단계-알림]] · [[aws-ec2]] · [[flask]] · [[데이터-라벨-감사]] · [[띵동]]
- 원글: [졸업작품 기록(4)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D4)
- 원글: [졸업작품 기록 (13)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-13)
- 원글: [졸업작품 기록 (40)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-40)
- 원글: [졸업작품 기록 (41)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-41)
- 원글: [졸업작품 기록 (44)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-44)
