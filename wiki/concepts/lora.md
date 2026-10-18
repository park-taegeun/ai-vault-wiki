---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/AI_LAB/2026-05-22-LAB-06.-기초를-다지자4.md, _private/raw/velog/AI_LAB/2026-05-21-LAB-04.-window-환경-셋업.md, _private/raw/velog/AI_LAB/2026-06-01-LAB-24.-LoRA-파인튜닝.md, _private/raw/velog/AI_LAB/2026-06-02-LAB-26.-Gemma-4-ASR-파인튜닝-1-도메인-적응-목표-설정과-데이터-준비.md, _private/raw/velog/AI_LAB/2026-06-22-LAB-35.-파인튜닝-소규모-학습검증.md, _private/raw/velog/AI_LAB/2026-06-23-LAB-37.-파인튜닝-결론.md, _private/raw/velog/AI_LAB/2026-06-23-LAB-38.-오디오-경로-구조-검증.md, _private/raw/velog/AI_LAB/2026-06-29-LAB-39.md, _private/raw/velog/AI_LAB/2026-06-29-LAB-41.-audiotower-LoRA-학습.md]
tags: [lora, qlora, peft, fine-tuning, gemma-4]
---

## 한 줄 정의
원래 가중치 W는 그대로 두고, 바뀌는 양 ΔW를 작은 행렬 두 개의 곱 A×B로 근사해서 A와 B만 학습하는 파인튜닝 기법이다. 4비트로 양자화한 모델 위에 붙이면 QLoRA라고 부른다.

## 핵심 내용
- **일반 파인튜닝이 비싼 이유**: 가중치 행렬 하나가 4096×4096이면 약 1,600만 파라미터다. 레이어가 수십 개면 수십억 개가 되고, 이걸 전부 업데이트하려면 VRAM이 몇 배로 든다.
- **핵심 관찰**: 파인튜닝할 때 실제로 바뀌는 ΔW는 rank가 낮다. 그래서 훨씬 작은 행렬로 표현할 수 있다.
- **방법**: `ΔW ≈ A × B`
  - A는 4096×8, B는 8×4096이다.
  - rank 8이면 학습할 파라미터가 16,777,216개에서 65,536개로, 약 256배 줄어든다.
  - 추론할 때는 W + A×B를 쓴다.
  - 모듈 하나에 lora_A(압축)와 lora_B(복원) 두 개가 붙는다. 그래서 96자리에 붙이면 학습 텐서는 192개다.
- **rank 고르기**
  - 4: 작고 빠르다. 표현력이 낮다.
  - 8: 균형이 맞아 가장 많이 쓴다.
  - 16: 표현력이 높고 메모리를 더 쓴다.
- **라이브러리**: `peft`가 LoRA를, `bitsandbytes`가 [[quantization]]을 맡는다.

## 언제 쓰나 (상황 예시)
- VRAM 12GB 정도인 단일 GPU에서 큰 모델을 특정 도메인에 맞출 때. 예: [[gemma-4]]를 회의 음성에 맞추는 [[asr-fine-tuning]]
- base 모델과 파인튜닝 모델을 깔끔하게 비교하고 싶을 때. 같은 로드 상태에서 어댑터만 켜고 끄면 된다.

## 실습에서 배운 것 / 트러블슈팅
- **Gemma 4 E4B에 QLoRA 붙이기 (LAB 26·35)**
  ```python
  model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
  model = prepare_model_for_kbit_training(model)
  for param in model.model.audio_tower.parameters():
      param.requires_grad = False
  lora_config = LoraConfig(r=8, lora_alpha=16, target_modules=target_modules,
                           lora_dropout=0.05, bias="none", task_type=TaskType.CAUSAL_LM)
  model = get_peft_model(model, lora_config)
  ```
  - 붙인 곳은 language_model의 attention이다. 앞 24층은 q·k·v·o에 96자리, KV를 공유하는 뒤 18층은 q·o에 36자리, 합쳐서 132자리다.
  - 결과는 `trainable params: 4,538,368 || all params: 7,945,639,200 || trainable%: 0.0571`이었다. 붙인 뒤 메모리 할당량은 9.775GB였다.
- **어디에 붙이느냐가 결과를 정한다 (LAB 37·38)**
  - 텍스트 쪽(language_model)에 붙인 LoRA는 사전분포 P(전사문)만 바꿨다. 말투를 회의 쪽 prior로 옮겼을 뿐이다.
  - 가능도 P(오디오|전사문)는 건드리지 않았다. 그래서 모델은 오디오를 더 듣는 대신 "짧게 말하기"라는 쉬운 길을 찾았다.
  - 교훈: prior를 조정하는 개입으로는 prior에 지배되는 문제를 풀 수 없다. → [[asr-hallucination]]
- **오디오 경로에 붙였을 때 (LAB 39·41)**
  - 결합 지점(embed_audio)에 붙였더니 짧은 발화 환각이 크게 줄었다. 오디오 길이와 출력 길이의 상관(Pearson)은 0.755가 됐고, 과생성은 35.5%에서 3.1%로 떨어졌다.
  - audio_tower 12층의 attention과 FFN에 붙였더니 초단발화 발음 오인식은 6건 중 하나도 고치지 못했다. → [[audio-tower]]
- **효과를 먼저 확인한다**: 어떤 모듈에 붙여야 할지 근거가 없으면 disable과 enable을 바꿔 가며 변수 하나만 비교해 효과부터 본다.

## 관련
- [[asr-fine-tuning]] · [[gemma-4]] · [[audio-tower]] · [[quantization]] · [[asr-hallucination]] · [[huggingface-transformers]] · [[transformer]] · [[wsl2-cuda-setup]] · [[회의-음성-어조-분석-연구]]
- 원글: [LAB 24. LoRA 파인튜닝](https://velog.io/@xorms/LAB-24.-LoRA-%ED%8C%8C%EC%9D%B8%ED%8A%9C%EB%8B%9D)
- 원글: [LAB 35. 파인튜닝 - 소규모 학습/검증](https://velog.io/@xorms/LAB-35.-%ED%8C%8C%EC%9D%B8%ED%8A%9C%EB%8B%9D-%EC%86%8C%EA%B7%9C%EB%AA%A8-%ED%95%99%EC%8A%B5%EA%B2%80%EC%A6%9D)
- 원글: [LAB 41. audio_tower LoRA 학습](https://velog.io/@xorms/LAB-41.-audiotower-LoRA-%ED%95%99%EC%8A%B5)
