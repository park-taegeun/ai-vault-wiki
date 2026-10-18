---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/AI_LAB/2026-06-02-LAB-26.-Gemma-4-ASR-파인튜닝-1-도메인-적응-목표-설정과-데이터-준비.md, _private/raw/velog/AI_LAB/2026-06-16-LAB-29.md, _private/raw/velog/AI_LAB/2026-06-16-LAB-30.-임베딩-프로빙.md, _private/raw/velog/AI_LAB/2026-06-23-LAB-38.-오디오-경로-구조-검증.md, _private/raw/velog/AI_LAB/2026-06-29-LAB-41.-audiotower-LoRA-학습.md, _private/raw/velog/AI_LAB/2026-06-29-LAB-42.-발음-오인식-외부-ASR-진단.md, _private/raw/velog/AI_LAB/2026-06-30-LAB-43.-depthwise-conv-음소-개입-실험.md, _private/raw/velog/AI_LAB/2026-07-02-LAB-44.-긴-발화-audiotower-발음-오인식-효과-검증.md]
tags: [audio-tower, gemma-4, conformer, embed-audio, depthwise-conv, 발음오인식]
---

## 한 줄 정의
[[gemma-4]]의 오디오 인코더다. 소리를 LLM이 읽을 수 있는 벡터 시퀀스로 바꾸는 "귀" 역할을 하며, 12층 conformer로 되어 있다. 출력은 `embed_audio`라는 결합 통로를 지나 language_model로 들어간다.

## 핵심 내용
### 오디오가 지나는 길 (LAB 38, E4B-it)
```
오디오 파형
 ↓ subsample       긴 소리를 짧게 압축
 ↓ rel_pos_enc     상대 위치 정보 부착
 ↓ layers (12층)   특징 추출
 ↓ output_proj     1024 → 1536
 ↓ embed_audio     1536 → 2560   ← 오디오와 텍스트의 결합 지점
 ↓ language_model  42층, 텍스트 생성
```
- **한 층의 구성**: FFN1 → self_attn → lconv1d(depthwise conv) → FFN2
  - self_attn은 시점끼리의 관계를 보고, 구성은 q·k·v·post다.
  - depthwise conv는 이웃한 몇 시점의 짧은 패턴을 본다.
  - FFN은 시점마다 따로 값을 정리한다.
- **오디오 토큰 수**: 1초에 약 25개다.
- **LLM과 만나는 방식**: 출력 벡터가 프롬프트의 `<|audio|>` 자리를 덮어쓴다. (LAB 29)
- **결합 지점**: 오디오 쪽(1536차원)과 글자 쪽(2560차원)은 차원이 달라 변환이 필요하다. `embed_audio` 안의 `embedding_projection`이 그 역할을 한다.

### 오디오 경로에 개입하는 두 방향 (LAB 38)
1. **가능도 키우기**: audio_tower를 학습시켜 특징을 더 정확히 뽑게 한다.
2. **결합 지점 강화**: 약한 오디오 신호를 LLM의 prior가 덮어쓰지 못하게 한다.

결합 지점을 먼저 건드렸다. 결합 지점만 강화했는데 효과가 나면 문제는 "인코딩"이 아니라 "전달"이었다는 뜻이다. 그래서 결합 지점 실험이 audio_tower에 문제가 있는지 가리는 진단 도구가 된다. 실제로 효과가 컸다(→ [[asr-fine-tuning]]).

## 언제 쓰나 (상황 예시)
- 멀티모달 모델이 오디오를 무시할 때, 원인이 인코딩인지 전달인지 나눠서 진단할 때
- 오디오가 텍스트로 바뀌기 전에 표현에 무엇이 남아 있는지 볼 때. 발화 하나를 1536차원 벡터로 요약하면 된다. → [[embedding-probing]]

## 실습에서 배운 것 / 트러블슈팅
- **처음에 얼린 이유 (LAB 26)**
  - 학습시키면 파라미터가 약 1억 5천만 개 늘어난다.
  - 대량 오디오로 이미 사전학습되어 있다.
  - 환각은 LLM 쪽에서 생긴다고 판단했다.
- **프로빙 결과 (LAB 30)**
  - audio_tower 표현에는 같은 글자("네/어/음")라도 감정 차이가 남아 있었다.
  - 정서 정보는 텍스트로 옮기는 단계에서 버려진다.

### 발음 오인식은 어디서 오나 (LAB 41~44)
결합 지점을 강화한 뒤에도 초단발화의 발음 오인식(예: "거부"를 "극복"으로 들음)은 남았다. 그래서 네 단계로 원인을 좁혀 갔다.

