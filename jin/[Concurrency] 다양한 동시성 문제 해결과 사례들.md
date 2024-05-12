# 다양한 동시성 이슈 해결 방식들과 기업 사례들
1. Java가 제공해 주는 기능 활용
   1. Synchronized
   3. ReentrantLock과 ConcurrentHashMap 활용
2. DB와 JPA 제공해 주는 기능 활용
   1. Select For Update 쿼리 (Pessimistic Lock)
   2. Optimistic Lock (JPA 제공)
   3. Named Lock (MySQL Locking Function - 우아한 형제들 사례)
3. Redis 활용
   1. Lecttuce (setnx + Pub/Sub - 채널톡 사례)
   2. Redisson (Lock Interface - 컬리 사례)
4. Zookeeper 활용
5. 특이 사례 : STW와 네트워크 지연으로도 동시성 문제가 발생할 수 있다.


# 동시성 이슈

하나의 자원에 2개 이상의 작업 주체가 접근할 수 있는 상황에서, 자원을 사용하는 방식이 Atomic 하지 않는 경우 상태 동기화 발생할 수 있다. <br>
예를 들어 자원의 상태를 변경하는 작업은 보통 Atomic 하지 않은데, 아래와 같이 여러 단계로 수행될 가능성이 높다.

1. 자원의 현재 상태를 확인한다.
2. 현재 상태에 무언가 연산을 한다.
3. 연산의 결과를 자원의 새로운 상태로 Update한다.

예를 들어 사과 5개 중 3개를 가져오는 상황을 생각해보자. <br>
스레드 1이 사과의 갯수가 5개인 것을 확인했고, `5 - 3`을 계산해 남은 갯수는 2임을 확정 지었다. 이제 "사과의 갯수"를 2로 바꾸어 저장하기 직전, 멀티 스레드 환경이어서 다른 스레드 2가 찾아왔고, 또 같은 연산을 수행한다. <br>
스레드 1이 사과의 갯수를 2개로 저장하기 전이기 때문에, 스레드 2가 파악한 현재 사과 갯수는 5개이고, `5 - 3 = 2`를 남은 갯수로 저장해버린다. 이후 스레드 1도 마저 "2"를 남은 갯수로 저장할 것이다. <br>
원래대로라면 사과는 5개 밖에 없으므로, 한 스레드는 3개를 가져가는 것에 실패했어야 정상이다. <br>
이는 자원이 공유중이고, 여러 작업 주체가 자원을 건들 수 있다면 어디서든 발생할 수 있다. <br>

이런 문제를 해결하기 위한 여러가지 방법들을 간단하게 알아보자.
# 1. Java가 제공해 주는 기능 활용

## 1.1 Java Synchronized 사용
Java `Synchronized` 키워드는 특정 블럭이나, 메서드에 적용할 수 있고, 해당 블럭에 한 스레드만 접근할 수 있도록 돕는다.

