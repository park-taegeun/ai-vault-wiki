---
type: tool
modified: 2026-10-18
sources: [_private/raw/velog/졸업작품-기록/2026-05-07-졸업작품-기록-23.md, _private/raw/velog/졸업작품-기록/2026-05-09-졸업작품-기록-27.md, _private/raw/velog/졸업작품-기록/2026-05-11-졸업작품-기록-29.md, _private/raw/velog/졸업작품-기록/2026-05-11-졸업작품-기록-30.md, _private/raw/velog/졸업작품-기록/2026-06-23-졸업작품-기록-36.md, _private/raw/velog/졸업작품-기록/2026-06-23-졸업작품-기록-37.md]
tags: [임베디드, 빌드도구, esp32, arduino]
---

## 한 줄 정의
`platformio.ini` 하나로 보드·프레임워크·라이브러리·빌드 환경(env)을 관리하는 임베디드 빌드 도구다.

## 핵심 내용
- env를 여러 개 두고 env마다 컴파일 대상 소스를 고를 수 있다(`build_src_filter`). 빌드가 끝나면 RAM/Flash 사용률을 출력한다.
- 라이브러리는 `lib_deps`에 등록한다(git URL도 가능). 프레임워크 패키지는 `~/.platformio/packages/` 아래에 설치된다.
- [[띵동]] PoC 환경 (2026-05-07):
  ```ini
  [env:poc]
  platform = espressif32
  board = seeed_xiao_esp32s3
  framework = arduino
  monitor_speed = 115200
  upload_speed = 921600

  build_flags =
    -DCAMERA_MODEL_XIAO_ESP32S3
    -DBOARD_HAS_PSRAM
    -mfix-esp32-psram-cache-issue

  lib_deps =
    sparkfun/SparkFun VL53L5CX Arduino Library
    https://github.com/adafruit/Adafruit_VL53L5.git
  ```
  - `-mfix-esp32-psram-cache-issue`: PSRAM cache 이슈 대응 → [[esp32-s3]]
  - Adafruit 라이브러리는 [[vl53l5cx]] 폴백용으로 미리 넣어 뒀다.
- 첫 컴파일: SUCCESS, 빌드 14.25초, RAM 5.6%(18,404 / 327,680 bytes), Flash 7.6%(253,821 / 3,342,336 bytes). `espressif32@7.0.0`, `framework-arduinoespressif32@3.20017.241212`(Arduino-ESP32 core 3.x), SparkFun VL53L5CX 1.0.3.

## 언제 쓰나 (상황 예시)
- ESP32 같은 보드에서 Arduino 프레임워크를 쓰되, 라이브러리 버전과 빌드 플래그를 파일로 고정하고 싶을 때.
- 부품별 단독 테스트를 env로 나눠 각각 컴파일·메모리 측정할 때 (`camera_v1`, `mic_dummy`, `tof_dummy` 등).

## 실습에서 배운 것 / 트러블슈팅
- `adafruit/Adafruit_VL53L5`는 PlatformIO Registry에 없어서 이름으로 넣으면 컴파일이 실패했다. `lib_deps`에 GitHub URL을 직접 적어 해결했다.
- 폴백 라이브러리를 같이 넣어도 dead code elimination으로 실제 쓰는 쪽만 링크된다.
- **단독 테스트 컨벤션**: 별도 디렉터리가 아니라 `firmware/src/`에 두고 `build_src_filter`로 env별로 격리한다. 위임 프롬프트가 `firmware/dummy_tests/camera_dummy/` 구조를 가정했다가 실제 커밋과 달라 바로잡았다 → [[ai-산출물-검증]]
- **공식 문서와 실제 패키지가 다를 수 있다**: ESP-IDF 5.x 권장 `driver/i2s_std.h`가 arduino-esp32 v3.20017 패키지에 없어서 fatal error가 났다. 헤더 존재를 직접 확인했다.
  ```bash
  find ~/.platformio/packages/framework-arduinoespressif32/tools/sdk/esp32s3/include/driver/include/driver/
  ```
  `i2s.h`만 있었다. wrapper SDK는 upstream 변경을 즉시 반영하지 않는다. 이후 4단계 확인으로 굳혔다: ① 공식 권장 ② 실제 패키지 헤더 노출 ③ 컴파일 ④ 런타임.
- `compile_commands.json`은 로컬 종속이라 `.gitignore`에 넣는다 → [[clangd]]
- **pio CLI가 통째로 사라짐 (2026-06-22)**: 패키지 캐시는 멀쩡한데 CLI venv만 없었다. 5월에 venv를 `/tmp/pio-venv`에 깔았고 macOS가 재부팅 때 `/tmp`를 비운 것이다. 결정 문서에는 그 경로가 적혀 있었지만 한 달 사이 현실과 어긋났다. 공식 installer로 표준 위치 `~/.platformio/penv`에 재설치했고, 캐시가 있어 재다운로드는 없었다 → [[single-source-of-truth]]
- **`build_src_filter` blacklist 잠복 회귀 (PR #4)**
  - `env:poc`를 빌드하자 `multiple definition of 'setup()'` / `'loop()'` 링커 에러가 났다. `env:poc`는 `+<*>`로 `src/` 전체를 넣고 카메라 파일만 빼는 blacklist였다.
  - 5/8 "컴파일 SUCCESS" 때 `src/`에는 `main.cpp` 하나뿐이었다. 5/10 `mic_test.cpp`, 5/11 `tof_test.cpp`가 추가된 뒤 poc를 한 번도 재빌드하지 않아 한 달간 잠복했다.
  - 부팅 당일("코드 0 수정" 규율)은 파일을 건드리지 않고 환경변수로 우회했다: `PLATFORMIO_BUILD_SRC_FILTER="-<*> +<main.cpp>" pio run -e poc -t upload`
  - PR #4에서 `build_src_filter = -<*> +<main.cpp>`로 영구 수정했다. RAM 13.8% / Flash 25.8%로 5/8 원본 poc footprint와 정확히 일치해 원래 상태 복구를 수치로 확인했다. "모든 env는 `-<*>` 먼저"로 규칙을 명문화했다.
  - blacklist는 "지금 있는 파일 기준"이라 파일이 추가될 때마다 제외 목록도 고쳐야 한다. whitelist는 명시하지 않으면 아무것도 안 들어와 [[monorepo]] 구조에서 안전하다.

> [!warning] 모순
> 기록 36은 5월 시점 `env:poc`를 `build_src_filter = +<*> -<camera_test_v1.cpp>`로, 기록 37은 `+<*> -<camera_test_v1.cpp> -<camera_common.cpp>`로 적었다. 제외 목록에 `camera_common.cpp`가 있었는지 확인 필요 (blacklist였다는 결론은 같다).

## 관련
- [[esp32-s3]] · [[vl53l5cx]] · [[clangd]] · [[monorepo]] · [[single-source-of-truth]] · [[ai-산출물-검증]] · [[reproducibility]] · [[띵동]]
- 원글: [졸업작품 기록 (23)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-23)
- 원글: [졸업작품 기록 (29)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-29)
- 원글: [졸업작품 기록 (36)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-36)
- 원글: [졸업작품 기록 (37)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-37)
