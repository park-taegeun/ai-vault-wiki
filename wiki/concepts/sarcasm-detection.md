---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/AI_LAB/2026-05-22-LAB-08.-감정-분석-모델-실습.md, _private/raw/velog/AI_LAB/2026-05-26-LAB-10.-Sarcasm-탐지-실험1.md, _private/raw/velog/AI_LAB/2026-05-26-LAB-11.-Sarcasm-탐지-실험2.md, _private/raw/velog/AI_LAB/2026-05-27-LAB-12.-통제-실험.md, _private/raw/velog/AI_LAB/2026-05-27-LAB-13.-실데이터셋-찾기.md, _private/raw/velog/AI_LAB/2026-06-16-LAB-31.md, _private/raw/velog/AI_LAB/2026-06-17-LAB-32.-임베딩openSMILE-편차-비중복-검증.md]
tags: [sarcasm, zero-shot, few-shot, gemma-4, 의심편향]
---

## 한 줄 정의
겉으로는 긍정인데 실제로는 비꼬거나 마지못해 동의하는 발화를 찾아내는 문제다. 감정 분석 모델은 표면 단어에 속는다. LLM은 텍스트만 보고도 일부를 잡아내지만, 진심인 발화까지 의심하는 경향을 보였다.

## 핵심 내용
### 용어
- **Zero-shot**: 예시 없이 바로 묻는다. 모델이 가진 실력을 그대로 잰다.
- **Few-shot**: 예시를 몇 개 주고 묻는다. 예시에 실험자의 판단이 들어가고 모델이 그 판단을 따라 할 수 있다.
- 그래서 실험은 zero-shot으로 진행했다. (A) 텍스트만 준 경우와 (B) 텍스트에 심박을 더 준 경우를 비교했다.

### 출력 형식
자유 텍스트로 답하게 하면 매번 형식이 달라 집계할 수 없다. 그래서 아래 세 필드를 담은 JSON으로만 답하게 했다.

| 필드 | 뜻 |
|---|---|
| `intent` | `SINCERE`, `SARCASTIC`, `FORCED_AGREEMENT`, `UNCERTAIN` 중 하나 |
| `confidence` | 0~1 |
| `evidence` | 판단 근거 한 문장. 텍스트 단서로 판단했는지 추측했는지를 가르는 핵심 필드 |

### 실험 ([[gemma-4]] E4B-it, NF4)
- `build_prompt()`는 심박 값이 있으면 `화자의 심박수: N bpm (평소 70 기준)`을 덧붙인다.
- `ask_gemma()`는 `generate(max_new_tokens=200, do_sample=False)`로 greedy 생성을 한다. 응답에서 정규식 `\{.*\}`로 JSON 부분만 뽑아 파싱하고, 실패하면 `PARSE_ERROR`로 처리한다. 원문은 `_raw`에 보관한다.
- 데이터는 직접 만든 회의 발화 4개다.

| id | 발화 | 심박 | KoBERT | 가설 정답 |
|---|---|---|---|---|
| suspect_1 (화자 A) | "네 좋아요." | 95 | POSITIVE 0.884 | FORCED_AGREEMENT |
| suspect_2 (화자 B) | "아 정말요, 너무 좋네요." | 102 | POSITIVE 0.970 | SARCASTIC |
| control_1 (화자 C) | "괜찮아요, 충분히 가능합니다." | 68 | POSITIVE 0.962 | SINCERE |
| control_2 (화자 D) | "그럼 그렇게 진행합시다." | 85 | POSITIVE 0.862 | SINCERE |

### 결과
- **실험 A (텍스트만)**
  - KoBERT는 의심 발화 2개 중 0개를 맞혔고, Gemma는 2개를 모두 맞혔다.
  - 하지만 Gemma는 control_1까지 FORCED_AGREEMENT로 판정했다. 근거는 "맥락 부족"이었다. 오탐(false positive)이다.
- **실험 B (텍스트 + 심박)**
  - 라벨 분포가 A와 완전히 같았다. 바뀐 것은 근거뿐이다.
  - control_1의 심박 68(정상 범위)을 "평소보다 낮아 확신이 없다"로 거꾸로 해석해서 여전히 의심했다.
- **통제 실험**
  - 같은 발화에 심박 50, 68, 110을 각각 넣어 6번 돌렸다.
  - 세 값 모두에서 답이 같았다. 심박의 방향과 상관없이 같은 결론이 나왔다. → [[placebo-control]]

