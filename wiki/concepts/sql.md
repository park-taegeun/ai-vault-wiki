---
type: concept
modified: 2026-10-19
sources: [비공개 원본]
tags: [sql, database, oracle]
---

## 한 줄 정의
관계형 데이터베이스(테이블 = 행·열, PK·FK로 관계)에서 데이터를 정의·조작·조회·제어하는 언어다. 여기서는 내가 헷갈렸던 지점(NULL, 실행 순서, 조인 종류, 집합·그룹·윈도우 함수) 위주로 정리한다. 예시 문법은 Oracle 기준이다.

## 핵심 내용
### 명령어 분류
| 분류 | 명령어 | 한 줄 |
|---|---|---|
| DML | SELECT, INSERT, UPDATE, DELETE, MERGE | 데이터 조회·입력·수정·삭제 |
| DDL | CREATE, ALTER, DROP, RENAME, TRUNCATE | 구조(스키마) 정의. Oracle에서는 자동 커밋 |
| DCL | GRANT, REVOKE (사용자 생성·삭제도 이쪽으로 분류) | 권한. 권한 묶음은 `CREATE ROLE` 뒤 롤을 GRANT |
| TCL | COMMIT, ROLLBACK, SAVEPOINT | 트랜잭션 제어 → [[트랜잭션]] |

- `UPDATE`는 데이터를, `ALTER`는 구조를 바꾼다.
- 전체 삭제 비교

| 명령 | 지우는 것 | 구조 | 롤백 | WHERE |
|---|---|---|---|---|
| `DELETE` (DML) | 조건에 맞는 행 | 유지 | 가능 | 가능 |
| `TRUNCATE` (DDL) | 모든 행 + 저장공간 초기화 | 유지 | 보통 불가 | 불가 |
| `DROP` (DDL) | 테이블 자체 | 사라짐 | 보통 불가 | - |

- "DDL은 자동 커밋이라 롤백 불가"는 Oracle 같은 DBMS 기준이다. PostgreSQL처럼 트랜잭션 안에서 `TRUNCATE`·`DROP`을 롤백할 수 있는 DBMS도 있다.

### SELECT의 논리적 실행 순서
`FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY`

쓰는 순서와 도는 순서가 다르다. 이 순서 하나로 여러 규칙이 설명된다.
- **WHERE vs HAVING**: WHERE는 묶기 전에 개별 행을 거르므로 집계 함수를 못 쓴다. HAVING은 묶은 뒤 그룹을 거르므로 집계 함수를 쓴다. 행 단위 조건을 HAVING에 써도 오류는 아니지만, GROUP BY 전에 줄여야 그룹핑 비용이 준다.
- SELECT에서 붙인 별칭은 ORDER BY에서만 쓸 수 있다(WHERE·GROUP BY는 SELECT보다 먼저 돈다).
- GROUP BY에 없는 일반 컬럼은 SELECT에 단독으로 올 수 없다. GROUP BY는 NULL을 버리지 않고 하나의 그룹으로 묶는다.
- `ORDER BY 2`의 숫자는 SELECT 목록의 순서이고, 컬럼 수보다 크면 오류다.
- 계층 쿼리의 `START WITH`, `CONNECT BY`는 WHERE보다 먼저 실행된다.
- 연산자 우선순위: 산술 → 연결 → 비교 → IN·LIKE·BETWEEN·IS NULL → NOT → AND → OR. **AND가 OR보다 먼저**다.

