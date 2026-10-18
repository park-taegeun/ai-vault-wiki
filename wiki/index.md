---
title: AI-Vault 공개 위키
type: note
modified: 2026-10-18
tags: [index]
---
# 공개 위키 목차

> Claude가 `/ingest` 때마다 갱신합니다. 이 목차에는 `_private/` 페이지를 넣지 않습니다.

## concepts
- [[mcp]] — 모델이 외부 도구를 직접 호출하게 하는 프로토콜, stdio·HTTP 방식 비교 (2026-10-18)
- [[mcp-scope]] — MCP·플러그인·훅의 적용 범위(local/user/project)와 클라이언트별 등록 차이 (2026-10-18)
- [[mcp-combo]] — 여러 MCP를 한 프롬프트로 엮는 실습 모음 (2026-10-18)
- [[nested-agent]] — 메인 에이전트가 서브에이전트에게 병렬 위임하는 구조 (2026-10-18)
- [[pandas]] — DataFrame, merge_asof 시간 정렬, groupby 집계 (2026-10-18)
- [[wsl2-cuda-setup]] — WSL2 + CUDA 12.8 로컬 연구 환경, RTX 5070(sm_120)에서 막힌 부분 (2026-10-18)
- [[transformer]] — Attention, Encoder/Decoder, BERT·GPT 분기 (2026-10-18)
- [[huggingface-transformers]] — pipeline부터 모델 클래스까지, Gemma 4 로드와 v5 API 변화 (2026-10-18)
- [[quantization]] — NF4 4bit, 오디오 타워를 양자화에서 빼야 하는 이유, 양자화가 환각의 원인인지 확인한 실험 (2026-10-18)
- [[lora]] — 저랭크 어댑터로 파인튜닝, 붙이는 위치가 결과를 정한다 (2026-10-18)
- [[gemma-4]] — 멀티모달 Gemma 4 구조, 오디오 주입 방식, "측정기가 아니라 해석기" (2026-10-18)
- [[audio-tower]] — Gemma 4 오디오 인코더와 embed_audio 결합 지점, 발음 오인식 진단 (2026-10-18)
- [[asr]] — 한국어 ASR, WER/CER, 오디오 변조 실험 (2026-10-18)
- [[asr-hallucination]] — 짧은 발화가 부르는 LLM ASR 환각, audio-gap, 프롬프트·디코딩으로 억제한 결과 (2026-10-18)
- [[asr-fine-tuning]] — QLoRA 도메인 적응, 개선이 과생성 억제의 부산물이었던 이유 (2026-10-18)
- [[kconfspeech]] — AI Hub 한국어 회의 음성 데이터셋 구조와 평가 결과 (2026-10-18)
- [[sarcasm-detection]] — 비꼼·강요된 동의 탐지, LLM의 의심 편향과 사후 합리화 (2026-10-18)
- [[mfcc]] — 음색을 13개 계수로 압축한 음향 특징 (2026-10-18)
- [[f0-pitch]] — 목소리 높낮이, 자기상관 추출, 화자 신체를 재는 절대값 (2026-10-18)
- [[egemaps]] — 감정·어조 연구의 표준 88차원 특징 세트 (2026-10-18)
- [[speech-emotion-recognition]] — 음성 감정 인식, hand-crafted 4모델 LOSO 비교 (2026-10-18)
- [[korean-emotion-speech-datasets]] — 한국어 감정 음성 데이터셋 후보와 선정·전환 기준 (2026-10-18)
- [[embedding-probing]] — 선형 프로브로 내부 표현에 담긴 정보 확인하기 (2026-10-18)
- [[placebo-control]] — 가짜 벡터 대조군으로 학습 효과와 신호 기여 분리하기 (2026-10-18)
- [[reproducibility]] — 측정·학습·실전 코드 세 층위의 재현 확인 (2026-10-18)
- [[어조-모듈]] — 발화를 126차원 어조 벡터로 바꾸는 오디오 모듈 (2026-10-18)
- [[어조-모듈-층2]] — 화자 평소 대비 편차 층, 기준점 설계와 평소 신뢰도 (2026-10-18)
- [[음향-벡터-프롬프트-주입]] — 음향 수치를 자연어로 바꿔 프롬프트에 넣는 경로와 그 실패 (2026-10-18)
- [[표현-수준-융합]] — projection + soft token으로 벡터를 LLM 임베딩에 넣기 (2026-10-18)
- [[어조-성분-분해]] — 감정 수준 성분과 발화 개별 성분으로 나눈 어조 기여 (2026-10-18)
- [[어조-기여-평가-지표]] — 정답률·정보량·승률, 감정가 불일치 구간으로 어조 기여 재기 (2026-10-18)

## tools
- [[context7-mcp]] — 라이브러리 최신 공식 문서를 조회해 할루시네이션을 줄이는 MCP (2026-10-18)
- [[github-mcp]] — 이슈·브랜치·PR·머지를 자연어로 처리하는 MCP (2026-10-18)
- [[notion-mcp]] — OAuth로 붙는 Notion 공식 원격 MCP (2026-10-18)
- [[playwright-mcp]] — 실제 브라우저를 자연어로 조작하는 MCP (2026-10-18)
- [[supabase-mcp]] — 자연어로 스키마·CRUD·RLS까지 다루는 DB MCP (2026-10-18)
- [[sequential-thinking-mcp]] — 생각을 단계로 나눠 전개하게 하는 추론 MCP (2026-10-18)
- [[firecrawl-mcp]] — 웹 페이지를 정제된 마크다운으로 바꾸는 크롤링 MCP (2026-10-18)
- [[memory-mcp]] — Knowledge Graph로 세션을 넘는 기억을 저장하는 MCP (2026-10-18)
- [[slack-mcp]] — Bot Token으로 채널·메시지를 다루는 MCP (2026-10-18)
- [[scrapling-mcp]] — Cloudflare 봇 검사를 통과하는 파이썬 스크래퍼 MCP (2026-10-18)
- [[hwp-mcp]] — 맥에서 한컴 없이 HWP/HWPX를 읽고 양식을 채우는 MCP (2026-10-18)
- [[photocraft-mcp]] — 오픈소스 포토샵 클론을 조종해 카드뉴스를 찍어내는 MCP (2026-10-18)
- [[obsidian-local-rest-api]] — Obsidian 볼트를 Claude Desktop에 MCP로 연결하는 플러그인 (2026-10-18)
- [[ruflo]] — Claude Code 위 에이전트 스웜 메타 하네스, 검증 실험 결과 (2026-10-18)
- [[claude-code-setup]] — 레포에 맞는 자동화를 추천하는 공식 플러그인, 비밀값 이중 방어 (2026-10-18)
- [[claude-mem]] — hook으로 작업을 자동 기록하는 메모리 플러그인, 탐침 실험 결과 (2026-10-18)
- [[opensmile]] — eGeMAPS 88개 음향 특징을 뽑는 음성 신호 처리 도구 (2026-10-18)

## projects
- [[회의-음성-어조-분석-연구]] — 회의 발화의 숨은 의도를 음성 어조로 읽는 멀티모달 연구 허브, AI_LAB 시리즈 전체 흐름 (2026-10-18)
