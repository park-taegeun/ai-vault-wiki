---
type: concept
modified: 2026-10-19
sources: [_private/raw/velog/졸업작품-기록/2026-04-07-졸업작품-기록-6.md, _private/raw/velog/졸업작품-기록/2026-04-11-졸업작품-기록10.md, _private/raw/velog/졸업작품-기록/2026-04-27-졸업작품-기록-13.md]
tags: [nginx, gunicorn, wsgi, 배포]
---

## 한 줄 정의
Nginx(리버스 프록시·SSL 처리) → Gunicorn(WSGI 서버) → Flask(WSGI 앱)로 이어지는 Python 웹 앱의 프로덕션 실행 구조다.

## 핵심 내용
- **프록시 두 종류**: 포워드 프록시는 클라이언트 앞에서 대신 요청을 보낸다(VPN과 비슷). 리버스 프록시는 서버 앞에서 요청을 받아 서버로 넘긴다. Nginx는 리버스 프록시다.
- **SSL Termination**: Nginx가 443 포트에서 HTTPS를 복호화하고 내부 포트(8000)로 HTTP 요청을 넘긴다. 암호화는 Nginx가 전담하므로 Gunicorn·Flask는 로직만 처리한다.
- **WSGI**: Nginx는 Flask 앱을 직접 실행하지 못한다. 둘 사이의 규약이 WSGI이고, Gunicorn이 WSGI 서버다.
- **Flask 내장 서버와의 차이**: 내장 서버는 싱글 스레드이고 에러가 나면 죽는 개발용이다. Gunicorn은 워커 프로세스 여러 개로 병렬 처리하고, 워커가 죽으면 새로 띄운다.

```
클라이언트(HTTPS) → Nginx :443 (SSL Termination) → localhost:8000 Gunicorn (워커 N개) → Flask 앱
```

## 언제 쓰나 (상황 예시)
- [[flask]] 앱을 외부에 HTTPS로 공개할 때. 인증서는 [[https-tls]] 참고.

## 실습에서 배운 것 / 트러블슈팅
- [[띵동]]은 [[aws-ec2]] 위에 이 구조를 쓰고 Gunicorn 워커를 2개로 설정할 계획이었다 (2026-04-07). 2026-04-08 발표 기준 구성은 AWS EC2 + Nginx + Gunicorn + Flask, Let's Encrypt SSL, venv + requirements.txt였다. 로컬 추정 라우팅 시간은 ~0.05초.
- **ML 모델 웜업**: TensorFlow 첫 추론은 그래프 컴파일 때문에 느리다 ([[yamnet]] 파이프라인 최대 150.1ms vs 이후 약 61ms). Gunicorn 워커 시작 시점에 더미 추론을 한 번 돌려 두면 운영 중에는 이 지연이 나오지 않는다.

## 관련
- [[flask]] · [[https-tls]] · [[aws-ec2]] · [[yamnet]] · [[구현-전-사전-테스트]] · [[vite]] · [[띵동]]
- [[jwt]] — CORS를 앱이 아니라 Nginx에서 검증한다는 Spring 실습 자료의 주석
- 원글: [졸업작품 기록 (6)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-6)
- 원글: [졸업작품 기록 (10)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D10)
- 원글: [졸업작품 기록 (13)](https://velog.io/@xorms/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88-%EA%B8%B0%EB%A1%9D-13)
