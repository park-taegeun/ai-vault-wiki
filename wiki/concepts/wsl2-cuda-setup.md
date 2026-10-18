---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/AI_LAB/2026-05-21-LAB-04.-window-환경-셋업.md]
tags: [wsl2, cuda, pytorch, setup, windows]
---

## 한 줄 정의
윈도우 데스크탑에 WSL2(Ubuntu), VS Code, conda, CUDA 호환 PyTorch를 설치해 로컬 AI 연구 환경을 만드는 방법.

## 핵심 내용
- **WSL2를 쓰는 이유**
  - AI 라이브러리는 대부분 리눅스를 기준으로 만들어져 있다.
  - WSL2는 윈도우 안에서 실제 리눅스를 돌리면서도 가상머신보다 가볍다.
  - NVIDIA 드라이버는 윈도우에만 설치하면 WSL2가 그대로 인식한다.
- **VS Code를 쓰는 이유**
  - 무료이고 확장 기능이 강력하다.
  - 나중에 서버에 SSH로 붙을 때도 같은 편집 환경을 그대로 쓸 수 있다.
- **구성**
  - Windows 11: 바탕 운영체제
  - WSL2 + Ubuntu 22.04: 실제 작업 환경(git, Python, conda)
  - VS Code: 윈도우에 설치하고 WSL에 원격으로 접속
- **셋업 순서**
  1. PowerShell에서 `wsl --install -d Ubuntu-22.04`
  2. `build-essential git curl wget` 설치
  3. VS Code와 WSL 확장 설치
  4. git 설정, SSH 키를 만들어 GitHub에 등록
  5. Miniconda 설치, conda 환경 생성
  6. PyTorch 설치, GPU 인식 확인
  7. 핵심 라이브러리 설치
  8. Jupyter 커널 등록
- **핵심 라이브러리**

  | 용도 | 라이브러리 |
  |---|---|
  | 데이터 | numpy, pandas, scikit-learn |
  | 모델 | transformers, datasets ([[huggingface-transformers]]) |
  | 큰 모델 학습 (VRAM 12GB) | peft, bitsandbytes ([[lora]], [[quantization]]) |
  | 비전 | timm, opencv, albumentations |
  | 실험 추적 | wandb |

## 언제 쓰나 (상황 예시)
- **이럴 때 쓴다**: 윈도우 PC에 GPU가 있고, 코랩 대신 로컬에서 개발하고 싶을 때.
- **코랩보다 나은 점**
  - 세션이 끊기지 않는다. 코랩은 12시간 제한, 90분 idle 제한이 있다.
  - 디버거와 git을 갖춘 IDE를 그대로 쓸 수 있다.
  - 데이터와 모델이 지워지지 않고 남는다.
- **한계**: A100/H100급 GPU가 필요한 큰 학습은 서버에서 해야 한다.

## 실습에서 배운 것 / 트러블슈팅
- 환경: NVIDIA RTX 5070(VRAM 12GB), RAM 32GB.
- **RTX 5070(Blackwell, sm_120) 호환 문제**
  - 증상: PyTorch 공식 페이지 기본 안내(CUDA 12.1/12.6 빌드)나 `pip install torch`로 설치하면 아래 에러가 난다.
    ```
    NVIDIA GeForce RTX 5070 with CUDA capability sm_120 is not compatible with the current PyTorch installation.
    ```
  - 해결: CUDA 12.8 빌드를 명시해서 설치한다.
    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
    ```
  - 확인 결과: `PyTorch: 2.11.0+cu128`, `CUDA available: True`, `Compute capability: (12, 0)`.

## 관련
- [[회의-음성-어조-분석-연구]] · [[pandas]] · [[huggingface-transformers]] · [[lora]] · [[quantization]]
- 원글: [LAB 05. window 환경 셋업](https://velog.io/@xorms/LAB-04.-window-%ED%99%98%EA%B2%BD-%EC%85%8B%EC%97%85)
