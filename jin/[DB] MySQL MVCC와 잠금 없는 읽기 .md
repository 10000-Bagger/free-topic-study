# Multi Version Concurrency Control


# 1. MVCC란
MVCC는 레코드 레벨의 트랜잭션을 지원하는 DBMS들이 제공하는 기능이며, MVCC의 주된 목적은 Lock 없는 "일관된" 읽기를 제공하는 것이다. <br>

일반적인 Locking 방식은, 여러 스레드가 동시에 Read를 시도할 때는 Lock 없이 접근 가능하나, 문제는 한 스레드라도 레코드에 대한 Write Lock을 얻는 경우, 다른 스레드들이 Read조차 할 수 없는 문제가 있었다. 이 때문에 트랜잭션 처리량은 급격히 낮아질 수 밖에 없었다. <br>
MVCC는 Multi Version Concurrency Control로 "Multi Version"이라는 표현은 하나의 레코드에 여러 개의 버전이 동시에 관리된다는 뜻이다 <br>
즉 MVCC는 다른 스레드가 Write를 위해 Lock을 획득한 경우에도, 다른 버전을 읽는 것을 허용하는 등의 방벅으로 Read를 허용할 수 있게 하는 것이 목적이다. (물론 Write Lock끼리는 서로를 기다려야 한다.) <br>
InnoDB는 Undo Log를 통해 MVCC를 구현했다. <br>
(의도적으로 Update를 위한 Read시 Lock을 걸고 싶다면, 쿼리에 "FOR UPDATE"를 붙여주면 된다. - Locking Read)

## 1.1 데이터 변경시 일어나는 일
READ_COMMITTED 격리 수준에서 동작을 살펴보자. <br>
아래는 Insert를 통해 레코드가 삽입된 모습이다. 버퍼 풀과 데이터 파일에 레코드가 저장된다. 

<Br>

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/47cd904a-f824-48dc-92b4-e1cdc012ff92)

<br>

만약 위 레코드의 필드에 UPDATE 쿼리가 적용됐다고 생각해보자. m_area를 '경기'로 바꾸는 예시이다. 

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/08471032-8665-475d-bcf5-14bd9e593702)

Commit이나, Rollback 전에, <br>
체크 포인트나, InnoDB Write 스레드에 의해 기록되는 실제 데이터는 정확히 언제 바뀌게 될지는 모르겠지만, (Disk에 정확히 언제 쓰이게 될지는 모르겠지만) **버퍼 풀에 저장된 레코드 데이터는 변화했고, WAL에 의해 기존 값을 Undo Log에 기록한다.** 트랜잭션 실패시 트랜잭션 중의 변경사항을 다시 되돌려야 하는데, 이를 위해 Undo Log에 기록한다. 물론 InnoDB는 ACID를 보장하기 때문에, 일반적으로 버퍼 풀 Data와 디스크 데이터 파일은 동일하다고 가정해도 된다.

<br> <br>

이때, 아직 Commit이나, Rollback이 되지 않은 현 상황에서, 다른 사용자가 작업중인 `id 12` 레코드를 조회하면 어디에 있는 데이터를 조회할까? <br> 

**답은 "MySQL 서버의 격리 수준에 따라 다르다."이다.** <Br> 

## 1.2 격리 수준별 MVCC 작동

### 1.1.1 READ_UNCOMMITTED
격리수준이 Read Uncommitted일 때는, 아직 Commit 되지 않은 데이터도 읽는다. 어떻게 아직 Commit 되지 않은 값을 Lock없이 읽게 허용해줄까? <Br> 

**-> InnoDB 버퍼풀에 있는 데이터를 읽어서 반환한다.** <Br>
InnoDB 버퍼풀에 있는 데이터는 아직 Commit 되었는지 되지 않았는지 확실하지 않다. 단지 InnoDB 버퍼풀에 있는 데이터를 주는 것만으로도 손 쉽게 Lock 없는 Read Uncommitted 구현이 가능하지 않겠는가?


