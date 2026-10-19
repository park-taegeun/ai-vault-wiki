---
type: concept
modified: 2026-10-19
sources: [_private/raw/notion/LAB/랩미팅/0619/스크립트 383d8df03cab80e7a50dcab1e44d0831.md, _private/raw/velog/AI_LAB/2026-05-26-LAB-9.-Gemma-4-로컬-셋업.md, _private/raw/velog/AI_LAB/2026-05-26-LAB-10.-Sarcasm-탐지-실험1.md, _private/raw/velog/AI_LAB/2026-05-28-LAB-14.-Gemma-4-음성-파이프라인-설계-1-MFCC-어조-그리고-추상화-레벨의-함정.md, _private/raw/velog/AI_LAB/2026-05-28-LAB-Gemma-4-E4B-it-첫-로드-테스트.md, _private/raw/velog/AI_LAB/2026-05-28-LAB-16.md, _private/raw/velog/AI_LAB/2026-05-28-LAB-17-win3cgck.md, _private/raw/velog/AI_LAB/2026-06-02-LAB-26.-Gemma-4-ASR-파인튜닝-1-도메인-적응-목표-설정과-데이터-준비.md, _private/raw/velog/AI_LAB/2026-06-11-LAB-28.-랩미팅-피드백-가벼운-모델-실험.md, _private/raw/velog/AI_LAB/2026-06-16-LAB-29.md, _private/raw/velog/AI_LAB/2026-06-16-LAB-31.md, _private/raw/velog/AI_LAB/2026-06-22-LAB-35.-파인튜닝-소규모-학습검증.md, _private/raw/velog/AI_LAB/2026-06-23-LAB-38.-오디오-경로-구조-검증.md, _private/raw/velog/AI_LAB/2026-07-28-LAB-57.-표현-수준-융합-설계.md]
tags: [gemma-4, llm, multimodal, asr, tokenizer]
---

## 한 줄 정의
Google의 오픈 가중치 멀티모달 모델이다. E4B-it 하나로 텍스트, 오디오, 이미지를 함께 입력받는다(`Gemma4ForConditionalGeneration`). 이 연구에서는 회의 음성 ASR의 백본으로 썼고, 이후 [[어조-모듈]]의 벡터를 받아들이는 융합단으로 썼다.

## 핵심 내용
### 구조
```
gemma-4-E4B-it
├─ vision_tower    이미지 (미사용)
├─ audio_tower     소리, 12층 conformer → 1536차원
├─ embed_audio     1536 → 2560 (RMSNorm → Linear, bias 없음)
└─ language_model  42층, hidden 2560
```
- **config로 확인한 정보 (LAB 15)**
  - 클래스 정보는 `architectures: ['Gemma4ForConditionalGeneration']`, `model_type: gemma4`다.
  - 설정은 `text_config`, `audio_config`, `vision_config` 세 덩어리로 나뉜다.
- **프로세서**
  - `AutoProcessor`로 불러오면 `Gemma4Processor`가 나온다.
  - 그 안에 토크나이저, `Gemma4AudioFeatureExtractor`, 이미지 프로세서가 들어 있다.
  - 오디오는 16kHz로 받는다.
- **LoRA를 붙일 수 있는 자리 (LAB 35)**
  - language_model 42층 중 앞 24층에는 q·k·v·o가 있다.
  - 뒤 18층은 KV를 공유해서 q·o만 있다.
  - 그래서 attention에 LoRA를 붙일 수 있는 자리는 24×4 + 18×2 = 132개다. → [[lora]]
- **모델 변형**
  - 주로 E4B를 NF4로 양자화해서 썼다.
  - 비교용으로 E2B(`google/gemma-4-E2B-it`)를 BF16 그대로 썼다. → [[quantization]]

### 오디오가 들어가는 방식 (LAB 29·57)
```
오디오 ──→ audio_tower ──→ embed_audio ──┐
                                         ├─→ language_model ──→ 토큰 생성 ──→ 전사
텍스트 ──→ 토크나이저 ──→ 토큰 임베딩 ────┘
```
- **오디오 토큰 배치**
  - 오디오는 토큰화하지 않는다. audio_tower가 짧은 시간 조각마다 벡터를 하나씩 만든다. 1초에 약 25개다.
  - 프로세서는 프롬프트에 `[boa(256000)][audio(258881) × N][eoa(258883)]`을 깔아 둔다.
  - forward 단계에서 `masked_scatter`가 그 자리를 오디오 임베딩으로 바꿔 끼운다.
  - 이 구조가 이미 있으니 프롬프트에 오디오 경계를 텍스트 태그로 따로 적을 필요는 없다.
- **LLM은 출처를 구분하지 않는다**
  - LLM은 벡터가 토큰에서 왔는지 오디오에서 왔는지 모른다.
  - 전사는 LLM이 토큰을 하나씩 "지어내는" 결과다.
  - 그래서 오디오 조건이 약하면 [[asr-hallucination]]이 생긴다.
  - 텍스트 임베딩, boa, 오디오 벡터들, eoa, 텍스트 임베딩이 **하나의 연속 시퀀스**로 self-attention에 들어간다. 한 줄 안의 모든 토큰이 서로를 보며 무엇을 얼마나 가져올지 정하고, 텍스트와 오디오의 통합은 이 연산에서 일어난다. 그 앞의 projection은 오디오 인코더 출력 차원을 LLM 임베딩 차원에 맞추는 작업이다(0619 랩미팅).
