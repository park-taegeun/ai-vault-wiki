---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/AI_LAB/2026-05-22-LAB-기초를-다지자-5.md, _private/raw/velog/AI_LAB/2026-05-22-LAB-08.-감정-분석-모델-실습.md, _private/raw/velog/AI_LAB/2026-05-28-LAB-Gemma-4-E4B-it-첫-로드-테스트.md, _private/raw/velog/AI_LAB/2026-05-28-LAB-16.md, _private/raw/velog/AI_LAB/2026-05-29-LAB-19.md]
tags: [huggingface, transformers, pipeline, datasets]
---

## 한 줄 정의
Hugging Face는 모델과 데이터셋을 공유하는 "AI 분야의 GitHub"다. 그 안의 `transformers`는 모든 Transformer 모델을 같은 인터페이스로 불러 쓰게 해 주는 라이브러리다.

## 핵심 내용
- **등장 배경**
  - 예전에는 추론 한 번을 하려면 논문을 읽고, 저자 GitHub에서 학습 코드를 받고, 프레임워크 버전을 맞추고, 가중치를 찾아야 했다.
  - `pytorch-pretrained-bert`가 나오면서 BERT를 코드 3줄로 쓸 수 있게 됐다. 이것이 지금의 `transformers`로 발전했다.
- **4개 기둥**
  - **Hub**: 모델·데이터셋 저장소
  - **transformers**: 모델 표준 인터페이스. 모델 ID만 바꾸면 BERT·LLaMA-3·KcBERT를 같은 코드로 쓴다.
  - **datasets**: 데이터셋 표준 인터페이스. 예: `load_dataset("klue", "ynat")`
  - **Spaces**: 데모 호스팅
- **`pipeline("sentiment-analysis")` 한 줄이 내부에서 하는 일**
  1. Hub에서 기본 모델(DistilBERT)을 받는다.
  2. 가중치와 설정을 로드한다.
  3. 토크나이저를 준비한다.
  4. 모델을 eval 모드로 둔다.
  5. 출력 숫자를 라벨로 바꾸는 후처리를 준비한다.
- **추상화 3단계**

  | 단계 | 도구 | 규모 | 쓰는 때 |
  |---|---|---|---|
  | 1 | `pipeline()` | 3줄 | 빠른 프로토타이핑 |
  | 2 | `AutoModel` + `AutoTokenizer` | 10~30줄 | 토크나이징·후처리 제어, 파인튜닝 |
  | 3 | 모델 클래스 직접 (`BertModel`, `LlamaForCausalLM`) | 50~200줄 | 레이어 수정, [[lora]], 커스텀 헤드 |

## 언제 쓰나 (상황 예시)
- 공개 모델을 빠르게 돌려볼 때는 `pipeline()`을 쓴다.
- 영어 모델을 한국어 모델로 바꿔보고 싶으면 모델 ID만 바꾸면 된다.
- 새 모델이 나왔다면 지금 설치된 버전이 그 아키텍처를 지원하는지부터 확인한다. config의 `model_type`과 프로세서를 보면 된다.

## 실습에서 배운 것 / 트러블슈팅
- **감정 분석 입문 실습 (LAB 08)**
  - 환경: Python 3.11.15, transformers 5.9.0, torch 2.11.0+cu128, RTX 5070
  - 공개 한국어 감정 분석 모델 하나로 돌린 결과
    - 명백한 긍정·부정은 잘 잡았다.
    - 질문이나 우려 표현, 사실 진술은 단어 단위로 보고 부정으로 분류했다.
    - sarcasm 발화에는 POSITIVE 0.97로 완전히 속았다.
  - 감정과 심박을 결합한 규칙 `sentiment == POSITIVE AND heart_rate >= 90`으로 의심 발화를 골라냈다.
    - 화자 A "네 좋아요"(심박 95)는 강요된 동의로 의심됐다.
    - 화자 B "아 정말요, 너무 좋네요"(심박 102)는 sarcasm으로 의심됐다.
    - 텍스트만 보면 둘 다 "동의"다. 심박을 붙이자 판단이 뒤집혔다.
  - 이 실습이 [[sarcasm-detection]]과 [[회의-음성-어조-분석-연구]]의 출발점이 됐다.
- **[[gemma-4]] 로드 (LAB 15·16)**
  - Transformers 5.9.0이 `Gemma4ForConditionalGeneration`을 인식하는지부터 확인했다.
  - `AutoProcessor.from_pretrained` 한 줄로 토크나이저, 오디오 특징 추출기, 이미지 프로세서를 묶은 `Gemma4Processor`가 로드된다.
  - `generate()` 출력에는 입력 토큰이 앞에 붙어 나온다. `input_len`만큼 잘라내고 생성된 부분만 디코딩한다.
- **v5.x API 변화 (LAB 28)**: `from_pretrained`의 dtype 인자가 `torch_dtype`에서 `dtype`으로 바뀌었다.
- **스트리밍 데이터 (LAB 19)**: `load_dataset("kresnik/zeroth_korean", split="test", streaming=True)`에 `cast_column("audio", Audio(decode=False))`를 걸었다. 디코딩은 `soundfile`로 직접 했다.
- **멀티모달 양자화 (LAB 16)**: 멀티모달 모델을 bitsandbytes로 양자화할 때는 오디오·비전 타워를 대상에서 빼야 한다(transformers 이슈 #45674). → [[quantization]]

## 관련
- [[transformer]] · [[gemma-4]] · [[quantization]] · [[asr]] · [[sarcasm-detection]] · [[wsl2-cuda-setup]] · [[회의-음성-어조-분석-연구]]
- 원글: [LAB 07. 기초를 다지자 (5)](https://velog.io/@xorms/LAB-%EA%B8%B0%EC%B4%88%EB%A5%BC-%EB%8B%A4%EC%A7%80%EC%9E%90-5)
- 원글: [LAB 08. 감정 분석 모델 실습](https://velog.io/@xorms/LAB-08.-%EA%B0%90%EC%A0%95-%EB%B6%84%EC%84%9D-%EB%AA%A8%EB%8D%B8-%EC%8B%A4%EC%8A%B5)
- 원글: [LAB 15. Gemma 4 E4B-it 첫 로드 테스트](https://velog.io/@xorms/LAB-Gemma-4-E4B-it-%EC%B2%AB-%EB%A1%9C%EB%93%9C-%ED%85%8C%EC%8A%A4%ED%8A%B8)
- 원글: [LAB 16. ARS 동작 테스트 - 오디오 타워 양자화 제외](https://velog.io/@xorms/LAB-16)
- 원글: [LAB 19. 한국어 ASR 환각 판정 지표 + baseline 진단](https://velog.io/@xorms/LAB-19)
