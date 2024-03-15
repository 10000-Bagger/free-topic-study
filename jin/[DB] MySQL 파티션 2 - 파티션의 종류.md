[Pull Request](https://github.com/10000-Bagger/free-topic-study/pull/52)
# MySQL 파티션의 종류


MySQL에서는 기본적인 파티션 4가지를 제공해준다.

1. Range Partition
2. List Partition
3. Hash Partition
4. Key Partition

<br>

(TODO : 짧게 기본적인 설명들 추가)
![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/0e2c6eee-a088-43bc-b557-4fe12c102092)

Range Partiton은 "범위"로 파티션 키를 지정하는 것이다. "2000년생 이상 2004년생 미만은 한 파티션에 들어가라"와 같이 범위로 지정하는 것이다. <Br>
List Partition 리스트 파티션과 유사하나, **파티션 키가 "연속된 범위"값이 아니다.** List Partiton 파티션 키 값 하나하나를 "리스트"로 나열해야 한다. 예를 들어 (3월, 6월, 9월, 생은 한 파티션에 들어가라)와 같이 지정하는 것이다. 또한 리스트 파티션은 MAXVALUE 지정이 불가능하다. <br>
Hash Partition은 MySQL에서 정의한 해시 함수에 의해 파티션이 결정된다. MySQL 해시 함수는 단순하게, `표현식 % 파티션 갯수`로 결정된다. 그래서 Hash Partition의 Partition Key는 정수 타입이거나, 정수를 반환하는 표현식이여야 한다. 읽으면서 눈치 챘겠지만, 추가 삭제에 대한 재분배가 엄청날 수 밖에 없다. <br>
Key Partition은 Hash Partition과 사용법이나 특징이 유사하다. <br> 
Hash Partition은 사용자가 파티션 키나 표현식을 통해 해시 값 계산을 어느 정도 명시할 수 있다. MySQL 서버는 그 결과값에 MOD를 적용하는 것이다. Key Partition은 조금 다르다. **사용자는 파티션 키 값만을 정할 수 있고, MySQL이 `MD5()`를 적용해 직접 해시값을 계산하고** 그 값에 MOD를 적용한다. **대신 꼭 정수형이 아니여도, 대부분의 데이터 타입을 Partition Key로 지정할 수 있다.**

<br>

이렇게 4가지 파티션이 제공된다. 이제 하나씩 특징을 살펴보자.

### 파티션의 장점
각 파티션의 종류를 더 자세히 보기 전에 다시 한번 파티션의 장점을 짚고 넘어가자. 왜냐하면, 우리가 파티션을 적용하는 목적과 장점을 분명히 해야, 여러 종류의 파티션 중 어떤 파티션을 고를지 더욱 명확해지기 때문이다. <br> <br>

파티션의 장점은 아래와 같다.
1. **필요한 파티션만 접근할 수 있다.** (읽기, 쓰기 모두 포함)
2. 큰 테이블을 작은 크기의 파티션으로 분리

**보통 1번 사항이 매우 중요하고 효과적이므로, 여기에 집중해야 한다!** <br>
오히려 2번 장점에 집중하는 경우 오히려 성능을 떨어뜨리게 될 수도 있는데, 여기에 집중하는 경우도 많으니 항상 주의해야 한다.



## 1. Range Partition


<br>

말 그대로 파티션 키의 "범위"로 파티션을 정의하는 방법이다. 가장 일반적이다. <br>
위 그림은 "월별로" 나뉘어 있다. 예를 들어 3월 1일 데이터 부터 ~~ 4월 31일 데이터는 한 테이블에 들어가게 되는 것이다. <Br>
이렇게 "범위로" 저장하기 떄문에 Range Partition이다. <br>
MySQL의 `MAXVALUE` 키워드를 통해 명시하지 않은 파티션 키 값이 들어가게 될 파티션도 결정할 수 있다.

### 1.1 용도

레인지 파티션은 어떤 상황에서 유리할까? 구체적인 예시는 아래와 같다.

1. 범위 기반으로 데이터를 여러 파티션에 균등하게 나눌 수 있을 때
2. 날짜 기반 누적 데이터 -> 특히 연도나 월, 일 단위로 분석 작업이 필요하거나, 삭제가 필요한 경우 유용하다.
3. 파티션 키 위주로 검색이 자주 실행될 때 (사실 모든 파티션에 적용되는 내용이긴 하다.)

<Br>

레인지 파티션을 위의 예시 상황에 적용하면, 앞서 언급한 파티션의 장점 2가지를 모두 누릴 수 있다! 
특히 이력, 로그를 저장하는 테이블에서 Range Partitiion이 매우 유용하다. <br>
복습 차원에서 한번 더 살펴보자.
1. 필요한 파티션만 접근
2. 큰 테이블을 작은 크기의 파티션으로 분리

### 1.2 레인지 파티션 테이블 생성
아래는 레인지 파티션을 활용해 사원의 입사 연도별로 파티션 테이블을 만든 것이다.

<br>

```sql
CREATE TABLE `employees`(
  id int NOT NULL,
  name varchar(10),
  hired date NOT NULL default '2010-01-01'

  ...

) engine=innodb default charset=utf8mb4
  PARTITION BY RANGE( YEAR(hired) ) (

  PARTITION p0 VALUES LESS THAN(2011) engine=innodb,
  PARTITION p1 VALUES LESS THAN(2012) engine=innodb,
  PARTITION p2 VALUES LESS THAN(2013) engine=innodb,
  PARTITION p3 VALUES LESS THAN(2014) engine=innodb,
  PARTITION p999 VALUES LESS THAN MAXVALUE engine=innodb

);
```


1. PARTITION BY RANGE : 키워드로 레인지 파티션을 정의했다.
2. 내장함수 `YEAR()`을 통해 "입사 연도"를 파티션 키로 명시했다.
3. `VALUES LESS THAN`을 통해 명시된 값보다 작은 값만 해당 파티션에 저장하게 설정했다. **(미만)** 
4. **`MAXVALUE` 키워드를 통해 명시되지 않은 값이 들어갈 곳을 지정했다! <br> 2014 년도 이후 입사자들은 p999에 저장될 것이다!** 
5. `MAXVALUE`를 정의하지 않은 경우, 2014년 이후 데이터가 INSERT 되는 경우 에러가 발생한다. <br> -> ex) 2024 insert한 경우 에러 메시지 : "Table has no partition for value 2024"
6. 명시하지 않아도 MySQL 기본 db인 innodb가 사용되나 명시해봤다.
7. 이미 이해 했겠지만, 2011 이상, 2012 이하인 경우 p1 파티션에 저장된다



