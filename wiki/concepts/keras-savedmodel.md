---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/졸업작품-기록/2026-07-01-졸업작품-기록-41.md]
tags: [tensorflow, keras, 배포, 서빙]
---

## 한 줄 정의
학습된 Keras 모델을 서버가 그대로 물고 추론할 수 있는 TensorFlow SavedModel 포맷으로 내보내는 것이다. Keras 3에서는 `model.export()`가 정공법이다.

## 핵심 내용
- `.keras` 파일(학습 산출물)과 SavedModel(서빙 아티팩트)은 다르다. `.keras`가 로드·추론이 멀쩡해도 SavedModel export는 실패할 수 있다.
- 구식 경로 `tf.saved_model.save()`는 TF-Hub 모듈처럼 내부에 자기 SavedModel 리소스를 들고 있는 서브모듈을 추적하지 못해 `untracked resource`를 낸다.
- `model.export(path)`는 저장 시점에 serving용 `tf.function`을 실제로 트레이스하고, 그 과정에서 backbone이 안고 있던 리소스까지 SavedModel 그래프에 넣는다.
- export 로그의 입력 `(None, None)`은 `tf.function`의 polymorphic 표기일 뿐이다. 실제 시그니처는 Keras `Input` 정의를 봐야 한다 (예: `Input(shape=(None,), batch_size=1)` → `(1, None)`).

## 언제 쓰나 (상황 예시)
- frozen backbone(TF-Hub YAMNet 등) 위에 head만 fine-tuning한 모델을 서버에 배포할 때.
- 재학습 없이 체크포인트(`best.keras`)만으로 서빙 모델을 다시 뽑아야 할 때. export를 독립 엔트리포인트로 분리해 두면 된다.

## 실습에서 배운 것 / 트러블슈팅
- [[띵동]]에서 frozen [[yamnet]] backbone + head 구조를 `tf.saved_model.save()`로 저장하다 `untracked resource`가 났다. 정확한 원인은 Lambda 레이어(`yamnet_backbone`)가 raw `hub.load()` 결과를 클로저로 캡처했는데, 그 객체가 모델 객체 그래프에 등록되지 않았던 것이다. 처음 진단은 "backbone 변수 미추적"이었고, 방향은 맞았지만 지점이 달랐다 → [[ai-산출물-검증]]
- 해법: `best.keras` → `model.export("inference_savedmodel/")`. `ml/training/export.py`로 분리하고, 체크포인트가 없으면 `FileNotFoundError`로 안내한다.
- 완료 판정은 실제 `best.keras` + 실제 YAMNet으로 export → `tf.saved_model.load`로 reload → `serving_default` 추론에서 출력 shape `(1, 3)`, softmax 합 1.0을 확인한 뒤에 했다. 더미 backbone 주입 검증으로는 hub 리소스 문제가 재현되지 않는다.
- 최종 서빙 시그니처:
  ```
  serving_default
    입력:  waveform  (1, None)  float32   # 배치 1 고정, 가변 길이
    출력:  logits    (1, 3)     float32   # doorbell=0 / knock=1 / fire_alarm=2
  ```
  라벨 인덱스는 config의 `CLASSES`를 상속해 한 곳에서 관리한다 → [[single-source-of-truth]]
- **회귀 방지**: `test_export_smoke.py`에 ① 구식 `tf.saved_model.save`가 untracked resource로 실패하는 재현 assert, ② `model.export` 성공, ③ reload한 `serving_default` 추론 정상을 넣었다. 구식 경로로 되돌리면 테스트에서 걸린다 → [[대조-가드]]
- PR 브랜치에만 있는 `export.py`를 로컬에서 돌리면 `No module named ...`가 난다. 웹에서 머지한 뒤 `git checkout main && git pull`을 해야 한다 → [[github-flow]]

## 관련
- [[yamnet]] · [[transfer-learning]] · [[ai-산출물-검증]] · [[single-source-of-truth]] · [[대조-가드]] · [[github-flow]] · [[띵동]]
- 원글: [졸업작품 기록 (41)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-41)
