---
type: concept
modified: 2026-10-19
sources: [_private/raw/velog/졸업작품-기록/2026-04-30-졸업작품-기록-19.md, _private/raw/velog/졸업작품-기록/2026-05-06-졸업작품-기록-22.md, _private/raw/velog/졸업작품-기록/2026-05-07-졸업작품-기록-23.md, _private/raw/velog/졸업작품-기록/2026-05-08-졸업작품-기록-25.md, _private/raw/velog/졸업작품-기록/2026-05-09-졸업작품-기록-27.md, _private/raw/velog/졸업작품-기록/2026-05-11-졸업작품-기록-29.md, _private/raw/velog/졸업작품-기록/2026-05-11-졸업작품-기록-30.md, _private/raw/velog/졸업작품-기록/2026-05-12-졸업작품-기록-31.md, _private/raw/velog/졸업작품-기록/2026-06-23-졸업작품-기록-36.md, _private/raw/velog/졸업작품-기록/2026-06-23-졸업작품-기록-37.md, _private/raw/velog/졸업작품-기록/2026-09-09-졸업작품-기록-59.md, _private/raw/velog/졸업작품-기록/2026-10-07-졸업작품-기록-64.md]
tags: [임베디드, esp32, 마이크로컨트롤러, 카메라, i2s]
---

## 한 줄 정의
Wi-Fi를 내장한 Espressif의 듀얼코어 마이크로컨트롤러다. [[띵동]]은 카메라가 붙은 Seeed XIAO ESP32-S3 Sense를 현관 디바이스로 쓴다.

## 핵심 내용
- **메모리**: user-available SRAM 약 320KB(빌드 리포트 기준 327,680 bytes), Flash 앱 영역 3,342,336 bytes, PSRAM 8MB.
- 듀얼 코어(Core 0/1)에 FreeRTOS 태스크를 핀 고정(`xTaskCreatePinnedToCore()`)하고 priority로 나눈다.
- **카메라와 I2S 마이크를 동시에 쓸 수 있나 (2026-04-30)**: 가능하다. ESP-IDF 공식 esp32-camera 드라이버 코드를 보면 구형과 S3가 다르다.
  - 구형 ESP32(`target/esp32/ll_cam.c`): 카메라가 I2S0를 카메라 모드로 점유한다(`I2S0.conf2.camera_en = 1`). I2S 마이크와 같이 쓰기 어렵다.
  - ESP32-S3(`target/esp32s3/ll_cam.c`): 카메라가 LCD_CAM 페리페럴 + GDMA를 쓴다. I2S0와 I2S1이 모두 비어 있다.
  - 보조 증거로 실제 작동 펌웨어 5건과, 포럼에서 "S3는 GDMA를 써서 PDM 마이크와 동시 사용 가능"이라고 글쓴이가 스스로 정정한 글을 확인했다.

> [!note] 정정
> S3 카메라는 I2S가 아니라 LCD_CAM + GDMA를 쓴다(기록 19, 기록 22 본문). 기록 22의 핀 검증 줄에는 "I2S0(카메라) ↔ I2S1(INMP441) 페리페럴 분리"라고 적혀 있었다. 같은 글 본문의 "I2S 페리페럴을 카메라가 점유하지 않는다"와 기록 19를 근거로 정정했다 (정정).

## 언제 쓰나 (상황 예시)
- 카메라·마이크·거리 센서·Wi-Fi를 한 보드에 몰아넣는 저가 IoT 디바이스.
- 구형 ESP32 자료를 S3에 그대로 적용하기 전에, 페리페럴 구조가 바뀌었는지 드라이버 코드로 확인할 때.
- 부품 도착 전에 env별 단독 더미 코드를 컴파일만 통과시켜 메모리 수치를 미리 모을 때 → [[구현-전-사전-테스트]]