### NULL — 제일 많이 틀린 곳
- NULL은 0이 아니라 "아직 값이 없음"이다.
- 가로 연산(한 행 안 사칙연산)에 NULL이 끼면 결과도 NULL. 세로 연산(집계 함수)은 NULL을 빼고 계산한다. `COUNT(*)`·`COUNT(1)`은 전체 행 수, `COUNT(컬럼)`은 NULL 제외.
- 비교는 `IS NULL` / `IS NOT NULL`만 의미가 있다. `COL = NULL`의 결과는 UNKNOWN이고, WHERE는 TRUE인 행만 통과시키므로 아무 행도 안 나온다.
- **`WHERE COL1 IN (3, NULL)`**
  - `COL1 = 3 OR COL1 = NULL`로 풀린다. 뒤쪽 `COL1 = NULL`은 어떤 행에서도 참이 될 수 없으니, `COL1 = 3`인 행만 나오고 **COL1이 NULL인 행은 나오지 않는다.**
  - 내 원래 노트는 "COL1 = NULL은 항상 FALSE"라고 적었다. 표준 SQL의 3값 논리로는 FALSE가 아니라 UNKNOWN이다. 이 쿼리에서는 결과가 같지만, `NOT`을 씌워도 UNKNOWN은 UNKNOWN이라 역시 통과하지 못한다는 점이 다르다.
  - NULL 행도 잡으려면 `OR COL1 IS NULL`을 따로 붙인다.
- `NOT (A OR B)`는 "A도 아니고 B도 아닌 행"이다.

| 함수 | 동작 |
|---|---|
| `NVL(a, b)` | a가 NULL이면 b (SQL Server의 `ISNULL`) |
| `NVL2(a, b, c)` | a가 NULL이 아니면 b, NULL이면 c |
| `NULLIF(a, b)` | a = b면 NULL, 아니면 a |
| `COALESCE(a, b, …)` | NULL이 아닌 첫 인수 |
| `DECODE(a, b, c, d)` | a = b면 c, 아니면 d |

- `CASE`는 ELSE가 없으면 NULL이 기본값이다.
- Oracle 정렬에서 NULL은 최댓값 취급이다. 내림차순이면 맨 위, 오름차순이면 맨 아래. `NULLS FIRST/LAST`로 바꿀 수 있다.

### 조건·함수 메모
- `BETWEEN A AND B`는 양 끝 포함. `200 BETWEEN COL1 AND COL2`는 `COL1 <= 200 AND 200 <= COL2`.
- `LIKE`: `_`는 정확히 한 글자, `%`는 0글자 이상. `%`·`_` 자체를 찾을 땐 `ESCAPE`로 탈출 문자를 지정한다.
- `LTRIM/RTRIM(s, set)`은 set을 문자열이 아니라 **글자 집합**으로 보고, 집합에 없는 글자를 만날 때까지 깎는다.
- `ROUND(163.76, -2) = 200`처럼 음수 자릿수는 정수부에서 반올림. `CEIL(-33.4) = -33`, `FLOOR(-22.3) = -23`.
- `CHAR`는 고정 길이라 공백을 채워 비교하므로 길이만 다르면 같다고 보고, `VARCHAR`는 다르다고 본다.
- 암시적 형변환에 기대지 말고 `TO_CHAR`·`TO_DATE`·`TO_NUMBER`로 명시한다.

### 조인
| 조인 | 핵심 |
|---|---|
| 세타 조인 | 비교 연산자(=, <, > …)로 조건을 거는 조인 전체 |
| EQUI(등가) / Non-EQUI | `=` 조건 / `BETWEEN`, `>` 같은 범위 조건 |
| INNER JOIN | 조건을 만족하는 행만. 조인 컬럼이 NULL인 행은 빠진다 |
| NATURAL JOIN | 두 테이블에서 **이름이 같은 모든 컬럼**으로 자동 EQUI JOIN하고 공통 컬럼은 한 번만 남긴다. ON·USING과 같이 못 쓰고 조인 컬럼 앞에 별칭을 못 붙인다. 같은 이름 컬럼이 없으면 대부분의 DBMS에서 카티션 곱이 나온다 |
| USING | 같은 이름 컬럼 중 **고른 것만** EQUI JOIN. 조인 컬럼 앞 별칭 불가 |
| CROSS JOIN | 조건 없이 모든 행 조합(카티션 곱). 결과 건수 = 양쪽 행 수의 곱 |
| OUTER JOIN | LEFT는 왼쪽 전부 + 오른쪽 일치분(없으면 NULL), RIGHT는 반대, FULL은 양쪽 전부. Oracle `(+)`는 기준의 반대편에 붙인다(`(+)`가 오른쪽이면 LEFT OUTER) |
| SELF JOIN | 같은 테이블을 별칭 둘로 나눠 조인. 사원의 관리자 찾기, 계층 쿼리 대신 |