### 해석
- **의심 편향**: 맥락 없이 발화 하나만 주면 Gemma는 과하게 의심한다.
- **사후 합리화 (motivated reasoning)**: 텍스트만 보고 내린 1차 판단이 결론을 정한다. 심박은 그 결론을 정당화하는 근거로만 쓰인다.
- 정리하면 표면 모델은 위험 발화를 놓치고(false negative), 생성 모델은 진심을 의심한다(false positive).
- **결론**: 부가 신호를 프롬프트 텍스트로 붙이는 것만으로는 멀티모달 이점이 생기지 않는다. 그래서 신호를 표현(representation) 수준에서 통합해야 한다는 가설이 나왔다. → [[음향-벡터-프롬프트-주입]], [[표현-수준-융합]]

### 기준은 화자 자신의 평소다 (LAB 31·32)
- 같은 "네, 좋아요"라도 음량이 평소보다 낮고 피치가 처지면 강요된 동의의 신호가 된다.
- 늘 활발한 사람이 납작하게 말하면 신호가 되지만, 원래 무뚝뚝한 사람이면 아무 의미가 없다.
- 그래서 몇 Hz인지 같은 절댓값이 아니라 그 화자의 평소에서 얼마나 벗어났는지를 재야 한다. 이 생각이 [[어조-모듈-층2]]의 출발점이 됐다.
- 다만 "평소에서 벗어남 = 비꼼"은 따로 증명해야 한다. 의도 라벨이 없는 데이터로는 답할 수 없다. → [[embedding-probing]]

### 실데이터셋 (LAB 13)
직접 만든 데이터 4개로는 한계가 있어서 공개 데이터셋을 조사했다.

| 데이터셋 | 규모 | 모달리티 | 검증할 수 있는 것 |
|---|---|---|---|
| KoCoSa | 12,824 | 텍스트 | 텍스트만으로 sarcasm을 잡는가 |
| MUStARD (ACL 2019) | 690 클립 | 영상·오디오·텍스트(영어) | 멀티모달 신호를 통합하는가 |

- KoCoSa의 `label`, `sarcasm_explanation` 필드는 기존 `expected_intent`, `evidence` 구조와 맞는다. 그래서 데이터 소스만 바꾸면 기존 실험 코드를 그대로 쓸 수 있다.
- 전략은 이중 트랙으로 정했다. KoCoSa로 텍스트 쪽 가설을 먼저 검증하고, 그동안 MUStARD를 검토하며 AI Hub 한국어 멀티모달 데이터를 신청한다.

## 언제 쓰나 (상황 예시)
- 회의 발화에서 강요된 동의나 반어를 찾아야 할 때
- LLM이 프롬프트에 붙인 부가 신호를 실제로 쓰는지 확인할 때. 부가 신호만 바꾸고 답이 달라지는지 본다.

## 실습에서 배운 것 / 트러블슈팅
- Gemma가 JSON을 코드블록으로 감싸서 돌려줄 때가 있다. 정규식으로 중괄호 구간만 뽑아 파싱했다.
- 표본이 작을 때는 한 번의 결과로 편향을 확정하지 않았다. 대조군을 추가하고, 같은 발화에 다른 심박을 넣는 통제 실험을 하는 순서로 범위를 좁혀 갔다.
- KoBERT가 나쁜 모델이어서 실패한 것은 아니다. 감정 라벨 예측을 학습 목표로 한 분류 모델이라 발화의 의도(화행)를 보지 못한다. → [[transformer]]

## 관련
- [[gemma-4]] · [[huggingface-transformers]] · [[transformer]] · [[placebo-control]] · [[opensmile]] · [[embedding-probing]] · [[어조-모듈-층2]] · [[음향-벡터-프롬프트-주입]] · [[표현-수준-융합]] · [[회의-음성-어조-분석-연구]]
- 원글: [LAB 08. 감정 분석 모델 실습](https://velog.io/@xorms/LAB-08.-%EA%B0%90%EC%A0%95-%EB%B6%84%EC%84%9D-%EB%AA%A8%EB%8D%B8-%EC%8B%A4%EC%8A%B5)
- 원글: [LAB 10. Sarcasm 탐지 실험(1)](https://velog.io/@xorms/LAB-10.-Sarcasm-%ED%83%90%EC%A7%80-%EC%8B%A4%ED%97%981)
- 원글: [LAB 11. Sarcasm 탐지 실험(2)](https://velog.io/@xorms/LAB-11.-Sarcasm-%ED%83%90%EC%A7%80-%EC%8B%A4%ED%97%982)
- 원글: [LAB 12. 통제 실험](https://velog.io/@xorms/LAB-12.-%ED%86%B5%EC%A0%9C-%EC%8B%A4%ED%97%98)
- 원글: [LAB 13. 실데이터셋 찾기](https://velog.io/@xorms/LAB-13.-%EC%8B%A4%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%85%8B-%EC%B0%BE%EA%B8%B0)
- 원글: [LAB 31. Gemma4 음성특징 스모크 + openSMILE 비교](https://velog.io/@xorms/LAB-31)