<Br>

### 1.3 레인지 파티션 추가
2014 이상 ~ 2024 미만 데이터가 담길 레인지 파티션을 추가해보자.

```sql
ALTER TABLE employees
  ADD PARTITION (PARTITION p4 VALUES LESS THAN (2024));
```

<br>

간단한 명령으로 추가할 수 있다. <br>
하지만, 우리 예시처럼 `MAXVALUE`가 걸려있는 경우엔, 저렇게 단순하게 추가할 수 없다. 에러가 발생하게 된다. <Br>
왜냐하면 이미 employees Table의 `MAXVALUE` 파티션이 2014 이상 레코드를 가지고 있는 상황이기 떄문이다. 이 경우에는 다른 명령어를 사용해야 한다. (Reorganize Partition 명령어를 써야 한다.)

```sql
ALTER TABLE employees ALGORITHM=INPLACE, LOCK=SHARED,
  REORGANIZE PARTITION p999 INTO (
    PARTITION p4 VALUES LESS THAN (2024),
    PARTITION p999 VALUES LESS THAN MAXVALUE
  );
```

Reorganize Partition 명령어는 MAXVALUE 테이블인 p999 파티션의 레코드를 새로운 두 개의 파티션으로 복사한다. 만약 p999에 레코드가 많았더라면, 이 작업은 오랜 시간이 걸릴 것이다. <br>
일반적으로는 중간에 추가하는 것이 좋지 않기 때문에, 미래에 사용하게 될 파티션 2 ~ 3개를 미리 만드는 것을 권한다. 거기에 더해 보통은 배치 스크립트를 활용해, 여유분도 자동으로 생성되게 하는 방식을 사용한다고 한다. 올해가 2024년이라고 한다면 2027 년도까지의 테이블을 미리 만들어 두는 배치 스크립트를 사용하면 좋을 것이다. 물론 배치 스크립트를 활용하는 경우 오류에 매우 매우 주의해야 할 것! <br> <br>


