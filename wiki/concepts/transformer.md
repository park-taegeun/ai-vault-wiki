---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/AI_LAB/2026-05-22-LAB-06.-기초를-다지자4.md, _private/raw/velog/AI_LAB/2026-05-22-LAB-기초를-다지자-5.md]
tags: [transformer, attention, encoder, decoder, bert, gpt]
---

## 한 줄 정의
문장을 순서대로 읽는 대신 전체를 한 번에 보고, 단어끼리의 관계를 attention으로 계산하는 모델 구조다. 2017년 논문 "Attention Is All You Need"에서 처음 나왔다.

## 핵심 내용
- **발전 흐름**
  - 1세대 RNN: 단어를 하나씩 순서대로 읽는다. 문장이 길어지면 앞부분을 잊고, 순서대로만 처리하니 병렬화가 어렵다.
  - 2세대 LSTM: 무엇을 기억하고 무엇을 잊을지 정하는 게이트를 붙였다. 하지만 여전히 순서대로 처리한다.
  - 3세대 Transformer: 문장 전체를 한 번에 본다. 병렬 처리가 되고, 긴 문맥을 다루며, 모델을 키울수록 성능이 오른다(스케일링).
- **Attention의 구성 요소**
  1. Self-Attention: 한 문장 안의 단어들이 서로를 참조한다.
  2. Multi-Head Attention: 여러 관점에서 동시에 참조한다.
  3. Positional Encoding: 단어의 순서 정보를 더한다.
  4. Feed-Forward Network: 단어마다 한 번 더 변환한다.
- **Encoder와 Decoder**
  - Encoder: 입력 전체를 한 번에 보고 각 단어 벡터의 의미를 찾는다. "이해"를 맡는다.
  - Decoder: 한 방향으로만 보면서 다음 단어를 하나씩 생성한다.
- **BERT와 GPT로 갈라짐 (2018)**
  - GPT (OpenAI, 2018.06): Decoder만 쓴다. 지금까지 나온 단어로 다음 단어를 맞히는 방식(CLM)으로 학습한다. 앞만 보기 때문에 글을 생성하는 데 강하다.
  - BERT (Google, 2018.10): Encoder만 쓴다. 문장의 일부 단어를 가리고 맞히는 방식(MLM)으로 학습한다. 앞뒤를 모두 보기 때문에 문장 이해에 강하다.
  - LLaMA-3: Meta의 오픈소스 LLM으로, Decoder 중심 구조다.

## 언제 쓰나 (상황 예시)
- 감정 분류처럼 문장을 이해해 라벨을 붙이는 작업에는 BERT 계열(DistilBERT, KoBERT, KcBERT)을 쓴다.
- 자유롭게 생성하거나 추론해야 하는 작업에는 Decoder LLM([[gemma-4]], LLaMA)을 쓴다.

## 실습에서 배운 것 / 트러블슈팅
- 감정 분석 실습에서 두 계열이 같은 발화를 다르게 읽었다.
  - BERT 계열 분류 모델은 표면 단어만 보고 판단해 sarcasm을 놓쳤다.
  - Decoder LLM은 같은 발화의 의도를 의심했다.
- 학습 목표가 라벨 예측이냐 다음 토큰 예측이냐에 따라 모델이 문장을 보는 깊이가 달라진다는 사례였다. → [[sarcasm-detection]]
- [[huggingface-transformers]]에서는 BERT, LLaMA-3, KcBERT 모두 같은 API로 불러온다.

## 관련
- [[huggingface-transformers]] · [[gemma-4]] · [[lora]] · [[sarcasm-detection]] · [[회의-음성-어조-분석-연구]]
- 원글: [LAB 06. 기초를 다지자(4)](https://velog.io/@xorms/LAB-06.-%EA%B8%B0%EC%B4%88%EB%A5%BC-%EB%8B%A4%EC%A7%80%EC%9E%904)
- 원글: [LAB 07. 기초를 다지자 (5)](https://velog.io/@xorms/LAB-%EA%B8%B0%EC%B4%88%EB%A5%BC-%EB%8B%A4%EC%A7%80%EC%9E%90-5)