> [!note] 정정
> 원본 노트에는 반대로 적혀 있었음 (정정). 오답노트 한 곳에서 NATURAL JOIN 설명에 "조건이 없으면 모든 조합 출력"을, CROSS JOIN 설명에 "같은 이름 컬럼 전부로 EQUI JOIN"을 적어 두었다. 위 표가 맞는 쪽이다. 같은 곳의 "NATURAL JOIN은 ON 절에 조건을 정의하고 USING과 함께 쓸 수 있다"도 틀렸다.

- OUTER JOIN에서 조건을 `ON`에 두면 붙일 행만 거르고 기준 테이블 행은 남는다. `WHERE`에 두면 조인이 끝난 뒤 행 자체를 거른다.
- 직접 FK로 이어지지 않은 엔터티는 경로 위의 연결마다 조인이 하나씩 든다(회원 → 주문 → 주문상품 → 배송이면 3번).
- 공용 키가 없어 이름 문자열로 조인해야 했던 실전 사례 → [[이름-정규화-조인]]

### 서브쿼리
| 위치 | 이름 | 규칙 |
|---|---|---|
| SELECT 등 컬럼 자리 | 스칼라 서브쿼리 | 반드시 1행 1열 |
| FROM | 인라인 뷰 | 임시 테이블처럼 사용 |
| WHERE·HAVING | 중첩 서브쿼리 | 연관 / 비연관 |

- 비연관은 한 번 돌고 결과를 재사용한다. 연관은 메인 쿼리 컬럼을 참조해 메인의 행마다 다시 돈다.
- 단일 행 비교는 `= < >`, 다중 행은 `IN ALL ANY SOME EXISTS`. 여러 행이 나올 수 있는 서브쿼리에 `=`를 쓰면 오류다. `> ALL`은 모든 값보다 커야 참, `> ANY`는 하나라도 만족하면 참.
- 뷰는 SELECT에 이름을 붙여 저장한 것이다(데이터는 저장하지 않음). 민감 컬럼을 빼서 보안, 스키마가 바뀌어도 뷰만 고치는 독립성, 복잡한 질의 단순화.

### 집합 연산자
- `UNION ALL`(중복 포함), `UNION`(중복 제거, 그 과정 때문에 더 느림), `INTERSECT`(교집합), `MINUS`/`EXCEPT`(차집합)
- 위아래 SELECT의 컬럼 수·타입이 같아야 한다. 결과 헤더는 첫 번째 쿼리를 따르고, `ORDER BY`는 맨 마지막에 한 번만.

### 그룹 함수 (소계·총계)
| 함수 | 만드는 그룹 | 메모 |
|---|---|---|
| `ROLLUP(A, B)` | (A,B), (A), 전체 | 인수 순서가 바뀌면 결과도 바뀜 |
| `CUBE(A, B)` | (A,B), (A), (B), 전체 | 가능한 조합 전부(2^n), 순서 무관, 부담이 큼 |
| `GROUPING SETS(…)` | 괄호에 적은 것만 | 순서 무관 |

- `GROUPING(컬럼)`은 그 컬럼이 소계·총계로 묶인 행이면 1이다. `CASE GROUPING(x) WHEN 1 THEN '합계' ELSE x END`로 NULL 대신 라벨을 단다.
- (원본 노트에는 CUBE의 (B) 조합이 "(N, A)"로 적혀 있었음 (정정))

