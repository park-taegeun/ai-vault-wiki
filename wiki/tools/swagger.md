---
type: tool
modified: 2026-10-19
sources: [_private/raw/notion/Backend/세션 정리/3주차 - API 명세의 이해와 Annotation/실습/Swagger 305d8df03cab80c7a474d0760d243ba6.md, _private/raw/notion/Backend/세션 정리/3주차 - API 명세의 이해와 Annotation/실습/Swagger Controller 305d8df03cab806389c5c8dc0346784d.md, _private/raw/notion/Backend/과제/3주차 - Swagger 309d8df03cab8041875cea50d1893d1e.md, _private/raw/notion/Backend/세션 정리/4주차 - Entity, Controller, Swagger 알아보기 30bd8df03cab80e0b5cedd9827abda36.md, _private/raw/notion/Backend/세션 정리/4주차 - Entity, Controller, Swagger 알아보기/실습 30bd8df03cab806dabc4fc1d4fa8452d.md]
tags: [spring, api-문서, openapi, springdoc, 멋쟁이사자처럼]
---

## 한 줄 정의
Spring 프로젝트의 컨트롤러를 읽어 API 문서 화면을 자동으로 만들어 주는 도구다. [[spring-boot]]에서는 springdoc-openapi 라이브러리로 붙인다. 멋쟁이사자처럼 13기 백엔드 트랙 3·4주차에 실습했다.

## 핵심 내용
### 필요한 것 세 가지: 의존성, config, controller
1. **의존성**: `build.gradle`의 `dependencies`에 springdoc을 넣고 Gradle 동기화를 누른다. 실습에서 쓴 버전은 2.8.1이다.
   ```gradle
   implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:2.8.1'
   implementation 'org.springdoc:springdoc-openapi-starter-webmvc-api:2.8.1'
   ```
2. **config**: 문서의 틀(제목·버전·서버·인증 방식·그룹)을 정하는 설정 클래스다.
3. **controller**: 문서에 실제로 채워질 API다. Swagger는 `@RestController`를 찾고 그 안의 `@GetMapping`·`@PostMapping` 같은 매핑을 읽어 문서를 만든다. 그래서 **컨트롤러가 없으면 화면에 보여 줄 게 없다.**

### config에서 정한 것
- `OpenAPI` Bean: 문서 정보(`title`, `version`, `description`)와 서버 주소를 넣는다.
- **bearerAuth 등록**: `SecurityScheme`을 `type(HTTP)` + `scheme("bearer")` + `bearerFormat("JWT")`로 만들어 `bearerAuth`라는 이름으로 등록한다. 요청 헤더에 `Authorization: Bearer <REDACTED>` 형태로 토큰을 싣는다는 뜻을 문서에 알린다. 같은 이름으로 `addSecurityItem(...)`도 함께 넣었다. 토큰 자체는 [[jwt]].
  - 원본 노트에는 "addSecurityItem이 있어야 Authorize 버튼이 생김"이라고 적혀 있었다. 버튼은 `components`에 보안 스킴을 등록하면 생기고, `addSecurityItem`은 그 스킴을 모든 API에 기본으로 적용하는 설정이다([swagger-ui 소스](https://github.com/swagger-api/swagger-ui/blob/master/src/core/containers/authorize-btn.jsx)) (정정).
- `GroupedOpenApi` Bean: 그룹 이름(`api`)과 문서화할 경로(`/**`)를 정한다.

### 주소
- 기본: `http://localhost:8080/swagger-ui/index.html`
- 바꾸기: `src/main/resources/application.properties`에 아래 한 줄을 넣으면 `http://localhost:8080/docs`로 열린다.
  ```properties
  springdoc.swagger-ui.path=/docs
  ```

### 어노테이션으로 문서 채우기
컨트롤러에는 API 설명을, DTO에는 요청·응답 데이터 구조 설명을 단다.

| 어노테이션 | 붙는 곳 | 하는 일 |
|---|---|---|
| `@Tag(name, description)` | 컨트롤러 클래스 | API를 카테고리로 묶음 |
| `@Operation(summary, description)` | 메서드 | 이 API가 무슨 기능인지 |
| `@Parameter(description)` | 파라미터 | 파라미터 설명 |
| `@Schema` | DTO 필드 | 필드 설명. `example`을 주면 테스트할 때 예제값이 미리 채워진다 |

- 4주차 실습에서는 게시글 API(`/api/v1/posts`) 다섯 개에 `@Tag(name = "Post")`와 메서드별 `@Operation`을 달았다. `description`에는 **어느 화면의 어떤 동작에서 불리는지**를 적었다. HTTP 메서드별 의미는 [[rest-api]].

### 결정과 이유
- 의존성·config·controller를 모두 둔 이유: 의존성은 도구를 들여오고, config는 문서의 틀을 정하고, controller가 있어야 문서에 내용이 생긴다.
- bearerAuth를 등록한 이유: 인증이 필요한 API를 문서 화면에서 바로 시험해 보려고.
- 문서 경로는 Spring Security로 개발자 역할만 보게 막을 수 있다. → [[jwt]]

## 언제 쓰나 (상황 예시)
- 프론트엔드와 API 명세를 맞출 때, 문서를 손으로 쓰지 않고 코드에서 바로 뽑고 싶을 때
- 서버를 띄운 채 브라우저에서 요청을 직접 보내 보며 엔드포인트를 확인할 때

## 실습에서 배운 것 / 트러블슈팅
- 3주차 실습은 `/api` 아래에 POST·GET·PATCH·PUT·DELETE 테스트 엔드포인트를 하나씩 만들어 문서에 메서드별로 뜨는지 확인했다. PATCH와 PUT은 같은 경로에 매핑해도 메서드로 구분된다.
- 원본 노트에는 "컨트롤러를 자동으로 스캔에서 문서로 만들어준다"로 적혀 있었다. 같은 문장의 뜻에 따라 "스캔해서"로 고쳤다 (정정).

## 관련
- [[rest-api]] · [[spring-data-jpa]] · [[spring-boot]] · [[jwt]]
