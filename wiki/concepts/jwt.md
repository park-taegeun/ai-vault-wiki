---
type: concept
modified: 2026-10-19
sources: [_private/raw/notion/Backend/Session/Week06 - Spring Security와 Server 2bdd8df03cab80b2b9d3c48711e706b2.md, _private/raw/notion/Backend/Session/Week09 - JSON Web Token 2bdd8df03cab80fdacd0e621df4c5070.md]
tags: [jwt, 인증, spring-security, 백엔드]
---

## 한 줄 정의
JWT(JSON Web Token)는 서버가 서명해 발급하는 토큰이다. 서버는 세션을 저장하지 않고, 요청에 실린 토큰의 서명과 만료만 검사해 사용자를 확인한다.

## 핵심 내용
멋쟁이사자처럼 13기 백엔드 세션(Week06 Spring Security, Week09 JWT) 배포 자료의 실습 코드를 구조 위주로 요약했다. 코드 원문은 옮기지 않았다.

### 인증 흐름 (로그인 → AT/RT 발급)
1. 클라이언트가 `POST /api/auths/login`으로 아이디·비밀번호를 보낸다.
2. 서비스가 사용자를 찾고, `AuthenticationManager`로 비밀번호를 검증한다.
3. `JwtProvider`가 Access Token(AT)과 Refresh Token(RT)을 만든다. RT에는 무작위 UUID를 토큰 ID로 넣고 사용자 엔티티에 저장한다.
4. 응답 본문에는 AT, 사용자 정보, AT 남은 만료 시간(ms)을 담는다. RT는 본문이 아니라 `Set-Cookie`로 보낸다.
5. 이후 요청은 `Authorization: Bearer <REDACTED>` 헤더에 AT를 실어 보낸다.

### 토큰 설정값

| 항목 | 값 |
|---|---|
| 서명 알고리즘 | HS256 |
| `spring.jwt.secret` | `<REDACTED>` |
| AT 만료 | 1800000 ms = 30분 |
| RT 만료 | 172800000 ms = 2일 |

- subject에는 사용자 아이디를 넣고, 필터는 subject로 사용자를 다시 불러온다. 라이브러리는 `io.jsonwebtoken`(jjwt)이다.

### RT를 HttpOnly 쿠키로 전달
- 쿠키 이름 `refreshToken`, `HttpOnly` 켬, `Path=/`.
- `Secure`는 주석 처리돼 있고 "HTTPS일 때만" 켜라고 적혀 있다. → [[https-tls]]

> [!note] 기록 간 차이
> 같은 Week09 자료 안에서 RT 만료는 2일(172800000 ms)인데, RT를 담는 쿠키의 `maxAge`는 `60 * 60 * 24 * 7`(7일, 주석 "예: 7일")이다. 어느 쪽에 맞춰야 하는지는 자료에 없다.

### STATELESS 세션과 필터 체인
- `SessionCreationPolicy.STATELESS`: 서버가 HTTP 세션을 만들지 않고, 매 요청을 토큰만으로 인증한다.
- `JwtAuthenticationFilter`(`OncePerRequestFilter`)가 요청마다 한 번 실행된다. `Authorization` 헤더에서 토큰을 꺼내 검증하고, 통과하면 `SecurityContextHolder`에 인증 정보를 넣는다. 만료·형식 오류·서명 불일치 등을 다른 에러 코드로 나누고, 실패하면 401이다.
- 이 필터는 기본 로그인 필터(`UsernamePasswordAuthenticationFilter`) 앞에 등록한다.

### 공통 응답과 예외 처리
- **BaseResponse**: 모든 API 응답을 `success`, `code`, `message`, `data` 네 필드로 통일한다. → [[rest-api]]
- **에러 코드 구조**: `BaseErrorCode` 인터페이스(code, message, HttpStatus)를 도메인별 enum(인증, JWT, 전역)이 구현하고, `CustomException`이 에러 코드 하나를 들고 던져진다.
- **GlobalExceptionHandler**(`@RestControllerAdvice`): `CustomException`은 그 에러 코드로, 입력 검증 실패는 필드별 메시지를 이어 400으로, 그 밖의 예외는 500으로 돌려준다.

### Spring Security 설정 요지
- **CORS**: 설정 소스를 연결한다. Week09 주석에는 "보통은 CORS 설정 활성화 하지 않음. 서버에서 NginX로 CORS 검증"이라고 적혀 있다. → [[nginx-gunicorn]]
- **CSRF 끔**, **STATELESS**, **BCrypt**(`BCryptPasswordEncoder`로 비밀번호 해시), HTTP Basic.
- Week06에서는 Swagger 경로(`/swagger-ui/**`, `/v3/api-docs/**` 등)를 `DEVELOPER` 역할로 제한하고, 계정은 설정 파일 값(`<REDACTED>`)으로 메모리에 하나 등록했다. → [[swagger]]

### 결정과 이유
- **CSRF 비활성화**: JWT 기반 REST API라서(자료 주석). 버린 것: 기본 CSRF 보호.
- **STATELESS**: JWT 기반이므로 무상태(자료 주석). 버린 것: 서버 세션.
- **RT를 응답 본문 대신 HttpOnly 쿠키로**: (이유 미기록. 자료에는 "HttpOnly + Secure"라는 주석만 있다)

## 언제 쓰나 (상황 예시)
- 프론트엔드와 분리된 REST API 서버에서 로그인 상태를 서버 세션 없이 유지할 때
- AT는 짧게(30분) 두고, 만료되면 RT로 다시 받는 구조가 필요할 때
- Swagger 문서를 개발자만 보게 하고 싶을 때(Week06 방식)

## 실습에서 배운 것 / 트러블슈팅
- 응답 형식(BaseResponse)과 에러 코드 체계를 먼저 고정해 두면 성공·검증 실패·인증 실패·서버 오류가 모두 같은 모양으로 내려온다.
- RT 쿠키의 `Secure`는 배포 환경이 HTTPS인지에 따라 켜고 끄는 설정이다.
- **실습 코드에서 확인된 결함 3가지** (원본 밖 근거로 검증, 2026-10-19)
  - 경로 규칙은 위에서부터 먼저 맞는 하나만 적용된다. Week06 코드처럼 `/api/**` permitAll이 앞에 있으면 뒤의 `/api/admin/**`(ADMIN), `/api/user/**`(인증 필요)는 적용되지 않는다. 구체적인 경로를 위에 둔다. ([Spring Security 문서](https://docs.spring.io/spring-security/reference/servlet/authorization/authorize-http-requests.html)) (정정)
  - Week09 필터는 `JwtException`과 `IllegalArgumentException`만 잡는데 검증 메서드는 `CustomException`을 던진다. 필터는 DispatcherServlet 밖에서 돌아서 `@RestControllerAdvice`에도 닿지 않는다. 그래서 의도한 401 대신 컨테이너 기본 오류가 날 수 있다. 필터 안에서 직접 응답을 쓰거나 AuthenticationEntryPoint로 넘겨야 한다. (정정)
  - Week09 코드는 Access Token의 `jti`에 username을 넣는다. `jti`는 토큰마다 고유한 ID여야 해서([RFC 7519 §4.1.7](https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.7)), 같은 사용자의 토큰이 모두 같은 값을 가지면 블랙리스트·재사용 방지에 쓸 수 없다. (정정)

## 관련
- [[spring-boot]] · [[rest-api]] · [[swagger]] · [[https-tls]] · [[nginx-gunicorn]]