### 1.3 레인지 파티션 삭제
`DROP PARTITON` 키워드를 사용해라. 레인지 파티션과 리스트 파티션은 파티션 삭제 작업이 아주 빠르게 처리 되어서 좋다. 보통 연도별 데이터 중 너무 오래되서 필요없는 데이터를 지울 때 많이 사용된다.
```sql
ALTER TABLE employees DROP PARTITION p0;
```

### 1.4 레인지 파티션 분리

하나의 파티션을 두 개 이상의 파티션으로 분리할 때도 아까 보인 `REORGANIZE PARTITION`을 활용하면 된다. <br>
물론 오랜 시간이 걸릴 수 있기 때문에, ALGORITHM과 LOCK을 활용하면 좋다. 최소한 Shared Lock은 걸자.
```sql
ALTER TABLE employees ALGORITHM=INPLACE, LOCK=SHARED,
  REORGANIZE PARTITION p999 INTO (
    PARTITION p4 VALUES LESS THAN (2024),
    PARTITION p999 VALUES LESS THAN MAXVALUE
  );
```

### 1.5 레인지 파티션 병합
이 또한 `REORGANIZE PARTITION`으로 가능하다. 
```sql
ALTER TABLE employees ALGORITHM=INPLACE, LOCK=SHARED,
  REORGANIZE PARTITION p2, p3 INTO (
    PARTITION p23 VALUES LESS THAN (2024)
  );
```
# 2. List Partition
List Partition은 레인지 파티션과 거의 비슷하다. 다른 점은 한 파티션에 들어가게 될 키값들의 "범위"를 지정하는 대신 "리스트"를 정의하는 방식이라는 점이다. <br>
리스트를 정의한다니까 자료구조 리스트가 떠올라서 말이 모호한데, 장보기 리스트를 짜는 것 처럼 파티션 키 리스트를 짜면 된다. <br>
예를 들어 레인지 파티션은 `3월 ~ 6월 생은 '봄' 그룹에 들어가세요`와 같이 "범위"로 정의했다면, List Partition은 `1월, 5월, 11월 생들은 그룹 A에 들어가세요`와 같이 하나 하나 지정하는 것이 특징이다. 예를 들어 아래와 같이 지정할 수 있다.
```sql

...
  ) PARTITION BY LIST (category_id) (
  
  ...

  PARTITION A VALUES IN (1, 5, 11),
  
  ...

  );
```

보시다 싶이 하나 하나 지정해줘야 한다는 점 외에는 레인지 파티션과 비슷하다. <br>
**또 하나의 가장 큰 차이는 `MAXVALUE` 파티션을 정의할 수 없다는 점과 NULL이 들어갈 곳을 지정할 수 있다는 것이다.** <br> 

## 2.1 리스트 파티션의 용도
테이블이 아래와 같은 특성이 있을 때 리스트 파티션이 효과적이다.
1. 파티션 키 값이 고정적일때, <br> ex) 카테고리, 코드 값 등 연속적이지 않은 값..
2. 키 값이 연속되지 않고, 정렬 순서와 무관한 방식으로 파티션을 해야 하는 경우
3. 파티션 키 값을 기준으로 레코드의 건수가 균일하고, 검색 조건에 파티션 키가 자주 사용되 때 <br> 예를 들어 쇼핑 카테고리별로 상품 갯수가 균일하고, 카테고리로 검색이 많다면 편리하겠쥬?


## 2.2 쿼리 쿼리 
### 생성
```sql
CREATE TABLE `tb_list_table` (
  id int not null auto_increment,
  name varchar(10),
  dept_no int not null,
  primary key(id,dept_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  PARTITION BY LIST(dept_no) (
  PARTITION P_ACCOUNTING VALUES IN(1, 9),
  PARTITION P_RESEARCH VALUES IN(2, 6, 7),
  PARTITION P_SALES VALUES IN(4, 5, 8, NULL)
);
```