### 윈도우 함수
```sql
RANK() OVER (PARTITION BY dept ORDER BY sal DESC)
```
- `OVER`가 필수다. `PARTITION BY`로 범위를 나누고, 순위 함수에는 `ORDER BY`가 반드시 있어야 한다.
- 순위: `RANK`(동점 같은 순위, 다음 순위 건너뜀: 1,1,3), `DENSE_RANK`(안 건너뜀: 1,1,2), `ROW_NUMBER`(동점도 다른 번호: 1,2,3)
- OVER에 ORDER BY가 없으면 파티션 전체, 있으면 누적 계산이다. 범위를 안 쓰면 기본값은 `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`. `ROWS`는 행 기준, `RANGE`는 값 기준(같은 값은 한꺼번에 합산).
- 함정: `LAST_VALUE`는 기본 범위가 "현재 행까지"라서 진짜 마지막 값을 보려면 `… AND UNBOUNDED FOLLOWING`을 명시한다.
- `LAG(col, n, 대체값)` / `LEAD(col, n, 대체값)`: n칸 위/아래 값. 행이 없으면 NULL이고, 세 번째 인수를 주면 그 값으로 대체한다. (원본 노트엔 두 번째 인수가 대체값이라고 적혀 있었음 (정정))
- 비율: `RATIO_TO_REPORT`(합계 대비), `PERCENT_RANK`((순위-1)/(건수-1)), `CUME_DIST`(누적 건수/전체)
- `NTILE(n)`: n등분하고 남는 행은 앞 그룹부터 하나씩 더 받는다. 5행이면 NTILE(2)는 3/2, NTILE(3)은 2/2/1. (원본 노트에는 "5행에 NTILE(5)면 3/2"로 적혀 있었음 (정정))

### Top-N, 계층 쿼리, PIVOT
- `ROWNUM`은 ORDER BY보다 먼저 매겨진다. 정렬은 인라인 뷰 안에서 하고 바깥에서 자른다. `ROWNUM = 2`처럼 1을 건너뛰는 조건은 결과가 없다.
  ```sql
  SELECT * FROM (SELECT name, sal FROM emp ORDER BY sal DESC) WHERE ROWNUM <= 5;
  ```
- 계층 쿼리: `START WITH`(루트) + `CONNECT BY PRIOR 부모 = 자식`(방향). `LEVEL`(루트 = 1), `SYS_CONNECT_BY_PATH`, `CONNECT_BY_ROOT`, `CONNECT_BY_ISLEAF`, `CONNECT_BY_ISCYCLE`. 일반 `ORDER BY`는 트리 순서를 깨므로 형제끼리만 정렬하려면 `ORDER SIBLINGS BY`.
- `PIVOT`은 행을 열로, `UNPIVOT`은 반대. 정규식 함수는 `REGEXP_SUBSTR / REPLACE / INSTR / COUNT`, 조건식 `REGEXP_LIKE`.

### DDL·DML 실무 포인트
- `INSERT`에서 컬럼명을 생략하면 모든 컬럼 값을 순서대로 줘야 한다. 일부만 넣으면 컬럼명 필수.
- `UPDATE`·`DELETE`에 WHERE가 없으면 전 행이 대상이다.
- `MERGE INTO 대상 USING 원본 ON (조건) WHEN MATCHED THEN UPDATE … WHEN NOT MATCHED THEN INSERT …` — upsert를 한 문장으로.
- 제약조건: PK(테이블당 1개, NULL 불가, UNIQUE 인덱스 자동 생성 → [[db-인덱스]]), UNIQUE(NULL 허용), NOT NULL, CHECK(값 범위), FK(참조 + `CASCADE`·`SET NULL` 등 삭제 옵션)
- `DROP TABLE t CASCADE CONSTRAINT`는 이 테이블을 참조하는 제약조건까지 지운다.
- `CREATE TABLE … AS SELECT`(CTAS)는 NOT NULL 제약만 따라온다.
- `ALTER TABLE`: `ADD`(항상 맨 끝), `DROP COLUMN`(복구 불가), `MODIFY`(데이터가 있으면 크기 축소·타입 변경 제한), `RENAME COLUMN … TO …`, `ADD/DROP CONSTRAINT`