### 1.1.2 READ_COMMITTED 이상
Read Committed는 오직 커밋된 데이터만 읽겠다는 격리 수준이다. 그 이상의 격리수준들인 Repeatable Read와 Serializable 또한 오직 커밋된 데이터만 읽는다. <Br> 
어떻게 Lock없이 빠르게 Commit된 데이터를 제공해줄 수 있을까? <br>
해답은 Undo Log에 있다. 데이터베이스는 어떤 트랜잭션이 만들어낸 변경 사항들을 Rollback할 수 있도록 Undo Log를 운용한다. 데이터가 실제로 물리적 디스크게 저장되기 전에 이 Undo Log에 쓰여야 Undo 할 수 있을 것이다. (WAL) <br>
**그렇다면 이 Undo Log의 데이터를 읽게 해주면 되지 않겠는가?** <br>

**~~InnoDB 버퍼 풀이나, 데이터 파일에 저장된 실제 데이터 대신~~ 변경되기 이전의 내용을 보관하고 있는 Undo 영역의 데이터를 반환하면 Lock 없이 Commit된, (혹은 그럴 것으로 추측되는) 데이터를 반환해줄 수 있다.** <br> <br>

### 1.1.3 Serializable
1. MySQL에서는 MVCC가 아닌 Lock 방식으로 작동하게 된다.
2. Postgresql에서는 [SSI](https://drkp.net/papers/ssi-vldb12.pdf)라는 기법이 적용된 MVCC로 동작한다.

### 1.2 MVCC 정리
이렇게 같은 데이터지만 여러 버전을 가지고 있고, 필요에 따라 데이터를 보여주므로, 이것을 MVCC라고 부르는 것이다.  <Br>

만약 데이터가 **Commit 된다면, InnoDB는 현재 버퍼풀의 데이터를 영구적인 데이터로 만들어 버린다. 이때 Undo 영역의 백업 데이터가 항상 바로 삭제되지는 않는다. 이 Undo 영역을 필요로 하는 트랜잭션이 없을 떄 비로소 삭제 된다.**  <br>

따라서 Undo에서 관리해야 하는 예전 버전의 데이터는 트랜잭션이 길어지면, 삭제되지 못하고 오래 관리되며, 무한히 많아질 수 있다. (언두 영역이 저장되는 System Table Space 공간이 많이 늘어나게 될 수도 있음) <br>

그리고 데이터가 **Rollback 된다면 Undo 영역의 데이터들을 InnoDB 버퍼 풀로 복구 시킨 다음 Undo 영역 내용을 지워버린다.** <Br> <br>

이러한 MVCC 덕분에, 읽기 작업시 레코드에 Lock을 걸지 않고도 데이터를 읽을 수 있다.


## 2. Non-Locking Consistent Read - 잠금 없는 일관된 읽기

InnoDB 스토리지 엔진은 MVCC를 통해 Lock 없이 Read 작업을 수행할 수 있다. **덕분에, Read 작업은 다른 트랜잭션이 가진 Lock을 기다리지 않는다.** <Br>

격리 수준이 SERIALIZABLE 미만인 경우, INSERT와 연결되지 않는 순수한 SELECT 작업은 다른 트랜잭션의 변경 작업과 무관하게 항상 Lock 대기 없이 바로 실행된다. <br> 
아래 그림과 같이 어떤 트랜잭션이 레코드를 변경 중이고, 아직 커밋되지 않았더라도 이 변경 트랜잭션이 다른 사용자의 SELECT 작업을 방해하지 않는다. 이를 "잠금 없는 일관된 읽기" 또는 Non-Locking Consistent Read라고 부른다. <Br>

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/a2efb813-f214-4344-bceb-dee6158f8da4)

InnoDB에서는 변경 전 데이터를 읽기 위해 Undo Log를 사용한다.

### 단점도 있다! - "잠금 없는 일관된 읽기"

만약 어떤 트랜잭션이 오랜 시간 활성 상태로 놓여 있다면, MySQL 서버가 느려질 수도 있다! <br>
바로, 잠금 없는 일관된 읽기를 제공하기 위해, Undo Log를 삭제하지 못하고 계~속 유지해야 하기 떄문에 발생한다. <br>
따라서, 트랜잭션이 시작됐다면 가능한 한 빨리 Commit이던, Rollback이던, 트랜잭션을 완료하는 것이 좋다.
