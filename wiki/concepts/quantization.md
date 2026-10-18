---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/AI_LAB/2026-05-26-LAB-9.-Gemma-4-로컬-셋업.md, _private/raw/velog/AI_LAB/2026-05-26-LAB-10.-Sarcasm-탐지-실험1.md, _private/raw/velog/AI_LAB/2026-05-28-LAB-Gemma-4-E4B-it-첫-로드-테스트.md, _private/raw/velog/AI_LAB/2026-05-28-LAB-16.md, _private/raw/velog/AI_LAB/2026-06-11-LAB-28.-랩미팅-피드백-가벼운-모델-실험.md, _private/raw/velog/AI_LAB/2026-06-22-LAB-35.-파인튜닝-소규모-학습검증.md]
tags: [quantization, nf4, bitsandbytes, qlora, gemma-4]
---

## 한 줄 정의
모델 가중치를 더 적은 비트로 저장해 VRAM 사용량을 줄이는 기법이다. 이 연구에서는 bitsandbytes의 NF4 4-bit 양자화를 썼다.

## 핵심 내용
- **NF4 (Normal Float 4)**
  - 값을 4-bit 정수로 균등하게 나누지 않고, 정규분포 모양에 맞춰 4-bit에 배정한다.
  - LLM 가중치는 대부분 정규분포에 가깝기 때문에 이 방식이 잘 맞는다. QLoRA 논문에서 검증됐다.
- **저장과 계산의 정밀도가 다르다**: 저장은 4-bit로 하고 계산은 BF16으로 한다. 메모리는 줄이면서 계산 정확도는 지키는 방식이고, QLoRA의 핵심 아이디어다.
- **설정 예**
  ```python
  BitsAndBytesConfig(
      load_in_4bit=True,
      bnb_4bit_quant_type="nf4",
      bnb_4bit_compute_dtype=torch.bfloat16,
      bnb_4bit_use_double_quant=True,   # 양자화 상수도 양자화
  )
  ```

## 언제 쓰나 (상황 예시)
- 12GB급 소비자 GPU에 멀티모달 LLM을 올릴 때. [[gemma-4]] E4B-it는 BF16으로는 14.79GB라서 RTX 5070(12GB)에서 swap이 생기고 추론 중 OOM이 난다.

## 실습에서 배운 것 / 트러블슈팅
- **실측 VRAM은 단순 계산보다 높다 (LAB 15)**
  - NF4로 로드하는 데 9.7초가 걸렸다.
  - VRAM 사용량은 allocated 8.665GB / 11.94GB(72.6%)였다. 추론에 쓸 KV cache 여유는 약 3.3GB 남았다.
  - LAB 09에서는 약 4~5GB를 예상했다. 실제로 더 많이 나온 이유는 양자화가 Transformer 레이어에만 적용되기 때문이다. 임베딩(256k 어휘)과 오디오·비전 인코더는 bf16으로 남는다.
- **멀티모달 모델은 오디오 타워를 양자화에서 빼야 한다 (LAB 16)**
  - 증상: 양자화한 상태로 한국어 음성을 받아쓰게 하면 제대로 옮기지 못했다. 텍스트 입력은 정상이었다.
  - 근거: transformers 이슈 #45674. 멀티모달 Gemma4는 품질을 지키려면 오디오·비전 타워를 양자화 대상에서 명시적으로 빼야 하고, 특히 오디오가 취약하다고 적혀 있다.
  - 조치: 오디오 타워를 제외하자 정상적으로 받아썼다. → [[audio-tower]]
- **양자화가 환각의 원인인가? E2B BF16 대조 실험 (LAB 28)**
  - 목적: 짧은 발화 환각이 NF4 양자화 때문인지, instruction-tuned 생성 모델의 구조 때문인지 가른다.
  - 로드 후 `Counter(str(p.dtype) for p in model.parameters())`로 모든 파라미터가 bf16인지 확인했다.

  | 지표 | E4B NF4 | E2B BF16 |
  |---|---|---|
  | mean CER | 0.579 | 0.342 |
  | median CER | 0.231 | 0.211 |
  | 환각률(CER>1.0) | 12.6% | 4.2% |

  - median CER은 거의 그대로였다. 줄어든 것은 "환각 꼬리" 쪽이다.
  - 길이 구간별 환각률은 모든 구간에서 떨어졌다. 10자 이하는 68.6%에서 41.0%로, 11~20자는 43.4%에서 12.2%로 내려갔다. 하지만 짧을수록 환각이 많은 구조는 두 모델이 같았다.
  - 결론: **양자화는 짧은 발화 환각의 근본 원인이 아니다.** 환각의 심한 정도만 절반 가까이 줄였다.
  - 한계: 모델 크기도 E4B에서 E2B로 함께 바뀌었다. 같은 크기에서 NF4와 BF16을 비교해야 양자화만의 효과를 분리할 수 있다. → [[asr-hallucination]]
- **어댑터 효과만 보려면 양자화 조건을 고정한다 (LAB 35)**: 파인튜닝 효과만 비교하려고 E4B를 NF4(연산 bf16)로 로드했다. base와 finetuned는 같은 모델에 어댑터만 붙였다 뗐다 하며 비교했다. → [[asr-fine-tuning]]

## 관련
- [[gemma-4]] · [[lora]] · [[huggingface-transformers]] · [[asr]] · [[asr-hallucination]] · [[audio-tower]] · [[wsl2-cuda-setup]]
- 원글: [LAB 09. Gemma 4 로컬 셋업](https://velog.io/@xorms/LAB-9.-Gemma-4-%EB%A1%9C%EC%BB%AC-%EC%85%8B%EC%97%85)
- 원글: [LAB 15. Gemma 4 E4B-it 첫 로드 테스트](https://velog.io/@xorms/LAB-Gemma-4-E4B-it-%EC%B2%AB-%EB%A1%9C%EB%93%9C-%ED%85%8C%EC%8A%A4%ED%8A%B8)
- 원글: [LAB 16. ARS 동작 테스트 - 오디오 타워 양자화 제외](https://velog.io/@xorms/LAB-16)
- 원글: [LAB 28. 랩미팅 피드백 & 가벼운 모델 실험](https://velog.io/@xorms/LAB-28.-%EB%9E%A9%EB%AF%B8%ED%8C%85-%ED%94%BC%EB%93%9C%EB%B0%B1-%EA%B0%80%EB%B2%BC%EC%9A%B4-%EB%AA%A8%EB%8D%B8-%EC%8B%A4%ED%97%98)