Range 때와 다르게 `PARTITION BY LIST`로 정의 하였다. <br>
`VALUES IN()` 안에 리스트 형식으로 값을 넣었다. 또한, NULL이 들어갈 파티션을 정의할 수 있다. <br>
아래와 같이 문자열로 지정하는 것도 가능하다.

```sql
  ...

) PARTITION BY LIST(category) (
  PARTITION P_ACCOUNTING VALUES IN('TV'),
  PARTITION P_RESEARCH VALUES IN('Notebook', 'Desktop'),
  PARTITION P_SALES VALUES IN('Tennis', 'Soccer')
);
```

### 분리와 병합
결국 Range Partition에서 `LESS THAN` 대신 `VALUES IN`을 사용한다는 것 외에는 전부 똑같이 `REORGANIZE PARTITON`을 사용하면 된다. <br>
주의할 점은 역시나 비슷하다. `MAXVALUE` 파티션을 정의할 수 없다는 점과 NULL이 들어갈 곳을 지정할 수 있다는 것이다. <br> 

# 3. Hash Partition

Hash Partition은 해시 함수로 레코드가 들어가게 될 파티션이 결정된다. <Br>
사실 "파티셔닝", "샤딩" 개념을 배울 때 항상 이 파티션을 예시로 배웠던 것 만큼 대부분에게 익숙할듯 하고, 실무 SNS 서비스에서도 비슷한 형태로 자주 쓰이는 것 같다. <Br> 

MySQL 해시 함수는 **사용자가 정의한 파티션 키나 표현식 값에 "파티션 갯수"를 나눈 값으로 파티션을 결정한다.** `표현식 % 파티션 갯수` 뭐 별거 없다. <br>
이렇게 계산하는 만큼, **사용자가 정의한 파티션 키나 표현식의 값은 정수 타입이거나, 정수 타입을 반환하는 표현식이여야 한다.** <br>

