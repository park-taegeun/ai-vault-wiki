---
type: tool
modified: 2026-10-19
sources: [_private/raw/notion/Backend/Session/Week02 - Spring Boot의 이해 2bdd8df03cab80128c61c894a0e7dd76.md, _private/raw/notion/Backend/세션 정리/2주차 - SpringBoot의 이해 302d8df03cab80f79890de9c3adf8d66.md, _private/raw/notion/Backend/세션 정리/2주차 - SpringBoot의 이해/실습 302d8df03cab8017b194d8be05592af3.md, _private/raw/notion/Backend/세션 정리/2주차 - SpringBoot의 이해/실습/helloWorld 브라우저 출력 흐름 302d8df03cab8065a6b7df2fce7cbfed.md, _private/raw/notion/Backend/세션 정리/2주차 - SpringBoot의 이해/실습/MySQL 302d8df03cab80979f22deb482953e5f.md, _private/raw/notion/Backend/세션 정리/2주차 - SpringBoot의 이해/실습/SpringBoot 어플리케이션 빌드 302d8df03cab806d8bb0f208dbf92f2c.md, _private/raw/notion/Backend/세션 정리/2주차 - SpringBoot의 이해/실습/SpringBoot로 데이터 조회 실습 302d8df03cab80e4b178ce1038e129d7.md, _private/raw/notion/Backend/과제/2주차 - MySQL 작성 및 스프링 부트 연동 303d8df03cab809f83aae52395c2d26b.md, 비공개 원본]
tags: [spring-boot, java, backend, gradle, mysql, 멋쟁이사자처럼]
---

## 한 줄 정의
Spring을 설정 부담 없이 쓰게 해 주는 자바 백엔드 프레임워크다. 의존성과 초기 설정을 알아서 잡아 주고 웹 서버(Tomcat)를 품고 있어서, 빌드한 jar 하나를 `java -jar`로 띄우면 서버가 된다. 멋쟁이사자처럼 13기 백엔드 트랙 2주차 세션에서 처음 다뤘다.

## 핵심 내용
### 프레임워크와 라이브러리
- **라이브러리**: 필요할 때 꺼내 쓰는 도구 모음이다. 개발자가 직접 호출하므로 제어 주도권은 개발자에게 있다.
- **프레임워크**: 따라야 할 구조와 규칙이 정해진 틀이다. 프레임워크가 개발자 코드를 호출하므로 제어 주도권은 프레임워크에 있다.
- Spring Boot는 애플리케이션 실행 흐름 전체를 관리하고, 개발자는 정해진 규칙(어노테이션, 클래스 구조)에 맞춰 코드를 채운다.

### Spring과 Spring Boot

| | Spring | Spring Boot |
|---|---|---|
| 초기 설정 | 직접, 복잡함 | 자동으로 잡아 줌 |
| 의존성 | 직접 관리 | 자동 관리 (Starter 단위로 추가) |
| 서버 | 따로 설정, war로 배포 | 내장 웹 서버, jar로 배포 |

### 바탕이 되는 Java
- **플랫폼 독립성**: 소스코드 → 컴파일 → 바이트코드 → JVM 실행. 바이트코드가 JVM 위에서 돌아서 OS마다 다시 컴파일하지 않는다.
- **객체지향 언어**, **강타입 언어**(변수 선언 시 타입을 명시).
- **자동 메모리 관리(GC)**: JVM의 GC가 참조되지 않는 객체를 정리한다.
- **객체지향 4특징**
  1. 캡슐화: 필드와 메서드를 한 클래스로 묶고, 접근 제어자로 외부의 직접 접근을 막아 getter/setter로 간접 접근하게 한다. 원본 노트에는 "간접접"으로 적혀 있었다 (정정).
  2. 상속: 부모 클래스의 속성과 메서드를 물려받아 재사용한다.
  3. 다형성: 같은 부모 타입으로 서로 다른 구현체를 다룬다. 오버로딩(컴파일타임)과 오버라이딩(런타임)으로 구현한다.
  4. 추상화: 복잡한 구현은 숨기고 필요한 인터페이스만 노출한다. `abstract`와 `interface`로 구현한다.

### 명명 규칙
- `camelCase`: 변수·메서드 (`getStudents`)
- `PascalCase`: 클래스·타입 (`StudentController`)
- `SNAKE_CASE`: 단어를 `_`로 잇는다. 상수명에 쓴다.

### MVC
Model은 데이터와 비즈니스 로직, View는 사용자에게 보이는 화면, Controller는 둘 사이에서 요청과 데이터 흐름을 조정한다. 2주차 실습은 화면 없이 Controller가 문자열·JSON을 바로 돌려주는 형태였다. HTTP 메서드와 명세는 [[rest-api]].

### 프로젝트 구조: 계층형과 도메인형

| | 계층형 | 도메인형 |
|---|---|---|
| 나누는 기준 | 계층(controller, repository …) | 도메인(기능) |
| 장점 | 전체 구조를 빨리 파악 | 기능별로 독립적 |
| 단점 | 한 디렉터리에 클래스가 쌓임 | 프로젝트를 잘 모르면 전체 구조가 안 보임 |

### Gradle 빌드와 실행
Gradle은 컴파일·테스트·패키징을 자동으로 해 주는 빌드 도구다. `build.gradle`(의존성·플러그인, group은 `com.likelion`), `settings.gradle`(`rootProject` 이름), `gradlew`/`gradlew.bat`(실행 스크립트), `gradle/wrapper`(Gradle을 설치하지 않아도 task 실행)로 이뤄진다.