- **구현 주의점**
  - 5.9.0 버전의 `masked_scatter`는 dtype을 맞춰주지 않는다.
  - 프로세서는 wav가 없으면 audio 토큰을 깔지 않는다.
  - 이 두 가지가 외부 벡터를 soft token으로 넣을 때의 주의점이다. → [[표현-수준-융합]]
- **채팅 템플릿 토큰**: `<|turn>`=105, `model`=4368, `<turn|>`=106, `\n`=107. 파인튜닝할 때 정답 구간을 찾는 기준이다. → [[asr-fine-tuning]]

### ASR로 쓰기 (LAB 14·16)
- Whisper 같은 외부 STT 없이 wav를 직접 받는다. 처리 단위는 30초다(30초 × 25 = 오디오 토큰 750개).
- 음성 입력은 `messages`의 `content`에 텍스트 지시와 `{"type": "audio", "audio": audio_array}`를 나란히 넣는다.
- Google 공식 ASR 프롬프트를 쓴다. `{LANGUAGE}`에 언어 이름을 넣고 "Only output the transcription, with no newlines."처럼 출력 형식을 지시한다.
- 출력 앞에는 입력 프롬프트가 붙어 나온다. `input_len`만큼 잘라내야 한다.

## 언제 쓰나 (상황 예시)
- 12GB급 GPU에서 멀티모달 LLM을 돌려야 할 때. 4-bit 로드가 전제다.
- 별도 STT 없이 음성을 바로 LLM에 넣고 싶을 때
- 발화가 어떤 발화인지(차분한 설명, 질문의 뉘앙스 등)를 자연어로 해석하게 할 때

## 실습에서 배운 것 / 트러블슈팅
- **로컬 셋업 (LAB 09)**
  - 토큰은 쉘 환경 변수 `HF_TOKEN`에서 읽는다. 값은 `<REDACTED>`이고, 코드에 평문으로 두지 않는다.
  - 본체(약 9GB)를 받기 전에 5MB짜리 토크나이저부터 받는다. 인증, 네트워크, 캐시가 정상인지 먼저 확인하기 위해서다.
- **첫 로드 결과 (LAB 15)**
  - RTX 5070에서 NF4로 로드하는 데 9.7초가 걸렸다. VRAM은 8.665GB를 썼다.
  - 텍스트로 자기소개를 시키자 23토큰을 2.0초에 생성했다(약 11 tok/s).
  - LAB 35에서 학습용으로 로드했을 때는 할당량이 약 9.756GB였다. 로드 조건이 다르다.
- **스스로를 "Gemini"라고 소개했다 (LAB 09)**: 모델의 환각이다. 표면 발화의 사실성을 믿기 어렵다는 연구상 시사점이 됐다.
- **텍스트만으로 화행을 판단하게 하면 의심 쪽으로 기운다.** → [[sarcasm-detection]]
- **토크나이저는 환각 원인이 아니다 (LAB 29)**
  - SentencePiece 계열이다. 한국어·영어 모두 encode→decode가 원문과 똑같이 돌아왔다.
  - "바야흐로" 같은 드문 표현은 음절 단위로 쪼개진다.
  - "한국어 토크나이저로 바꾸면 환각이 줄 것"이라는 가설은 이 결과로 기각했다.
- **Gemma 4는 측정기가 아니라 해석기다 (LAB 31)**
  - 피치, 발화속도, 억양, 음량 등 7개 항목을 지정하고 "추측·내용 요약 금지"를 걸어 서술하게 했다. 서술은 깔끔해졌다.
  - 하지만 Hz, dB 같은 수치는 하나도 나오지 않았다. 5개 샘플을 사실상 같은 형용사로 묘사했다.
  - [[opensmile]] 실측과 비교하니 억양 변화폭의 방향(논리형이 가장 평탄하고 감정형이 가장 큼)은 맞혔다. 틀린 게 아니라 해상도가 낮은 것이다.
  - 그래서 상대적인 수치 변화를 잡는 일은 측정 도구에 맡겼다. → [[opensmile]], [[어조-모듈]]

## 관련
- [[audio-tower]] · [[quantization]] · [[huggingface-transformers]] · [[transformer]] · [[asr]] · [[asr-hallucination]] · [[asr-fine-tuning]] · [[lora]] · [[sarcasm-detection]] · [[opensmile]] · [[embedding-probing]] · [[표현-수준-융합]] · [[어조-모듈]] · [[회의-음성-어조-분석-연구]]
- 원글: [LAB 09. Gemma 4 로컬 셋업](https://velog.io/@xorms/LAB-9.-Gemma-4-%EB%A1%9C%EC%BB%AC-%EC%85%8B%EC%97%85)
- 원글: [LAB 15. Gemma 4 E4B-it 첫 로드 테스트](https://velog.io/@xorms/LAB-Gemma-4-E4B-it-%EC%B2%AB-%EB%A1%9C%EB%93%9C-%ED%85%8C%EC%8A%A4%ED%8A%B8)
- 원글: [LAB 29. 토크나이저 & 태그 실험](https://velog.io/@xorms/LAB-29)
- 원글: [LAB 31. Gemma4 음성특징 스모크 + openSMILE 비교](https://velog.io/@xorms/LAB-31)
- 원글: [LAB 57. 표현 수준 융합 설계](https://velog.io/@xorms/LAB-57.-%ED%91%9C%ED%98%84-%EC%88%98%EC%A4%80-%EC%9C%B5%ED%95%A9-%EC%84%A4%EA%B3%84)