파티션의 추가 삭제에 대한 엄청난 재분배가 일어날 수 밖에 없다. 예를 들어 이제까지 파티션을 5개만 사용중이었는데, 6개가 되어 버린다면, 앞으로 값을 찾을 때 `파티션 키 % 6`을 사용해 값을 찾게 될 것이다. <br>
만약 재분배가 없다면 기존 값을 찾을 수 없게 된다! 예를 들어 id값이 11인 값을 찾고 싶을 때, 파티션이 5개일 때는 `11 % 5 = 1`인 `1번 파티션`에 데이터가 저장 되어 있을텐데, 파티션 갯수가 6개라면 `11 % 6 = 5`인 `5번 파티션`에 저장되어 있는게 정상이다. <br>
따라서, 파티션이 하나 늘고 줄을 때마다 재분배가 필요하고, 재분배가 적을 것으로 예상될 때 사용하던지, 다른 대안을 생각해야 한다. ex) [안정해시](https://binux.tistory.com/119) <Br>


## 3.1 용도
해시 파티션은 아래와 같은 테이블에서 적합하다.
1. **Range Partition이나 List Partiton으로 테이블을 균등하게 나누기 어렵다.** <br> 예를 들어 카테고리별로 상품을 나누는데, "치킨" 카테고리에만 상품이 엄~청 많고 "취두부" 카테고리에는 상품이 별로 없을 수도 있다. 이 경우 어떤 테이블은 뚱뚱해지고, 어떤 테이블은 날씬해진다. 이 경우 차라리 Hash 해버리면, 오히려 균등할 수도 있다.
2. **테이블의 모든 레코드가 비슷한 사용 빈도를 보이지만, 테이블이 너무 클 때** (사실상 그냥 테이블이 큰 경우)

<br> <br>

대표적으로 회원 테이블! 회원 정보는 가입 일자가 오래 되었다고 덜 사용되지도, 최근 가입 회원이라고 더 자주 사용하지도 않는다. 취미, 사는 지역 등 어떤 "칼럽 값" 하나로 사용이 빈번하고 많고가 결정되진 않는다. 결국 [유명인 빼고는](https://www.rkenmi.com/posts/sharding-user-ids-of-celebrities) 균등하게 사용이 된다. <br>

## 3.2 파티션 생성
```sql
  CREATE TABLE employees (
  
  ...

  ) PARTITION BY HASH (id) PARTITIONS 4 (

    PARTITON p0 ENGINE=INNODB,
    PARTITON p1 ENGINE=INNODB,
    PARTITON p2 ENGINE=INNODB
  );

```

`PARTITION BY HASH`로 해시 파티션임을 지정하고, id값을 기준으로 함을 명시했다. 그리고 `PARTITIONS 4`라는 키워드로 4개의 파티션을 생성할 것을 정의했다. 아래는 파티션의 이름을 명시하기 위해 적었지만, 원래도 p0, p1, p2와 같이 알아서 지정된다. <br> 사실 해시 파티션에선 특정 파티션을 지정해서 삭제하거나 병합할 일이 별로 업식 때문에, 이름을 짓는 것이 별로 의미는 없음


## 3.3 파티션의 추가
죽음의 재분배 Time..을 수반한 파티션 추가. 명령어 자체는 간단하다.
<br>

1. 파티션 1개 추가 + 파티션 이름 부여
```sql
ALTER TABLE employees ALGORITHM=INPLACE, LOCK=SHARED,
    ADD PARTITION(PARTITION p5 ENGINE=INNODB);
```

<Br>

2. 파티션 6개 추가 + 이름 부여 X
```sql
ALTER TABLE employees ALGORITHM=INPLACE, LOCK=SHARED,
    ADD PARTITION PARTITIONS 6;
```

<br>

위 명령어들을 입력하면, 모든 파티션에 있는 데이터들이 재분배된다. 기존 테이블들에 읽기 잠금이 걸리게 되고, 많은 부하가 발생된다.

<Br>

## 3.4 나머지 연산들
### 삭제
해시 파티션은 파티션 단위로 레코드를 삭제할 수 없다. 단순히 DROP 명령어를 쓸 수 없다. 애초에 의미 없이 해쉬값으로만 나눈 것이기 때문에, 지우는 거슨 의미도 없고 해서도 안된다. 거기에 뭐가 있는줄 알고?


<Br>

### 분할 - 없음
### 병합- 없다!!
단, 파티션 갯수를 줄이고, 재구성할 수 있다.

```sql
ALTER TABLE employees ALGORITHM=INPLACE, LOCK=SHARED
    COALESCE PARTITION 1;
```

이렇게 입력한다면 **파티션이 1개 줄어든다! 1개가 되는 것이 아님 ㅇㅇ**

### 주의사항
1. 특정 파티션만 삭제할 수는 없다 `DROP PARTITION`
2. 새로운 파티션을 추가, 삭제 하는 작업은 전면 재배치가 일어난다..
3. 해시 파티션은 다른 파티션과는 아예 방식이 다르기 때문에, 용도가 적합한지 확실히 해라.

# 4. Key Partition

Key Partition은 Hash Partition과 사용법이나 특성이 같다 <br> 
Hash Partition은 사용자가 파티션 키나 표현식을 통해 해시 값 계산을 어느 정도 명시할 수 있다. MySQL 서버는 그 결과값에 MOD를 적용하는 것이다. Key Partition은 조금 다르다. 

다만, Key Partition은 사용자가 `파티션 키 값`까지만 딱 정할 수 있고, MySQL이 해시함수인 `MD5()`를 적용한다. 그 다음 또 MOD값을 적용한다. **대신 Hash Partition과 다르게 정수형이 아니어도 된다는 장점이 있다.**

<br>

쿼리는 아래와 같이 작성한다

```sql
PARTITION BY KEY() PARTITIONS 2; 
```

1. `PARTITONS 2`로 파티션 갯수를 지정할 수 있다.
2. 괄호의 내용을 비워 두는 경우 Primary Key의 모든 칼럼이 파티션 키가 된다.
3. 프라이머리 키가 없는 경우 유니크 키가 존재한다면 파티션 키로 사용된다.
4. 프라이머리 키나, 유니크 키를 구성하는 컬럼 중에서 일부를 선택해 파티션 키로 설정할 수 있다.
5. 유니크 키를 파티션 키로 사용할 때, 해당 유니크 키는 반드시 NOT NULL이어야 한다.

<Br>


