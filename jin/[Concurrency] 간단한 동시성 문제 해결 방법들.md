# 간단한 동기성 이슈 해결 방식들
1. Java가 제공해 주는 기능 활용하기
   1. Synchronized
   2. ReentrantLock과 ConcurrentHashMap 활용
2. DB 활용하기
   1. Select For Update (Pessimistic Lock)
   2. Optimistic Lock
   3. Named Lock
3. In-memory DB Redis 활용하기
   1. 라이브러리 Lecttuce (setnx - Set If Not Exist 활용)
   2. 라이브러리 Redisson (컬리 분산락 사례)


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
  try {
    // 트랜잭션 시작 부분
    startTransaction();

    // 실제 메서드 호출 부분
    fruitService.eatApple(quantity);

} catch(...) { ... } 
  finally() {

    // 트랜잭션을 끝내는 부분
    commitTransaction();
  }
}
```

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


# 2. DB가 제공해주는 기술을 활용한 해결
## 2.1 Pessimistic Lock - `SELECT FOR UPDATE` Query

Select For Update는 MySQL에서 8.0 부터 사용할 수 있는 쿼리의 한 종류로, 말 그대로 Update를 위한 Select를 제공해주는데, **정확한 값 Update를 할 수 있도록 검색된 모든 행에 대해, 다른 트랜잭션의 접근을 막아준다.** <br>

```sql
SELECT * FROM fruits f WHERE f.name = 'apple' FOR UPDATE;
```

간단하게 DB 수준에서 동시성 이슈를 막아줄 수 있다. <Br>
하지만 언급한 것과 같이 검색된 모든 행에 Lock이 걸리게 되므로, 성능 저하나 데드락의 원인이 될 수 있기 때문에, 대기 시간이나 옵션을 잘 사용해야 한다. <br>
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
쿼리 발행을 확인해 보면, 맨 끝에 `FOR UPDATE`가 붙어서 발행된다!


## 2.2 DB가 제공해주는 Lock을 활용하는 방법
DB에서도 자체적으로 제공하는 Lock들이 있다. 아래 3가지 Lock을 사용해 동시성 문제를 해결할 수 있다.

1. `Pessimistic Lock` (앞서 보임)
2. `Optimistic Lock`
3. `Named Lock`

JPA와 함께 활용하는 방식을 보일것이다. 어차피 JPA는 App단에서 DB 기능을 쓸 수 있도록 돕는 것이기 때문에 JPA 없이도 원래 DB 설정으로 아래 제시한 Lock들을 사용할 수 있다.


### 2.2.1 Optimistic Lock
실제로 Lock을 이용하지 않고 따로 버전을 저장한다. 이 버전 값을 활용해 정합성을 맞춘다. <Br> 

먼저 데이터를 가져올 때, 버전값을 확인했다가, **실제 `UPDATE` 쿼리를 날리는 시점에 버전을 다시 확인한다. 이때, DB에 저장된 버전이 처음 SELECT시의 버전과 다르면 트랜잭션을 롤백한다!** 데이터가 성공적으로 Commit되면 버전 값을 업데이트 한다.

<br> <br>

별도의 락을 잡지 않고 저장된 버전을 통해 판단하므로, 경쟁 상황이 그리 심하지 않은 경우 `Pessimistic Lock`보다 성능이 좋다! <br>
단점도 있다.
1. 재시도하는 로직을 프로그래머가 직접 작성해줘야 해서 번거롭고, 실수할 수도 있다. (버전이 다른 경우 트랜잭션이 실패하기 때문에, 저장해야 한다면 재시도 로직을 작성해야 한다.)
2. Entity 객체에 version field를 추가해야 한다. -> 추가 관리 포인트가 될 수 있다.
3. 버전 값이 달라져 업데이트가 실패하는 경우가 많은 경우, 요청을 여러번 보내야 하므로 Pessimistic Lock 보다 성능이 떨어진다고 할 수 있다.



<br>

JPA와 구현하는 법을 살펴보자. 일단 엔티티에 `@Version` 어노테이션이 달린 field가 추가 되어야 한다.
```java
  @Version
  private Long version;
``` 

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

경쟁 상황이 별로 없다면 성능적으로 꽤나 괜찮지만, 상당히 번거롭고 누군가 실수하기 딱 좋은 방식인 것 같다.

### 2.2.2 Named Lock

이름을 가진 metadata locking 이다. 이름을 가진 lock을 획득한 후, 해제할 때까지 다른 세션은 이 lock을 획득할 수 없게 한다. <br> 

일단 아래와 같이 LockRepository를 선언한 다음 Native Qurey를 아래와 같이 작성해준다. 

```java
public interface LockRepository extends JpaRepository<Stock, Long> {

    @Query(value = "select get_lock(:key, 3000)", nativeQuery = true)
    void getLock(String key);

    @Query(value = "select release_lock(:key)", nativeQuery = true)
    void releaseLock(String key);
}
```

쿼리를 보면 String 값의 key가 있는데, 앞서 보인 ReentrantLock와 CuncurrentHashMap을 활용한 사례처럼 같이 특정 "key" 값을 통해 락을 제어할 수 있다는 것이 장점이다. 이러한 key를 사용한다고 해서 Named Lock이다. 
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


# 3. 레디스를 활용한 방식
## 3.1 Lettuce
## 3.2 Redisson
## 3.3 두 라이브러리 비교