## 실습에서 배운 것 / 트러블슈팅
- **카메라는 OV2640이 아니라 OV3660 (2026-05-07)**: 계획은 OV2640이었는데, 구매한 XIAO ESP32-S3 Sense Pre-Soldered(23,870원)에는 신형 OV3660이 달려 있었다. 기존 멀티코어 사례 대부분이 OV2640 기준이라 다시 조사했다. 부품 판매 페이지의 모델명은 구매 전에 확인한다.
- **INMP441 + 카메라 PoC 함정 3가지**
  1. INMP441 power-up 노이즈 약 250ms: 처음 12~14개 DMA 버퍼를 버린다. datasheet의 "VDD 인가 후 2^18 clock cycles"를 16kHz × 64 = 1.024MHz BCLK로 계산하면 256ms라 코드의 250ms 상수와 맞았다.
  2. 핀 충돌: D2(GPIO3)가 SD 카드 CS와 겹친다.
  3. 멀티코어 분리: 카메라 + 마이크 + 기타를 코어별로 나눈다. 잠정안은 Core 0 = micTask(p4) + tofTask(p3), Core 1 = cameraTask(p4) + wifiTask(p3).
- **카메라 설정**: `xclk_freq_hz = 20000000`(안전값), `fb_count = 2`, `fb_location = CAMERA_FB_IN_PSRAM`, `grab_mode = CAMERA_GRAB_LATEST`, `jpeg_quality = 12`, `PIXFORMAT_JPEG`/`FRAMESIZE_QVGA`, `esp_camera_fb_return()` 뒤 `vTaskDelay(pdMS_TO_TICKS(30))`(JPEG timeout 회피).
- **카메라 더미 — Version A/B (2026-05-09)**: A는 `cameraTask` 하나가 fb_get → 처리 → fb_return, B는 `writerTask`를 분리해 fb_get 블로킹을 격리한다. 정답을 정하지 않고 두 벌을 짜 두고 실측으로 비교하기로 했다. 공개 글의 함정 6개와 대조했는데, 처음엔 "함정 4개"로 잘못 알고 진행했다 → [[ai-산출물-검증]]
- **Wi-Fi + HTTPS 더미 (2026-05-08)**: WPA2-Enterprise(802.1X)는 호환성 리스크가 커서 포기하고 WPA2-Personal로 통일했다. 런타임 SSID fallback(PRIMARY → FALLBACK)으로 환경을 바꿀 때 코드 수정을 없앴다. 재연결은 지수 백오프(base 1s × 2^retry, 최대 5회). HTTPS는 → [[https-tls]]
- **마이크 I2S (2026-05-10)**: INMP441 핀 SCK = GPIO 2, WS = GPIO 3, SD = GPIO 7, L/R = GND. ESP-IDF 5.x 권장 `driver/i2s_std.h`가 패키지에 없어 legacy `driver/i2s.h`로 갔다 → [[platformio]]
- **정적 메모리 예산 — delta sum (2026-05-12)**: env별 단독 빌드 수치는 각각 베이스라인을 포함하므로 그냥 더하면 베이스라인이 4번 잡힌다. 베이스라인 하나에 페리페럴별 증가분만 더한다.

| env | RAM | Flash | RAM delta | Flash delta |
|---|---|---|---|---|
| baseline (5/7) | 5.6% | 7.6% | — | — |
| WiFi+HTTPS | 13.8% | 25.8% | +8.2pp | +18.2pp |
| camera_v2 | 7.0% | 9.4% | +1.4pp | +1.8pp |
| mic_dummy | 8.1% | 8.1% | +2.5pp | +0.5pp |
| tof_dummy | 6.1% | 11.1% | +0.5pp | +3.5pp |

  - 결과: RAM 18.2%(약 59,640 bytes), Flash 31.6%(약 1,056,178 bytes). 단순 합산이었다면 RAM 35.0% / Flash 54.4%로 과대평가했을 것이다.
  - Wi-Fi가 압도적이었다(esp_wifi + lwIP + wpa_supplicant + mbedtls + HTTPClient + ArduinoJson으로 Flash 약 608KB). ToF Flash 117KB 중 약 84KB는 센서 펌웨어 이미지다 → [[vl53l5cx]]
  - PSRAM은 카메라 frame buffer만 쓴다(약 50KB, 8MB의 0.6%). frame buffer를 PSRAM에 두는 것이 SRAM 압박을 줄이는 핵심이다.