```java
public synchronized void eatApple(Long quantity) {
    AppleStock appleStock = fruitStockRepository.getAppleStock();
    appleStock.eat(quantity);
    fruitStockRepository.save(appleStock);
}
```
예를 들어 위와 같이 메서드에 `synchronized`를 걸어주면, 위 메서드에는 한개의 스레드만 접근이 가능하다. 혹은 블럭 단위로 진입을 막을 수도 있는데, 더욱 자세한 설명은 다른 글을 참고하자 [synchronized 키워드란? - 느리더라도 꾸준하게](https://steady-coding.tistory.com/556) <br> <br>

synchronized를 사용해 사과의 갯수를 파악하고, 줄이고, 저장하는 과정에 한개의 스레드만 접근할 수 있게 해준다면, 재고를 관리하는 메서드가 eatApple하나라면 갯수가 잘못 저장되는 문제는 발생하지 않을 것이다. <br>
하지만 이런 방법이 항상 먹히는 것은 아니다.


## 1.1.1 Java Synchronized 활용 방법의 문제점
일단 다양한 문제가 있을 수 있다.
1. **재고를 변경시키는 메서드가 또 있다면?** - 갯수를 늘리는 메서드가 있다면, 해당 메서드는 여전히 접근 가능할 것이다. 
2. 자바 `synchronized`는 하나의 프로세스 안에서만 스레드 동시 접근을 막을 수 있기 때문에, **만약 여러 서버에서 접근할 수 있는 곳에 데이터가 저장되어 있다면, 똑같이 RaceCondition이 발생한다.** <br> 예를 들어 사과가 DB에 저장되어 있고, Application이 여러대라면 똑같은 동시성 이슈가 발생할 수 있다.
3. `synchronized` 키워드와 springframework가 제공하는 `@Transactional` 키워드를 같이 쓰는 경우 동시성 보장이 안 된다. **왜냐하면, `synchronized`는 프록시 전체를 감싸지 못해서, 메서드 호출 이후 작은 틈이 생기기 때문이다.**

<br> <br>

3번에 대해서 부연하겠다. `@Trnasactional`은 AOP 방식으로 작동하며, 프록시를 사용한다. 예를 들어 메서드에 `@Trnasactional`과 `synchrinoized`이 걸려 있다면, 프록시에 새로 선언된 메서드는 아래와 같은 형태로 생겼을 것이다.

```java
// 프록시 클래스의 eatApple
public void eatApple(Long quantity) {
  try (connection) {
    // 트랜잭션 시작 부분
    startTransaction();

    // 실제 메서드 호출 부분
    fruitService.eatApple(quantity);

    // commit
    doCommit();

  } catch(SQLException e) { 
    // rollback
    rollback();
  } 
}
```

내가 만든 메서드를 위와 같은 트랜잭션 코드들 사이에 넣어 호출할 것이다. <br>
잘 보면, synchronized가 실제로 걸리게 되는 부분은 `fruitService.eatApple(quantity)` 부분일 것이다. 그리고 DB 변경 사항이 실제로 저장되는 것은 `commitTransaction`이 호출된 이후일 것이다. <br> 
결국 `fruitService.eatApple(quantity)` 이후 실제로 변경 사항이 Commit 되기 까지 작은 틈새들이 생기게 된다! <br>
`5 - 3 = 2`를 계산한 이후, 엔티티에는 해당 값을 썼지만, 실제로 DB에 저장 요청을 보내고 Commit을 수행하기 전에 다른 스레드가 값을 Read한다면.. 잘못된 값을 읽게 되는 것이다. <br>
**이래서 원래 접근을 막을 때는 다른 트랜잭션이 끝난 이후, 업데이트가 전부 끝난 이후까지 막아야 한다.** 나중에 락 부분에서 언급하겠지만, 락을 사용하는 경우에도 트랜잭션 커밋 이후 락을 반환해야 한다. <Br> <br>

synchronized를 통해 동시성 이슈를 해결하려면 이 문제들을 모두 이해하고 하나의 서버만 돌아가는 곳에서 쓰던지, `@Transactional` 없이 사용하던지, 해당 메서드보다 큰 범위의 synchronized 블럭을 만들어 내던지.. 위에서 언급한 부분들을 조심해 가며 막아내야 한다.

## 1.2 ReentrantLock을 활용

synchronized 외에도 Java 5 부터 추가된 java.util.concurrent.lock에서 제공되는 다양한 Lock 객체를 활용해 해결할 수도 있다. <br>
그 중 ReentrantLock을 활용하여 문제를 해결해보자. <br> 
ReentrantLock는 Lock을 제공해주는 객체로, RenntrntLock 인스턴스별로 접근을 제한해준다.

```java
  ReentrantLock reentrantLock = new ReentrantLock();
  
  if (reentrantLock.tryLock(timeout, unit)) {
    // 수행
  }
  reentrantLock.unlock();
```

`tryLock` 메서드를 통해 Lock을 얻을 수 있고, 다른 곳에서 (ex 다른 스레드) 같은 인스턴스를 이용해 tryLock을 호출하는 경우, 먼저 lock을 얻는 곳에서 `unlock` 메서드를 호출할 때까지 대기한다.  <br>
대기 시간을 `tryLock` 호출 시 함께 넣어줄 수 있는데, 이를 이용해 획득 시도 시간을 제한할 수 있다. <br> <br>


사용자별로 Lock을 만들 수 있게 하고, 다른 작업주체가 접근하지 못하게 할 범위를 결정한 다음 락을 구현하면 될 것이다. 예를 들어, 하나의 레코드에 접근하지 못하게 하려면 레코드 PK, 엔티티의 식별자를 활용해 락을 구현하면 될 것이다. 어떤 회원의 id가 3이고 이 회원의 정보 변경에 대한 락을 잡고 싶다면, 회원의 id값인 3을 활용하면 될 것이다. <br>
주의해야 할 점도 있다. 이러한 Lock을 얻기 위해 다른 스레드들이 너무 오랜 시간 대기할 수도 있고, 로직이 복잡해지면서 예상치 못한 무한 대기나 데드락을 대비하기 위해서, 대기 시간이나 재시도 횟수를 적당하게 정해 주는 것이 좋다. <br>
위에서 언급한 부분들을 고려해 아래와 같이 구현할 수 있을 것이다.
```java
public class ExclusiveRunner {
    private final ConcurrentHashMap<String, CountedLock> locks = new ConcurrentHashMap<>();

    public <T> T call(String key, Duration tryLockTimeout, Callable<T> callable) throws TimeoutException {
        CountedLock lock = locks.computeIfAbsent(key, k -> new CountedLock());
        lock.increase();
        try {
            if (lock.tryLock(tryLockTimeout.toMillis(), TimeUnit.MICROSECONDS)) {
                return callable.call();
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        } finally {
            decreaseLockCount(key, lock);
            lock.unlock();
        }
        throw new TimeoutException("timeout~");
    }

    private void decreaseLockCount(String key, CountedLock lock) {
        int count = lock.decreaseAndGet();
        if (count == 0) {
            locks.remove(key, lock);
        }
    }
}
```

좋은 구현인지는 모르겠다. ConcurrnetHashMap을 이용해 특정 key에 대한 객체를 저장해준다. 그리고, ReentrantLock을 컴포지션으로 갖고, 사용중인 스레드 갯수를 세는 CountedLock을 만들어 보았다. AtomicInteger로 세든, 갯수를 조정하는 메서드를 synchronized로 선언하든, 갯수는 주의해서 세야할 것이다. 그리고 사용하는 곳이 없는 경우 락을 지운다. <br>
unlock은 finally에서 호출되게 하여 무조건 unlock이 되도록 하고, 만약 `tryLock`이 제한 시간이 넘도록 계속 예외가 발생한다면 TimeoutException을 던지도록 구현했으나, 실제로 사용할 때는 리트라이 로직을 넣을 것 같다. <br>


# 2. DB와 JPA가 제공해주는 기술을 활용한 해결
이번에는 DB와 JPA가 제공해주는 기능을 활용해 문제를 해결해보자. <br>
첫 번째로는 격리 수준 자체를 바꾸는 방법이 있다. <br>
기본적으로 MySQL InnoDB는 `Repeatable Read`, Postgresql은 `Read Comitted`를 격리수준으로 설정 되어 있다. 격리 수준을 바꿈으로써 몇 가지 정도의 동시성 문제는 해결할 수 있지만, 성능을 매우 저하 시키기 때문에, 좋은 방법이라고 하긴 어렵다. 기본 쿼리나 DB 수준에서 제공되는 Lock들을 활용해 해결해보자. <Br>

## 2.1 `SELECT FOR UPDATE` Query (Pessimistic Lock)

Select For Update는 MySQL에서 8.0 부터 사용할 수 있는 쿼리의 한 종류로, 말 그대로 Update를 위한 Select를 제공해주는데, **정확한 값 Update를 할 수 있도록 검색된 모든 행과 팬텀 리드가 발생할 수 있는 레코드에 대해, 다른 트랜잭션의 접근을 막아준다.** <br>

```sql
SELECT * FROM fruits f WHERE f.name = 'apple' FOR UPDATE;
```

간단하게 DB 수준에서 동시성 이슈를 막아줄 수 있다. <Br>
하지만 언급한 것과 같이 검색된 행 뿐만 아니라 팬텀 리드가 발생할 수 있는 레코드에도 Lock이 걸리게 된다. 물론 DB에 따라 다른데, 이는 **MySQL에서는 Gap Lock 때문이다.** 갭락은 예를 들어 이름을 `LIKE = 'L%'`로 검색했을 때, 실제 L로 시작하는 레코드만 잠그는게 아니다. 실제 레코드들은 레코드 락이 걸리게 되고, **모든 L로 시작하는 이름의 insert를 막는다.** 이를 Gap Lock이라고 한다. <br>
따라서 조건에 따라 락의 범위가 클 수 있고, 성능 저하나 데드락의 원인이 될 수 있기 때문에, 대기 시간이나 옵션을 잘 사용해야 한다. <br>
옵션들
1. `NOWAIT` : `NOWAIT`은 Lock을 얻을 수 없는 경우 대기하지 않고 즉시 에러를 발생시키는 옵션이다. `FOR UPDATE NOWAIT`와 같이 사용한다.
2. `SKIP LOCKED` : SKIP LOCKED 옵션은 다른 트랜잭션이 이미 Lock을 획득한 행을 건너뛰고, Lock이 없는 행만 반환한다. 
3. `WAIT T` : `WAIT T` 옵션은 원하는 초 만큼 Lock을 얻기 위해 대기하도록 설정해줄 수 있고, 시간이 넘어가면 에러를 발생시킨다! **가급적 이 옵션을 사용하는 것이 좋다.**  <Br> 5초를 정지 시키고 싶은 경우 `UPDATE WAIT 5`를 붙여주면 된다.

<Br>

조사하면서 느낀 점인데, `SELECT FOR UPDATE`는 병목과 데드락의 원인이 되는 경우가 많아서 그런지 대부분의 사람들이 최대한 Application 단에서 해결할 수 있으면 App단에서 해결하려는 것 같다. <br>
어떤 DBA가 작성하신 글을 보면 회사에서는 `SELECT FOR UPDATE`를 쓰는 부분이 있다면 꼭 DBA에게 보고하라고 한다. 이후 해당 로직과 쿼리를 `특별 관리 대상`에 포함한다고 한다. 그래서 최대한 안 하려면 안 하고 싶어한다는 느낌을 받게 되었다. <br> <br>

Jpa와 함께 아주 간단하게 사용할 수도 있다. 


```java
public interface StockRepository extends JpaRepository<Stock, Long> {

    @Lock(value = LockModeType.PESSIMISTIC_WRITE)
    @Query("select s from Stock s where s.id = :id")
    Stock findById(Long id);
}
```

위와 같이 `@Qurey`와 함께 Native Query를 작성해주고 `@Lock(value = LockModeType.PESSIMISTIC_WRITE)`을 통해 손쉽게 설정할 수 있다. <br>
쿼리 발행을 확인해 보면, 맨 끝에 `FOR UPDATE`가 붙어서 발행된다! <br> <br>


코드에선 가장 기본적인 `PESSIMISTIC_WRITE` 옵션을 사용했는데, 다른 옵션을 사용할 수도 있다. <br>
1. Shared Lock을 활용하고 싶다면, `@Lock(value = LockModeType.PESSIMISTIC_READ)`
2. `NOWAIT` 옵션을 사용하고 싶다면, `@Lock(value = LockModeType.PESSIMISTIC_FORCE_INCREMENT)`

## 2.2 Optimistic Lock With JPA

실제로 Lock을 이용하지 않고 따로 버전을 저장한다. 이 버전 값을 활용해 정합성을 맞춘다. <Br> 

먼저 데이터를 가져올 때, 버전값을 확인했다가, **실제 `UPDATE` 쿼리를 날리는 시점에 버전을 다시 확인한다. 이때, DB에 저장된 버전이 처음 SELECT시의 버전과 다르면 트랜잭션을 롤백한다!** 데이터가 성공적으로 Commit되면 버전 값을 업데이트 한다.

<br> <br>

이 버전 값을 엔티티에 추가하면, JPA가 관리해준다. 데이터가 update될 때마다 값을 늘려주는데, 검색 쿼리에 `WHERE version = 저장한 버전` 내용을 붙여 준다. 그래서 버전이 달라지면 쿼리가 실패하는 것이다.


<br>

JPA와 구현하는 법을 살펴보자. 일단 엔티티에 `@Version` 어노테이션이 달린 field가 추가 되어야 한다.
```java
  @Version
  private Long version;
``` 

이 `@Version` 어노테이션은 숫자형 int, long, short와 timestamp 형식(DB의)에 적용될 수 있다. <Br>

이후 아래와 같이 재시도 로직을 작성해 준다.

```java
public void decrease(Long id, Long quantity) throws InterruptedException {
    while (true) {
        try {
            optimisticLockStockService.decrease(id, quantity);
            break;
        } catch (Exception e) {
            /* 실패한 경우 50 milli second 후에 재시도된다. */
            Thread.sleep(50);
        }
    }
}
```

별도의 락을 잡지 않고 저장된 버전을 통해 판단하므로, 경쟁 상황이 그리 심하지 않은 경우 `Pessimistic Lock`보다 성능이 좋다! <br>
하지만..
1. 재시도하는 로직을 프로그래머가 직접 작성해줘야 해서 번거롭고, 실수할 수도 있다. (버전이 다른 경우 트랜잭션이 실패하기 때문에, 저장해야 한다면 재시도 로직을 작성해야 한다.)
2. Entity 객체에 version field를 추가해야 한다. -> 추가 관리 포인트가 될 수 있다.
3. **버전 값이 달라져 업데이트가 실패하는 경우가 많은 경우, 요청을 여러번 보내야 하므로 Pessimistic Lock 보다 성능이 떨어진다.** 예를 들어 100명이 동시에 요청을 보내는 경우 99명이 실패해서 재시도를 하게 된다. 99명은 또 동시에 보내서 98명이 재시도를 하게 된다.. 그래서 (100 + 1) * 50 번의 쿼리가 발행된다. 조심..해야겠지?

<br>



## 2.3 Named Lock (MySQL Locking Function)

이름을 가진 metadata locking 이다. 이름을 가진 lock을 획득한 후, 해제할 때까지 다른 세션은 이 lock을 획득할 수 없게 한다. <br> 
예를 들어 "치킨"이라는 이름으로 Lock을 얻는다면, 같은 이름을 가진 락에 대해 접근을 막아준다. <br>
앞서 보인 ReentrntLock과 ConcurrentHashMap을 사용한 방법과 거의 유사하다. <br>
MySQL에서 기본적으로 제공해주는 [Locking Function](https://dev.mysql.com/doc/refman/8.0/en/locking-functions.html)들인 `get_lock()`이나, `release_lock()`등을 이용해 구현할 수 있다. JPA로 사용할 때는 아래와 같이 LockRepository를 선언한 다음 Native Qurey를 아래와 같이 작성해준다. 

```java
public interface LockRepository extends JpaRepository<Stock, Long> {

    @Query(value = "select get_lock(:key, 3000)", nativeQuery = true)
    void getLock(String key);

    @Query(value = "select release_lock(:key)", nativeQuery = true)
    void releaseLock(String key);
}
```

쿼리를 보면 String 값의 key가 있는데, 특정 값을 통해 락을 제어할 수 있다는 것이 장점이다. 예를 들어 레코드의 PK를 Lock의 값으로 쓰면, 한 레코드 단위로 락을 걸 수 있을 것이다. 이러한 이름으로 구분되는 key를 lock에 사용한다고 해서 Named Lock이다. 

<br>

잘 보면 `get_lock`의 두번째 파라미터로 숫자를 넣어주는데, 간편하게 Lock 타임 아웃 시간을 설정할 수 있어서 좋다. <br>

```java

  private static final String APPLE = "APPLE";
  public void eatApple(Long quantity) {
      try {
          lockRepository.getLock(APPLE);
          fruitService.eatApple(quantity);
      } finally {
          lockRepository.releaseLock(APPLE);
      }
  }
```

이후 위와 같이 사용한다. `eatApple`을 수행하기 전, 이름을 통해 락을 얻고, finally를 통해 해제한다. 만약 식별자가 있다면 식별자를 통해 락을 잡을 수 있을 것이다. <br>

Pessimistic Lock과 Exclusive하다는 점은 비슷하다. **Pessimistic Lock(SELECT FOR UPDATE)은 Row나 Table에 락을 건다면, Named Lock은 메타데이터에 락을 걸게 된다는 차이가 있다.** 주로 분산락을 구현할 때 사용된다. <br>

또한 Pessimistic Lock은 타임 아웃 구현이 어렵지만, Named Lock은 위와 같이 간단한 쿼리문 작성만으로 손쉽게 구현할 수 있다는 것이 장점이다. 또한 단순 Insert시에도 정합성을 맞추는 데에 활용할 수 있다. <br>
주의할 점으로는 transaction이 종료될 때 이 lock이 자동으로 해제되지 않으므로 별도의 명령어로 해제를 수행해주거나, 선점 시간이 끝나야 해제된다. <br> 
그래서 트랜잭션 종료시 락 헤제와 세션관리를 잘 해줘야 한다.

### 2.3.1 우아한 형제들 Named Lock 사례

우형 비즈인프라 개발팀에서도 광고 시스템에서 발생한 동시성 관리 문제를 MySQL Named Lock을 사용해 분산락을 만들어 해결했다. <Br>
문제 상황은 유저 신용카드 등록 갯수 제한을 Application 단에서 관리하고 있는데, 그 과정에서 동시성 문제가 발생한 것이다. <br>

다른 기술로는 ZooKeeper, Redis를 고려했었지만, 두 기술이 사용되고 있지 않았는지 추가적인 인프라 구축 비용과 유지보수의 문제가 있었다. <br>
반면 MySQL은 프로젝트 초반 부터 사용해왔기에 추가적인 비용이 없고 Named Lock의 "이름"을 Application 단에서 제어할 수 있으므로, 이를 활용했다고 한다.

- [MySQL을 이용한 분산락으로 여러 서버에 걸친 동시성 관리](https://techblog.woowahan.com/2631/)


# 3. 레디스를 활용한 방식
인-메모리 DB인 레디스를 활용해 분산 락을 구현할 수 있다. <br>
여러 대의 서버가 있는 상황에서는 앞서 언급했던 방법 중, Java를 활용한 방법으로는 문제를 해결하기 어려울 것이다. <Br> 
그래서 보통은 DB를 활용하던지, 아니면 서버들이 공유하는 메모리 DB인 레디스를 활용해 락을 구현하기도 한다. <Br> <br>
Redis 연산 중 `SETNX`는 `SET if Not eXists`의 줄임말로, 어떤 값이 현재 저장되어 있지 않다면 저장하고, 이미 저장되어 있다면 저장하지 않는 연산이다. Redis는 데이터를 읽고 쓸 때, 싱글 스레드로 작동하기 때문에 어떤 값이 존재하냐 존재하지 않냐 여부를 확인할 때, 동시성 문제가 발생하지 않으므로 이 SETNX를 활용해 락을 구현할 수 있다. <Br>
예를 들어 "key:1"이라는 값이 현재 저장되어 있지 않다면, 새로 저장하고 저장에 성공한 상태를 락을 획득했다고 본다. 다른 작업 작업 주체들은 "key:1"이라는 값이 이미 있는 경우 이미 락을 누군가 가지고 있다고 판단하여 획득에 실패하는 것이다. 자원을 다 사용한 이후, 저장된 "key:1"를 삭제하는데 이 행위를 락을 해제한 것으로 본다. <br> 
이후 대기하고 있던 다른 작업 주체가 다시 저장을 시도했을 때 성공하게 되므로, 락을 획득할 수 있는 것이다. <br> 
읽고 쓰는 작업이 싱글 스레드로 동작하기 때문에 위 과정은 원자성이 보장된다. <br> <br>

보통 Application 단에서 레디스를 사용하기 위해 다양한 클라이언트 라이브러리를 사용하는데, 이들이 제공해주는 인터페이스에 따라 구체적인 코드는 달라질 수 있다. <br>
그리고 Lock 대기시 redis가 지원해주는 pub/sub 기능을 통해 spin lock으로 구현하는 것을 피할 수 있는데, `wait-signal` 방식을 pub/sub 기능으로 구현한 것이다. <br>
이러한 Redis를 활용한 방식은 DB를 사용하는 것에 비해 DB에게 주는 부담을 크게 줄여줄 수 있으므로 이미 Redis를 이미 사용하는 조직에서는 보통 Redis를 활용해 분산락을 구현하는 것 같다. <br> <br>

앞서 우아한 형제들 비즈 인프라 개발 팀에서는 Redis가 없어 DB Named Lock으로 해결했지만, 채널톡, 와디즈 펀딩개발팀, 하이퍼 커넥트 Azar API팀, 컬리 풀필먼트 프로덕트 등 다양한 조직에서 Redis를 통해 분산락을 구현해 사용 중이다. <br>
대부분 선택 이유중 하나로 "이미 Redis를 활용 중임"을 꼽았다. 

<br>


## 3.1 Lettuce + 채널톡 사례
Lettuce는 Redis 클라이언트의 한 종류이다. <br>
Lecttuce를 통해 구체적으로 분산락을 구현하는 코드를 확인해 보자. 제시된 코드는 채널톡 기술 블로그의 코드를 가져왔다. -> [Distributed Lock 구현 과정](https://channel.io/ko/blog/distributedlock_2022_backend) <Br> 

앞서 언급한 setnx 연산을 활용하고, pub/sub 활용으로 개선했다. <br>

```java
public String tryAcquire(String lockKey, Duration expireTime) {  
    if (redis.set(lockKey, uniqueId).nx().ex(expireTime) != null) {
        return uniqueId;
    } else {
        return "LOCK_ACQUIRE_FAILED";
    }
}
```

락을 얻는 코드이다. `set()` 호출 뒤에 메서드 체이닝을 통해 `nx()`를 호출하고 있다. 이렇게 setnx를 호출할 수 있다. lockKey라는 key가 있는 경우 아무것도 하지 않고 락 획득을 실패했다고 본다. 그리고 없는 경우 unique한 값을 value로 세팅해준다. (key-value 방식으로 데이터 저장) <br>
`ex()`를 통해 만료시간을 지정할 수 있는데, 이후 데이터가 지워진다. <Br>
value는 클라이언트 마다 unique한 값으로 설정해주어야 한다. 왜냐하면, Timout된 Lock 삭제를 시도 할 때, 다른 클라이언트가 점유중이라면 삭제가 되지 않아야 하는데, 다 같은 value를 가지고 있다면 다른 클라이언트가 가진 락을 지워버리게 될 수도 있다. <br>
그래서 키를 해제하는 코드는 아래와 같이 작성된다.

```java
if (redis.get(lockKey) == uniqueId) {  
   redis.del(lockKey);
   redis.publish("distributedLockChannel", lockKey);
}
```
클라이언트 본인이 얻은 락이 맞는지 확인하기 위해 uniqueId를 비교하고 있다. <Br>
이후 publish를 통해 Key을 Subscribe하고 있는 클라이언트들에게 Lock의 해제를 알려준다! 이 키의 락 헤제만 기다리는 이들에게 메시지를 보내는 것이다. <Br>
동시성 이슈를 피하기 위해 전부 원자적으로 실행 되어야 한다. 이는 LUA Script를 활용해 구현할 수 있다.

<Br> <br>

Lock을 기다리는 클라이언트들은 언제 다시 Lock 획득을 시도할까? 바로 Sub중인 채널에 메시지가 pub될때 마다이다. <br>
문제는, 네트워크 장애나 지연, 혹은 GC Stop-the-world로 인해 Lock Timeout이 되어 Message가 누락될 수도 있다. 그래서 timeout이 되도록 메시지가 아예 오지 않으면 한번쯤 재시도를 해준다.

<Br> <br>

이 방법에는 Single Redis에 의존해 결함 허용성이 낮다는 단점이 있는데, 락 HA를 위한 Redis Clustering은 좀 심해서, Redlock 알고리즘을 사용한다. 자세한 것은 채널톡 블로그의 "해당 Lock의 문제점" 부분을 읽어보자. [Distributed Lock 구현 과정](https://channel.io/ko/blog/distributedlock_2022_backend)

## 3.2 Redisson
Redisson도 레디스 클라이언트 라이브러리의 하나이다. Redission은 기본적으로 Lock interface를 지원해주기 때문에, 따로 setnx를 직접 사용하며 락 관리를 구현할 필요가 없다. <br>


컬리 또한 이미 Redis를 사용하고 있기에 추가적인 인프라 구축이 없어 사용했다. 또한, MySQL Named Lock을 사용하는 경우 락을 위한 별도의 커넥션 풀을 관리하거나 락에 관련된 부하가 부담되어 Redis를 사용했다고 한다. <Br>
또한 Redisson을 사용한 이유는 Lock Interface의 지원으로 직접 여러 기능을 구현할 필요가 없어 더욱 안전하기 떄문이라고 한다. <br>
그리고 이미 구현되어 있는 Lock도 Pub/Sub을 활용해 구현되어 있어 spin lock보다 낫다 <br>

Lock Interface를 활용해 AOP로 구현한 코드는 아래 글에서 확인해볼 수 있다.
- [컬리 - 풀필먼트 입고 서비스팀에서 분산락을 사용하는 방법](https://helloworld.kurly.com/blog/distributed-redisson-lock/) <br>

다른 글도 궁금하다면 아지르 팀의 글을 읽어보자.
- [레디스와 분산 락(1/2) - 레디스를 활용한 분산 락과 안전하고 빠른 락의 구현](https://hyperconnect.github.io/2019/11/15/redis-distributed-lock-1.html)


## 3.3 두 클라이언트 라이브러리 비교
### 3.3.1 Lettuce
1. 구현이 간단하다.
2. spring data redis를 이용하면 lettuce가 기본이기 때문에 별도의 설정 없이 바로 적용 가능
3. 단, Pub/Sub을 활용하지 않으면 기본적으로 spin lock 방식이기 때문에 많은 스레드가 lock 획득 대기 상태라면 redis에 부하가 갈 수 있다. 결국 사용자가 손이 많이 간다. 락을 얻고 해제하고, 재시도하고, 구독자들에게 알리는 대부분의 과정을 직접 구현해야 한다.

### 3.3.2 Redisson
1. lock 관리 API를 라이브러리 차원에서 제공해준다는 것이 큰 장점. <br> **락 획득 재시도 등의 다양한 로직을 기본으로 제공하고, Pub/Sub으로 구현되어 있어 Lecttuce 대비 Redis 부하가 덜하다.**
2. 별도의 라이브러리를 이용해야 한다. (기본이 아니다.)

<br>

딱히 재시도가 필요 없고 간단하게 낮은 요청 횟수에서 사용하려면 Lecttuce도 나쁘지 않지만, 그 외엔 Redission이 나은 것 같다. <br>
그리고 DB를 사용하는 방식과 Redis를 사용하는 방식을 비교해보자면, 현재 Redis를 사용중이지 않고, 오직 Lock만을 위해 Redis를 사용하는 것은 관리 포인트가 너무 많아지기 때문에 좋지 않다. 하지만, 이미 사용하고 있다면 Redis를 고려하는 것도 좋다. <Br>

왜냐하면 DB 부하에도 좋고, 성능에도 좋다. 
1. Lock을 위한 DB의 추가 부하를 줄여줄 수 있다.
2. DB를 다녀오는 것과 memory에서 처리하는 것은 엄청난 속도 차이가 난다.

그래서 낮은 트래픽에서 간단하게만 사용할 것이고 Redis가 없다면 DB를, 아니라면 Redis를 고려하면 될 것 같다.


# 4. Zookeeper 활용
Zookeeper로도 분산락을 구현할 수 있다. <br>
방법 자체는 아래 글에서 확인하자.
- [[zookeeer-2] 주키퍼(zookeeper) 분산 락처리](https://zaccoding.tistory.com/27)

<br> <br>

Zookeeper를 활용하는 방법은 지금은 거의 쓰지 않는 방법이다. 왜냐하면 주키퍼 자체가 단지 분산락을 위해 사용하기엔 너무 무겁다는 것이 문제이다. 또한, 락이 중요하다면 HA를 위해 클러스터링이나 다른 조치를 취할텐데 안 그래도 무거운데 다중화까지 한다면 서버가 버거워 할 것이다. <br>

대안으로도 Redis도 있고 DB로도 해결할 있기 때문에 지금은 거의 쓰지 않는다고 하는 것 같다. 물론 Redis도 없고 이미 주키퍼 인프라가 잘 되어 있다면 고려해볼 수 있는 방법일 수도 있을 것 같다.

# 5. STW와 네트워크 지연으로도 동시성 문제가 발생할 수 있다.
Redis를 활용한 Lock이 있음에도 동시성 문제가 발생할 수도 있다. <br>
Lock을 획득한 상태에서 GC의 Stop the World가 발생하거나, 네트워크가 지연되었고 아직 데이터를 쓰기 전인데 그 사이에 Lock이 만료되어 반환되었다고 생각해보자. 그리고 홀랑 다른 서버에서 데이터를 저장했다. <br>

![image](https://github.com/binary-ho/TIL-public/assets/71186266/b2c15166-b8f5-45cd-9674-49ed0601dfa8)

이런 방식으로 락이 있음에도 동시성 문제가 발생할 수 있다. 재미있는 사례라 공유한다. <br>
또한 위 글에 따르면 Hbase에서도 인터넷 지연으로 인한 비슷한 이슈가 있었다고 해서 같이 공유한다.

- [와디즈 - 분산 환경 속에서 ‘따닥’을 외치다](https://blog.wadiz.kr/%EB%B6%84%EC%82%B0-%ED%99%98%EA%B2%BD-%EC%86%8D%EC%97%90%EC%84%9C-%EB%94%B0%EB%8B%A5%EC%9D%84-%EC%99%B8%EC%B9%98%EB%8B%A4/)
- [](https://blog.cloudera.com/tuning-java-garbage-collection-for-hbase/)