### 키와 무결성
- 슈퍼키는 유일성만, 후보키는 유일성 + 최소성을 만족한다.
- 개체 무결성: PK는 NULL 불가 + 중복 불가
- 참조 무결성: FK는 NULL이거나, 참조하는 테이블의 PK에 실제로 있는 값
- 도메인 무결성: 값이 정의된 범위 안에 있어야 한다(CHECK, DEFAULT)
- 정규화가 필요한 이유는 이상 현상이다. 삽입 이상(원치 않는 데이터까지 같이 넣어야 함), 삭제 이상(한 행을 지우면 딸린 정보까지 사라짐), 갱신 이상(중복 값 중 일부만 바뀌어 어긋남). 반대로 반정규화는 성능을 위해 중복을 허용하거나 테이블을 합쳐 조인 수를 줄인다.

### 관계대수와의 대응
SQL 뒤의 이론은 관계대수(절차로 표현)와 관계해석(원하는 것만 표현)이다. σ(셀렉트)는 WHERE처럼 행을, π(프로젝트)는 SELECT 목록처럼 열을 고른다. ⨝은 조인, ×는 카티션 프로덕트, ÷(디비전)는 A(X, Y) ÷ B(Y)일 때 B의 모든 튜플과 짝을 이루는 A의 X 값을 돌려준다.

## 언제 쓰나 (상황 예시)
- 조건에 NULL이 섞일 수 있는 필터: `IN` 목록에 NULL을 넣어도 NULL 행은 안 잡힌다. `OR COL1 IS NULL`을 따로 붙인다.
- 같은 이름 컬럼이 여러 개인 두 테이블을 이을 때: NATURAL JOIN은 의도하지 않은 컬럼까지 조건에 넣으므로 USING이나 ON으로 명시한다.
- "부서별 평균이 N 이상" → GROUP BY + HAVING / "부서별 소계 + 전체 합계" → `ROLLUP` + `GROUPING`
- "급여 상위 5명" → 인라인 뷰 정렬 + `ROWNUM <= 5`, 또는 `ROW_NUMBER()`
- "직전 기록과 비교" → `LAG` / "있으면 수정, 없으면 입력" → `MERGE`

## 실습에서 배운 것 / 트러블슈팅
- 헷갈린 이유 대부분이 "NULL은 값이 아니다"를 놓친 데서 나왔다. `= NULL`, `IN (…, NULL)`, `COUNT(컬럼)`이 같은 뿌리다.
- 집계 조건을 WHERE에 쓰는 실수가 가장 흔했다. 실행 순서를 떠올리면 왜 안 되는지 바로 보인다. 노트 두 곳에 HAVING이 GROUP BY 앞에 적혀 있었던 것도 바로잡았다.
- 조인 이름과 설명을 짝지어 외우다 서로 바꿔 적었다(위 정정). "CROSS = 조건 없음 = 곱", "NATURAL = 같은 이름 자동"처럼 키워드 하나로 묶는 편이 덜 헷갈렸다.
- 윈도우 함수 결과에 SUM이 나오면 그 값이 어떤 범위(ROWS/RANGE, 누적 여부)로 계산됐는지부터 거꾸로 따라가는 게 빨랐다.
- 계층 쿼리 결과 맞히기: START WITH에서 LEVEL 1이 될 행을 찾고, CONNECT BY 조건대로 더 붙을 행이 없을 때까지 따라간다.

## 관련
- [[트랜잭션]] — COMMIT·ROLLBACK, DDL 자동 커밋
- [[db-인덱스]] — PK가 만드는 UNIQUE 인덱스, WHERE·JOIN 조건 컬럼
- [[이름-정규화-조인]] — 공용 키 없이 이름으로 조인한 사례
- [[pandas]] — DataFrame merge도 같은 조인 개념