- **Plan B 트리거 정량화**: 일반론 임계값 대신 320KB SRAM, 동적 heap peak, TLS handshake 때 약 80KB 추가 소비를 반영해 다시 정했다.

| Stage | 조건 | 대응 |
|---|---|---|
| 1 알람 | 정적 SRAM ≥25% 또는 Flash ≥40% | `ESP.getMinFreeHeap()` 동적 측정 |
| 2 최적화 | SRAM ≥35% 또는 Flash ≥60% | DMA buffer 축소, ToF FW를 PSRAM으로, Wi-Fi sdkconfig minimal |
| 3 Plan B | SRAM ≥50% 또는 Flash ≥75% | 카메라 QVGA→CIF, ToF 8x8→4x4, Wi-Fi→ESP-NOW |

  18.2% / 31.6%로 어느 Stage도 발동하지 않았다. 정적 예산이라 통합 후 동적 heap 추적이 따로 필요하다.
- **첫 실물 부팅 (2026-06-22)**
  - **XIAO ESP32-S3는 내장 안테나가 없다(IPEX 전용)**: 두 SSID가 모두 timeout이었다. 두 SSID가 동시에 실패하는 건 RF 수신 자체가 안 되는 징후라 하드웨어를 먼저 의심했다.
  - **Sense 확장보드가 IPEX 커넥터를 덮는다**: 카메라 확장보드 분리 → u.FL 안테나를 한쪽 가장자리부터 걸치고 반대쪽을 눌러 "딸깍" → 확장보드 재결합. 데이터시트만으로는 모르는 실물 함정이다.
  - 안테나 장착 후 RSSI -53dBm, IP 할당 0.7초, `POST /api/v1/detect → 200 OK` → [[flask]]
  - 카메라: 센서 PID `0x3660` → OV3660 확정, PSRAM 8MB OCTAL, QVGA JPEG 연속 캡처 정상.
- **PID 비교 잘림 버그 (PR #4)**: `sensorIdToName()`이 `case 0x36:`으로 비교해 실제 PID `0x3660`과 매칭에 실패했다. 같은 비교를 쓰는 dark-image 보정 분기도 안 걸리고 있었다. 캡처는 정상이라 눈에 안 띄는 잠복 버그였다. `grep`으로 비교 지점 2곳을 찾아 `OV3660_PID` 매크로로 바꿨다. 센서 ID 비교는 매직 넘버 대신 매크로로 한다.
- **마이크 링 버퍼 (2026-09-09)**: 최근 2.048초를 항상 들고 있는 구조다. 메모리가 계산만큼 줄었고 118초 동안 누락 0회였다 → [[onset-detection]]
- **"출력이 안 뜸"과 "멈춤"은 다른 사건 (2026-10-07)**: 두 번째 전송 뒤 기기 화면에 결과 줄이 안 떴다. 서버-기기 열린 연결 0건으로 멈춤이 아님을 확인했고, 다른 키를 누르자 밀린 결과가 한꺼번에 나왔다. 출력만 USB 쪽에 묶여 있었다(원인은 추정). 이후 판정은 화면이 아니라 서버 기록·연결 상태로 한다.

## 관련
- [[vl53l5cx]] · [[i2c]] · [[platformio]] · [[clangd]] · [[https-tls]] · [[onset-detection]] · [[idempotency-key]] · [[2단계-알림]] · [[구현-전-사전-테스트]] · [[ai-산출물-검증]] · [[http-timeout]] · [[마이크-튐-판별]] · [[띵동]]
- 원글: [졸업작품 기록 (19)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-19)
- 원글: [졸업작품 기록 (22)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-22)
- 원글: [졸업작품 기록 (31)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-31)
- 원글: [졸업작품 기록 (36)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-36)
- 원글: [졸업작품 기록 (37)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-37)