```bash
./gradlew build                                   # gradlew가 있는 프로젝트 루트에서
java -jar build/libs/<프로젝트명>-0.0.1-SNAPSHOT.jar
```
- `./gradlew build`: 소스 컴파일 → 테스트 실행 → `build/libs/`에 jar 생성. 배포가 아니라 **배포 전 단계**다. IntelliJ에서 실행·테스트를 끝낸 뒤 마지막 전체 검증으로 돌린다.
- `java -jar`: jar 안의 main 메서드(`@SpringBootApplication` 클래스) 실행 → Spring Boot 시작 → 내장 Tomcat이 8080 포트를 연다 → 컨트롤러 스캔 → 요청 대기. IntelliJ 실행 버튼을 누른 것과 같은 상태다.

### Bean과 DI
- Bean은 Spring Container가 만들고 관리하는 객체다. 개발자가 `new`로 만들지 않고, 한 곳에서 관리하니 같은 객체를 재사용하고 유지보수가 쉽다.
- 등록 방법: 수동은 `@Configuration` 클래스 안 `@Bean` 메서드(외부 라이브러리도 등록 가능), 자동은 `@Controller`, `@Service` 등이 붙은 클래스를 스캔한다.
- 주입: 필요한 Bean을 Spring이 넣어 준다. 세션 정리에는 `@Autowired`로 객체가 주입된다고 적었다(원본 노트에는 "객체제 주입"으로 적혀 있었다 (정정)). 실습 코드는 `@Autowired` 없이 **생성자 주입**을 썼다. Spring이 컨트롤러를 만들다가 생성자 파라미터에 Repository가 필요한 걸 보고, 이미 만들어 둔 Bean을 넣는다.

```java
@RestController
@RequestMapping("/api")
public class StudentController {
    private final StudentRepository studentRepository;

    public StudentController(StudentRepository studentRepository) {
        this.studentRepository = studentRepository;
    }

    @GetMapping("/students")
    public List<Student> getStudents() {
        return studentRepository.findAll();   // 테이블 전체 조회 → JSON 응답
    }
}
```

### MySQL 연동 흐름
1. `build.gradle`에서 Edit Starters로 **MySQL Driver**와 **Spring Data JPA** 의존성을 추가한다.
2. `src/main/resources/application.properties`에 DB 접속 정보(값은 `<REDACTED>`)와 JPA 설정을 넣는다.
3. 터미널에서 MySQL에 접속해 DB·테이블을 만들고 데이터를 넣는다. → [[sql]]
4. 엔티티(`@Entity`, `@Id`, `@GeneratedValue(strategy = GenerationType.IDENTITY)`)와 `JpaRepository<엔티티, PK타입>`을 상속한 인터페이스, 컨트롤러를 만들어 `/api/students`가 데이터를 돌려주는지 본다. → [[spring-data-jpa]]

### 결정과 이유
- **`application.properties`를 Git에서 뺀다**: DB 접속 정보 같은 중요한 값이 들어 있어서 GitHub에 올라가면 노출된다. `.gitignore`에 경로를 추가하고 `git rm --cached src/main/resources/application.properties`로 추적을 해제한 뒤 `git status`에서 삭제로 표시되는지 확인한다.
- **이미지는 `resources/static/images`에 둔다**: `static`은 정적 파일 폴더다. `images` 말고는 쓸 일이 거의 없어 `static/images`만 만들었다.
- **코드 포매터를 맞춘다**: 사람마다 작성 스타일이 달라서 생기는 conflict를 줄이려고 정해진 컨벤션으로 자동 정렬한다. → [[github-flow]]

## 언제 쓰나 (상황 예시)
- DB 테이블을 JSON API로 내보내는 백엔드를 빠르게 세울 때 (엔티티 + Repository + Controller)
- IntelliJ 없이 서버를 띄워야 할 때: `./gradlew build` 후 `java -jar`
- 여러 사람이 같은 프로젝트를 쓸 때: 접속 정보가 든 설정 파일은 `.gitignore`, 코드 스타일은 포매터로 통일

## 실습에서 배운 것 / 트러블슈팅
### helloWorld가 브라우저에 찍히기까지
1. `@SpringBootApplication` 클래스의 `main`에서 `SpringApplication.run(...)` → 내장 Tomcat이 켜지고 8080 포트가 열리며 프로젝트 전체를 스캔한다.
2. 브라우저가 `/api/hello`를 요청한다.
3. 클래스 레벨 `@RequestMapping("/api")` + 메서드 레벨 `@GetMapping("/hello")` = `/api/hello`에 맞는 메서드를 찾아 실행한다.
4. `@RestController`라서 반환한 문자열이 그대로 응답이 되어 브라우저에 찍힌다.

### 포트 8080 충돌로 실행이 안 될 때
```bash
lsof -i :8080   # 8080을 쓰는 프로세스 찾기
kill -9 PID     # 찾은 PID를 넣어 종료
```
같은 증상을 Flask 5000 포트에서 겪은 사례는 [[flask]].

### 프로젝트·패키지 이름 바꾸기
이름이 남는 곳이 많았다: IntelliJ Project Structure, `settings.gradle`의 `rootProject`, 패키지 디렉터리(Refactor → Rename), Application 클래스 이름(테스트 클래스도 같이 바뀜), `application.properties`, `build.gradle`의 group. 마지막에 Find in Files로 옛 이름이 안 나오는지 확인하고, `.idea` 폴더를 지운 뒤 다시 열었다.

## 관련
- [[spring-data-jpa]] · [[rest-api]] · [[swagger]] · [[jwt]] · [[sql]] · [[sqlalchemy]] · [[flask]] · [[github-flow]]