| 실험 | 개입 | 결과 |
|---|---|---|
| LAB 41 | audio_tower 12층의 attn(q/k/v/post)과 FFN에 LoRA (96자리) | 발음 오인식 6개 중 0개 복구. 평균이 내려간 건 도피 1건이 고쳐진 이상치 효과였다. 실제로는 나빠진 발화가 좋아진 발화의 2배였다. |
| LAB 42 | 같은 6개를 Whisper large-v3에 넣기 | 외부 모델은 음소를 맞혔다. 정보는 입력에 있는데 본 모델이 뽑지 못한 것이다. 고유명사 1건만 사전 문제였다. |
| LAB 43 | depthwise conv만 따로 full-FT (학습 파라미터 61,440) | loss가 거의 움직이지 않았다. 학습량을 4배로 늘려도 바뀐 글자가 하나도 없었다. |
| LAB 44 | 긴 발화 40개로 다시 검증 (base, 통로만, 통로+귀) | base → 통로 → 통로+귀 순으로 CER이 줄었다. 개선 폭이 큰 상위 6개에서는 발음 오인식이 어느 정도 해결됐다. |

> [!note] 결론이 바뀐 순서
> - LAB 42: 정보는 입력에 있고, 추출에 실패했다.
> - LAB 43: 가벼운 개입으로는 안 되니, 한계는 인코더의 용량이다.
> - LAB 44: 초단발화에만 해당하는 결론이었다. 한계는 **입력 정보량 × 인코더 용량**의 상호작용이다.
>
> LAB 42에서 Whisper가 맞혔다고 해서 Gemma 쪽 결론과 모순되지는 않는다. "대형 전용 ASR은 그 짧은 정보로도 음소를 뽑지만, 가벼운 LoRA로 Gemma의 귀를 그 수준까지 올리기는 어렵다"로 읽으면 세 결론이 이어진다. 이 해석은 위키를 정리하면서 붙인 것이다.

- **변수를 격리하는 법**: 학습 가능한 텐서를 출력해서 원하는 모듈만 열렸는지 확인한다. 예를 들어 conv 실험에서는 통로(embed_audio)의 trainable이 0이어야 한다.
- **발음 샘플은 학습에서 뺀다**: 6개를 학습에 넣으면 음소 변별이 아니라 6문장을 외우게 된다. 그래서 held-out으로 떼어 두고 train에 섞이지 않았는지 확인했다.
- **LoRA를 넓게 붙일 때의 위험**: 96자리에 붙이면 과적합과 ASR 저하가 생길 수 있다. 그래서 disable과 enable을 바꿔 가며 변수 하나만 비교했다.
- **결론에는 샘플 조건을 적는다**: 결론을 낸 샘플 조건(예: 초단발화)을 함께 적어야 일반화 오류를 피한다.

> [!note] 원문 수치
> LAB 43 본문에 "465 스텝"과 "310스텝"이 함께 나온다. 계산식(2485/16 ≈ 155 × 2에폭)과 로그를 보면 310이다.

## 관련
- [[gemma-4]] · [[lora]] · [[asr-fine-tuning]] · [[asr-hallucination]] · [[asr]] · [[quantization]] · [[embedding-probing]] · [[표현-수준-융합]] · [[회의-음성-어조-분석-연구]]
- 원글: [LAB 38. 오디오 경로 구조 검증](https://velog.io/@xorms/LAB-38.-%EC%98%A4%EB%94%94%EC%98%A4-%EA%B2%BD%EB%A1%9C-%EA%B5%AC%EC%A1%B0-%EA%B2%80%EC%A6%9D)
- 원글: [LAB 41. audio_tower LoRA 학습](https://velog.io/@xorms/LAB-41.-audiotower-LoRA-%ED%95%99%EC%8A%B5)
- 원글: [LAB 42. 발음 오인식 외부 ASR 진단](https://velog.io/@xorms/LAB-42.-%EB%B0%9C%EC%9D%8C-%EC%98%A4%EC%9D%B8%EC%8B%9D-%EC%99%B8%EB%B6%80-ASR-%EC%A7%84%EB%8B%A8)
- 원글: [LAB 43. depthwise conv 음소 개입 실험](https://velog.io/@xorms/LAB-43.-depthwise-conv-%EC%9D%8C%EC%86%8C-%EA%B0%9C%EC%9E%85-%EC%8B%A4%ED%97%98)
- 원글: [LAB 44. 긴 발화 audio_tower 발음 오인식 효과 검증](https://velog.io/@xorms/LAB-44.-%EA%B8%B4-%EB%B0%9C%ED%99%94-audiotower-%EB%B0%9C%EC%9D%8C-%EC%98%A4%EC%9D%B8%EC%8B%9D-%ED%9A%A8%EA%B3%BC-%EA%B2%80%EC%A6%9D)
