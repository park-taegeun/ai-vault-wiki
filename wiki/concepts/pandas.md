---
type: concept
modified: 2026-10-18
sources: [_private/raw/velog/AI_LAB/2026-05-19-LAB-03.-기초를-다지자.md, _private/raw/velog/AI_LAB/2026-05-20-LAB-03.-기초를-다지자2.md, _private/raw/velog/AI_LAB/2026-05-20-LAB-04.-기초를-다지자3.md]
tags: [pandas, python, 데이터처리, 시간정렬]
---

## 한 줄 정의
2차원 표(DataFrame)와 1차원 표(Series)를 라벨 기준으로 다루는 파이썬 데이터 처리 라이브러리.

## 핵심 내용
- **DataFrame / Series**: DataFrame은 행 라벨(index)과 열 라벨(columns)이 있는 2차원 표다. Series는 index만 있는 1차원 표다.
- **라벨 기반 연산**: 연산은 index·columns 라벨이 같은 칸끼리 이루어진다. 짝이 맞는 라벨이 없으면 결과는 NaN이 된다. 크기가 다른 대상끼리는 브로드캐스팅으로 계산한다.
- **boolean indexing**: 행이나 열 개수와 길이가 같은 True/False 배열로 원하는 행을 고른다.
  ```python
  s1 = df["수학"] > 90
  df.loc[s1]
  ```
- **시간 정렬 (`merge_asof`)**: 측정 속도가 서로 다른 신호를 같은 시간축에 맞춘다. 일반 `merge`는 time 값이 정확히 같은 행끼리만 합친다.
  ```python
  pd.merge_asof(text_df, heart_df, on='time', direction='nearest')
  ```
  `direction` 옵션은 세 가지다.
  - `'backward'`(기본값): 그 시각 이전의 가장 최근 값
  - `'forward'`: 그 시각 이후의 가장 가까운 값
  - `'nearest'`: 앞뒤를 가리지 않고 가장 가까운 값
- **`groupby` + `agg`**

  | 단계 | 코드 | 결과 |
  |---|---|---|
  | 기본 | `.groupby('A')['B'].mean()` | A별 B의 평균 |
  | 여러 통계 | `.groupby('A')['B'].agg(['mean','max','min','std','count'])` | A별 B의 여러 통계 |
  | 다중 컬럼 | `.groupby('A').agg({컬럼: 함수})` | 컬럼마다 다른 통계 |

## 언제 쓰나 (상황 예시)
- 회의 데이터에서 화자별 평균 심박, 감정 점수, 음량, 발화 횟수를 한 표로 묶은 화자별 프로필을 만들 때 (`groupby('speaker').agg({...})`)
- 발화마다 그 시각의 심박을 붙이는 것처럼 여러 모달리티 신호를 시간축으로 합칠 때 (`merge_asof`)

## 실습에서 배운 것 / 트러블슈팅
- **일반 `merge` 결과가 0행이었던 문제**
  - 상황: 텍스트 발화 시각(0.35, 1.27, 2.81, 3.42, 4.69초)과 심박(10Hz, 0.1초 간격 50개)을 `on='time'`으로 merge했더니 결과가 0행이었다. 시각이 정확히 일치하는 행이 없었기 때문이다.
  - 해결: `merge_asof(direction='nearest')`로 바꾸자 5행이 모두 매칭됐다. 실제 데이터는 시각이 딱 맞아떨어지지 않으므로 "충분히 가까우면 매칭"하는 방식이 필요하다.
- **실제 연구에서 예상되는 모달리티별 측정 속도**: 음성 16,000Hz, EEG 500Hz, 아이트래커 120Hz, 영상 30Hz, 심박 10Hz, 텍스트는 발화 단위로 약 1Hz다. 이 숫자는 작성자의 추정치다. 이번 실습은 텍스트와 심박 두 가지로 줄여서 연습했다.
- 랜덤 데이터는 `np.random.seed(42)`로 고정해 실행할 때마다 같은 결과가 나오게 했다. → [[reproducibility]]

## 관련
- [[회의-음성-어조-분석-연구]] · [[wsl2-cuda-setup]] · [[reproducibility]]
- [[sql]] — DataFrame merge와 같은 조인 개념
- 원글: [LAB 02. 기초를 다지자](https://velog.io/@xorms/LAB-03.-%EA%B8%B0%EC%B4%88%EB%A5%BC-%EB%8B%A4%EC%A7%80%EC%9E%90)
- 원글: [LAB 03. 기초를 다지자(2)](https://velog.io/@xorms/LAB-03.-%EA%B8%B0%EC%B4%88%EB%A5%BC-%EB%8B%A4%EC%A7%80%EC%9E%902)
- 원글: [LAB 04. 기초를 다지자(3)](https://velog.io/@xorms/LAB-04.-%EA%B8%B0%EC%B4%88%EB%A5%BC-%EB%8B%A4%EC%A7%80%EC%9E%903)
