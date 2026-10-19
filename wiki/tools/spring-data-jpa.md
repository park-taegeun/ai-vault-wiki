---
type: tool
modified: 2026-10-19
sources: [_private/raw/notion/Backend/세션 정리/4주차 - Entity, Controller, Swagger 알아보기 30bd8df03cab80e0b5cedd9827abda36.md, _private/raw/notion/Backend/세션 정리/4주차 - Entity, Controller, Swagger 알아보기/실습 30bd8df03cab806dabc4fc1d4fa8452d.md, _private/raw/notion/Backend/세션 정리/3주차 - API 명세의 이해와 Annotation 305d8df03cab80d9893cf645c6f4274b.md]
tags: [spring, jpa, orm, lombok, 멋쟁이사자처럼]
---

## 한 줄 정의
자바 객체를 관계형 DB 테이블에 맞춰 저장·조회하게 해 주는 Spring의 ORM 도구다. 개발자는 객체 중심으로 코드를 쓰고, DB에 맞는 SQL 처리는 JPA 쪽에 맡긴다. 멋쟁이사자처럼 13기 백엔드 트랙 4주차에 Lombok과 함께 들였다.

## 핵심 내용
### 왜 필요한가: 패러다임 불일치
- 관계형 DB는 "데이터를 어떻게 저장할지"를 중심으로 설계됐고, 객체지향은 기능과 속성을 한 객체에 묶는다. 생각 틀이 달라서 객체를 그대로 DB에 넣으려 하면 어긋남이 생긴다. 이것을 패러다임 불일치라고 부른다.
- 손으로 메우다 보면 애플리케이션 코드보다 SQL이 더 많아진다. JPA를 쓰면 SQL에 매이지 않고 객체 중심으로 개발할 수 있다.
- 원본 노트에는 "JAP는 이를 RDB에 맞게…"로 적혀 있었다. 같은 노트 첫머리의 "Spring data JPA"에 따라 JPA로 고쳤다 (정정).

### 도메인과 Entity
- 도메인은 게시글·회원·댓글·결제처럼 서비스가 다루는 핵심 대상이다. 도메인 패키지에는 Entity, Repository(데이터 저장·조회), 그 도메인의 비즈니스 로직이 모인다.
- Entity는 DB 테이블 하나와 짝이 되는 클래스다. `@Entity`를 붙여야 JPA가 관리하고, 기본 키 `@Id`도 함께 단다.
- JPA는 리플렉션으로 객체를 만들기 때문에 기본 생성자가 필요하다. 그래서 `@NoArgsConstructor`를 붙인다.
- 4주차 실습의 `Post` 엔티티: `id`(자동 증가 PK), `title`, `content`(둘 다 NOT NULL), `BaseTimeEntity` 상속.

### BaseTimeEntity (Auditing)
- 거의 모든 테이블에 생성·수정 시각 컬럼이 있어서, 두 시각을 가진 추상 부모 클래스를 하나 만들고 엔티티가 상속받게 한다.
- 부모에는 `@MappedSuperclass`(자식이 이 필드를 컬럼으로 인식)와 `@EntityListeners(AuditingEntityListener.class)`를, 필드에는 `@CreatedDate`·`@LastModifiedDate`를 단다. Application 클래스에 `@EnableJpaAuditing`을 붙여야 동작한다.

### Lombok
- 생성자, getter·setter 같은 반복 코드를 어노테이션 하나로 컴파일 시점에 만들어 주는 라이브러리다. 원본 노트(3주차)에는 "Lombock"으로 적혀 있었다 (정정).

| 어노테이션 | 만들어 주는 것 |
|---|---|
| `@Getter` / `@Setter` | 모든 필드의 get / set 메서드 |
| `@NoArgsConstructor` | 기본 생성자 (JPA 엔티티에 필수) |
| `@AllArgsConstructor` | 모든 필드를 받는 생성자 |
| `@RequiredArgsConstructor` | `final` 또는 `@NonNull` 필드만 받는 생성자. 주입받을 때 주로 씀 → [[spring-boot]] |
| `@Builder` | 빌더 패턴 (`Post.builder().title(…).build()`) |

### 어노테이션 레벨별 정리
어노테이션은 `@`로 시작하는 표시로, 코드에 관한 정보를 덧붙여 특별한 의미나 기능을 준다. 원본 노트(3주차)에는 "Annotoation"으로 적혀 있었다 (정정).

| 레벨 | 어노테이션 | 뜻 |
|---|---|---|
| 클래스 | `@Entity`, `@Table(name = "…")` | DB 테이블과 매핑, 테이블 이름 |
| 클래스 | `@RestController`, `@RequestMapping("/api/v1")` | REST 컨트롤러, 공통 경로 |
| 필드 | `@Id`, `@GeneratedValue(strategy = GenerationType.IDENTITY)` | 기본 키, DB 자동 증가(MySQL AUTO_INCREMENT) |
| 필드 | `@Column(length = 500, nullable = false)` | 길이 제한, NULL 허용 여부 |
| 메서드 | `@GetMapping` `@PostMapping` `@PutMapping` `@DeleteMapping` | HTTP 메서드별 요청 처리 → [[rest-api]] |
| 파라미터 | `@RequestBody`, `@PathVariable`, `@RequestParam` | JSON 본문, URL 경로 변수, 쿼리 파라미터 |

Swagger 문서용 어노테이션은 [[swagger]].

### 결정과 이유
- `BaseTimeEntity`를 부모로 뺀 이유: 생성·수정 시각을 엔티티마다 반복해서 쓰기 번거로워서.
- `@NoArgsConstructor`를 단 이유: JPA가 리플렉션으로 객체를 만들 때 기본 생성자가 필요해서.

## 언제 쓰나 (상황 예시)
- Spring 서버에서 도메인 객체를 DB에 저장·조회해야 할 때
- 생성·수정 시각처럼 모든 테이블에 공통인 컬럼을 한 곳에서 관리할 때
- 같은 문제를 Python에서 푼 ORM은 [[sqlalchemy]]다.

## 실습에서 배운 것 / 트러블슈팅
- 4주차 실습에서 `Post` 엔티티와 `PostController`를 함께 만들었다. 컨트롤러는 아직 Service 없이 문자열만 돌려주는 뼈대 단계였다.

## 관련
- [[sqlalchemy]] · [[swagger]] · [[rest-api]] · [[spring-boot]] · [[sql]]
