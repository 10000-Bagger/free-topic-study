
# 4. 스레드와 높은 수준 추상화
자바 스트림의 병렬 스트림은, 병렬성을 아주 쉽게 달성할 수 있도록 도와주었다. <br>
예를 들어, 원래는 100만회의 for 루프 연산을 4개의 스레드에서 병렬 수행하려면 아래와 같이 각 스레드에 외부 반복 (명시적인 루프) 연산을 할당해주고 `start()`를 호출한 다음, `join()`으로 취합해야 했다.

```java
// 스레드 1
int sum = 0;
for (int i = 0; i < 250_000; i++) {
  sum += numbers[i];
}

// 스레드 2
int sum2 = 0;
for (int i = 250_000; i < 500_000; i++) {
  sum2 += numbers[i];
}

// 스레드 3
...


// 스레드 4
int sum4 = 0;
for (int i = 750_000; i < 1_000_000; i++) {
  sum4 += numbers[i];
}


...


// 그리고 어디선가 네 결과를 취합 - `join()`
return sum1 + sum2 + sum3 + sum4;
```

<br>

하지만 병렬 스트림을 사용한다면, 내부 반복만으도 구현이 가능하다
```java
sum = Arrays.stream(numbers)
        .parallel()
        .num()
```

스트림을 통해 스레드 사용을 손쉽게 추상화 한 모습이다. 이는 사용하기도 쉽고, 명시적인 루프들을 내부로 숨길 수 있어서 복잡성도 줄어든다. <br>
긴 루프들을 읽으며.. 이게 뭐 하는 로직인지 생각하는 것은 어렵다. 스트림으로 작성된 코드는 추상화가 잘 되어 있어 몇 줄의 코드만으로 빠르게 상황을 이해할 수 있다. <br>
parallel은 내부적으로 포크/조인을 통해 분할 정복 방식으로 여러 스레드에 연산을 나누어 준다. 

## 4.1 Executor와 스레드 풀
이제 ExecutorService와 스레드 풀에 대해 알아보자. <br>

자바의 스레드는 직접 OS의 스레드에 접근한다. OS 스레드를 만들고 종료하는 것은 비싼 오버헤드가 존재하고, 갯수도 제한 되어 있다. <br>
OS가 지원하는 스레드 수를 초과해 사용하는 경우, 자바 애플리케이션이 예상치 못하게 크래시 될 수 있기 때문에, 기존 스레드가 실행되고 있는 상황에서 계속해서 새로운 스레드가 만들어지는 상황은 주의해야 한다. <br> <br>

### 스레드 풀과 자바
스레드의 갯수를 컨트롤하고, 스레드를 만들고 없애는 오버헤드를 줄이기 위해, 스레드 풀은 아주 좋은 선택이다. <br>
정해진 갯수만큼의 스레드를 미리 만들어 놓은 만큼, Pool에서 가져다 쓰는 것이다. <br> 

자바 Executors에선 간단하게 스레드 풀을 선택할 수 있는 Factory Method를 제공해준다. 
1. newFixedThreadPool
2. newWorkStealingPool
3. newSingleThreadExecutor
4. newCachedThreadPool
5. newScheduledThreadPool

등등... 여러 스레드 풀을 가진 ExecutorService 혹은 그 구현체를 반환해준다. 사용자는 ExecutorService에 Task를 제출하면, ExecutorService가 제공해주는 인터페이스를 통해 나중에 결과를 수집할 수 있다. <br> 
하나만 예를 들면 `ExecutorService newFixedThreadPool(int nThread)`는 고정 사이즈 스레드 풀을 가진 ExecutorService를 생성한다. 이는 nThread 갯수의 워커 스레드를 갖는다. 제출된 Task들을 큐에 저장해 먼저 온 순서대로 사용하지 않은 스레드로 제출해 실행한다. 그리고 스레드 사용이 끝나면 다시 스레드 풀로 반환한다. <br>
또한 스레드 풀을 설정하고, 간단하게 큐의 크기나 거부 정책, 태스크 종류에 딸느 우선순위도 설정할 수 있다. <br>
프로그래머는 단지 Runnable이나 Callalbe인 Task를 제공하면 손쉽게 스레드가 이를 수행하도록 주문할 수 있다.


## 4.2 스레드 풀의 단점 이야기
웬만하면 스레드 풀이 없는 것 보다 있는 것이 좋지만, 이런 스레드 풀도 만능은 아니다. "잘 사용해야 한다".  


### 1. Block 될 수 있는 스레드를 조심하자

만약 처음에 제출된 Task들이 스레드의 절반을 Block시킬 수 있다고 가정해보자. 이 경우 스레드들이 Block되는 동안 나머지 살아있는 스레드들이 힘겹게 다른 Task들을 처리해야 한다. 그리고 이는 성능 저하를 유발하고, Block된 Task들 끼리 결과를 필요로 하는 경우 데드락에 걸릴 수도 있다. 
<br>

결론적으로 Block될 수 있는 Task는 스레드 풀에 제출하지 말아야 한다! 물론 이는 항상 지킬 수 있는 사항은 아니다.

### 2. 프로그램 종료 전에 모든 스레드 풀을 종료해야 한다. 
그렇지 않으면 중요한 코드를 실행하는 스레드가 죽을 수도 있다. <br>

기존에 실행중이던 스레드가 종료되지 않은 상황에서 자바 main()이 반환된다면 아래와 같은 두 가지 상황이 벌어질 수 있다. (둘 다 안전하지 않다.)

- Application을 종료하지 못하고, 모든 스레드 실행 종료를 기다린다.
- Application 종료를 방해하는 스레드를 강제로 종료 시키고 Application을 종료한다.

<br>

첫 번째 방법에서는 잊고서 종료하지 못한 스레드에 의해 Applicatino이 크래시 될 수 있다. 또 다른 문제로는 디스크에 쓰기 I/O 작업을 시도하는 작업이 중단되었을 때 이로 인해 데이터 일관성이 파괴될 수 있다. 꼭 모든 스레드를 종료하고 App을 종료하자. <br>

`setDaemon()` 메서드를 활용하면 좋다. 데몬 스레드는 Applicatino이 종료될 때 강제로 종료된다. 따라서 디스크 데이터 일관성과 무관한 동작을 수행할 때 유용하다. 반대로 비데몬 스레드는 main메서드가 종료를 기다린다.

<br>


### 3. [스레드 풀은 크면 클 수록 무조건 좋은게 아니다.](https://www.youtube.com/watch?v=jSaBkvtHhrM)

## 4.3 결국 우리가 스레드를 다루면서 기대하는 것!

결국 우리가 스레드를 다루며 기대하는 것은 병렬성의 극대화이다. <br>
프로그램을 작은 Task 단위로 구조화하고, 병렬적으로 수행하고 싶은 것이 우리가 기대하는 것이다! 단, 변환 비용을 고려해 너무 작은 크기는 아니여야 한다. <br>

이를 위해 어렵게 스레드를 다루는 것이고, 여러 방법들이 나오게 된 것이다. 이들을 가슴에 새겨 놓고 공부하자.


# 5. CompletableFuture 사용법 - 안정적 비동기 프로그래밍
이제는 자세한 사용법을 살펴보자. 외부 컴포넌트에서 가격 정보를 가져오는 메서드를 CompletableFuture을 활용해 개선했다고 가정한 상황이다. <br>
예시가 이런 이유는 실제로 서비스를 구현하다 보면, 여러 외부 서버에서 가격 정보나 할인 정보를 가져올 일이 빈번하기 때문이다. 이 작업들이 모두 동기 + Blocking으로 이루어진다면, 서비스는 끔찍하게 느릴 수 밖에 없다. <br> 보통은 비동기적으로 외부 서버에 접근하고, 데이터를 취합한다.

```java
public Future<Double> getPriceAsync(String product) {
  CompletableFuture<Double> futurePrice = new CompletableFuture<>();
  new Thread(() -> {
    double price = calculatePrice(product);
    futurePice.complete(price);
  }).start();
  return futurePrice;
}
```

위 메서드를 호출하면 Future 객체를 바로 전달 받는다. 그리고, 반환된 Future 객체를 통해 나중에 결과를 얻을 수 있다. 
가장 기본적인 형태이다. 여기서 부터 개선하면서, 사용방법을 익히자.


### 5.1 예외 처리
만약 외부 컴포넌트에서 데이터를 가져오다가 예외가 발생하면 어떤 일이 일어날까? `getPriceAsync`를 호출한 메서드에겐 영향이 미치지 않기 때문에, 계속 진행되고, 일의 순서가 꼬이게 된다. <br>
Future값에서 가격을 꺼내올 때 어쩌면 영원히 기다리게 될 수도 있다. <br>
아래와 같이 `completeExceptionally`를 활용하면, 예외 발생을 클라이언트까지 전달해줄 수 있다.

```java
public Future<Double> getPriceAsync(String product) {
  CompletableFuture<Double> futurePrice = new CompletableFuture<>();
  new Thread(() -> {
    try {
      double price = calculatePrice(product);
      futurePice.complete(price);
    } catch (Exception exception) {
      futurePice.completeExceptionally(exception);
    }
    
  }).start();
  return futurePrice;
}
```

이런 방식으로 진행중에 예외가 발생하면 핸들링하고, 외부에 전달할 상태들도 결정할 수 있다. <br>
이를 밖에서 (수행한) 받을때는, `exeptionally()` 로 받을 수 있다. 
"어떤 예외가 발생할 때, 어떤 행동을 한다"를 지정할 수 있다.
```java
void exceptionally(boolean doThrow) throws ExecutionException, InterruptedException {
    CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
        if (doThrow) {
            throw new IllegalArgumentException("Invalid Argument");
        }

        return "Thread: " + Thread.currentThread().getName();
    }).exceptionally(e -> {
        return e.getMessage();
    });

    System.out.println(future.get());
}
```

위를 보면 `exceptionally`가 있는데, 간단하게 메시지를 출력하는데 사용했다. 나는 내 출석 서비스에서 에러를 로깅하고, 출석이 실패했음을 저장하는 데에 사용하고 있다!

<br>

또 하나 있는데 `handle`이 있다.

```java
void handle(boolean doThrow) throws ExecutionException, InterruptedException {
    CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
        if (doThrow) {
            throw new IllegalArgumentException("Invalid Argument");
        }

        return "Thread: " + Thread.currentThread().getName();
    }).handle((result, e) -> {
        return e == null
                ? result
                : e.getMessage();
    });

    System.out.println(future.get());
}
```
실행 결과도 같이 받아서, 결과에 대한 처리를 할 수 있다! `exceptionally`는 단순히 예외에 대한 처리만 가능하다! <br>

이 외에도 아직 완료되지 않았으면 `get()`을 호출해 기다리고, 실패시엔 exception을 던지는 `completeExceptionally`이나, 강제로 예외를 발생시키는 `obtrudeException`도 있다. (어느 상황에 쓰는지 떠오르지는 않는다.) <br>

또한, 예외를 확인하는 `isCompletedExceptionally`도 있다. <Br>
이 다양한 예외들을 보니, 코틀린에서 다양한 예외 상황을 관리하는 `Result` 객체가 등장하게 된 배경을 조금 알 것 같다. [좋은 글](https://tech.kakaopay.com/post/msa-transaction/)


### orTimeout
마지막으로 `orTimeout`은 앞선 메서드들 보다 더 늦게 Java 9에 도입된 기능으로, 직접 타임아웃 시간 설정이 가능하다! <br>

아래에서 설명할 코드지만, `orTimeout`만 봐주세요 ㅎㅎ
```java
public Future<Double> getPriceAsync(String product) {
  return CompletableFutre.supplyAsync(() -> calculatePrice(product));
}.orTimeout(3, TimeUnit.SECONDS);
```

위와 같은 코드를 통해 비동기 작업이 너무 길어지는 경우에 대한 예외 처리를 할 수 있다. DB I/O의 경우 기본 타임아웃이 있지만, 지정해주지 못 하는 경우나, 기본 타임 아웃 시간과 다른 타임 아웃이 필요할 때 설정해 주면 될 것 같다. <br>
위 코드는 직관적으로 3초가 넘으면 `TimeoutException`을 발생시킨다. 

<br>

![image](https://github.com/depromeet/amazing3-be/assets/71186266/2ff7e01b-dc57-469d-a3f6-96431b3db914)


또한 completeOnTimeout은 타임아웃시 "기본값"을 설정해줄 수 있는 마법같은 메서드이다.



### 5.2 다양한 팩토리 메서드
팩토리 메서드를 활용해 지금까지 보인 방법 보다 훨씬 쉬운 방법으로 CompletableFuture를 만들 수 있다. <br>

```java
public Future<Double> getPriceAsync(String product) {
  return CompletableFutre.supplyAsync(() -> calculatePrice(product));
}
```

이는 Supplier를 인수로 받아 CompletableFutre를 반환한다. 내부에서 비동기적으로 Supplier를 실행하고 결과를 생성한다. <br> 
- 기본 : ForkJoinPool의 Executor 중 하나가 Supplier를 실행
- 설정 : 두 번째 파라미터를 통해 Executor를 지정 가능하다! (굿)

<br> <br>


위 코드는 직전 "5.1 예외 처리"의 코드와 동일한 코드인데, 예외 까지도 똑같이 관리해준다!고 하는데, 못 믿겠으니 내부적으로 어떻게 돌아가는지 확인해보자.

![image](https://github.com/depromeet/amazing3-be/assets/71186266/56231fe6-dd32-4351-81dd-e11bcdd25558)


![image](https://github.com/depromeet/amazing3-be/assets/71186266/5032ac33-832b-4977-8b63-92ff71efdce5)


위 그림과 같이 두 번째 파라미터에 따라 스레드 풀을 결정한다.

![image](https://github.com/depromeet/amazing3-be/assets/71186266/d6d37e11-009e-4306-9bee-5be0f2e78b5d)
그리고, CompletableFutre를 생성해 Executor로 실행하고, Future를 반환한다. 그리고 AsyncSupply는 내부적으로 아래와 같이 동작한다.
![image](https://github.com/depromeet/amazing3-be/assets/71186266/db682365-fc64-4522-84d5-202b547c01b5)

Runnable의 메서드 `run()`을 보면, 책에서 언급한 것이 사실이었다. eompleteThrowable을 호출해 예외를 넣어주고 있다. 사실이구나 못 믿어서 미안하다. <br>

결론적으로 팩터리 메서드를 사용해 손쉽게 비동기 처리를 구현할 수 있겠다. 
반환값이 없는 경우 `supplyAsync`와 완전히 동일하게 `runAsync`를 사용할 수 있다. `runAsync`는 반환값이 Void 타입이다.

### 5.3 작업 조합
여러 Future가 사용되는 경우, 어떤 연산이 다른 연산의 선행 조건일 수 있다. 이 때, get()을 호출하고 기다릴 수도 있지만, 앞선 글에서 설명한 데코레이션 방식으로 조합할 수도 있다.

1. `thenCompose()` : 두 작업이 이어서 실행되고, 앞선 작업의 결과를 받아 사용한다. "합성"이라는 느낌으로 앞선 결과와 다음 것을 "합성"해서 최종 결과를 만든다고 생각하자. 함수형 인터페이스 `Funtion`를 파라미터로 받음
2. `thenCombine()` 두 작업을 독립적으로 실행하고, 둘 다 완료되는 경우 콜백을 받는다! 합성과 달리 따로 둘 다 수행하는 느낌인데, 둘의 완료를 기다리는 느낌!
3. `allOf()` : 여러 작업을 동시 수행하고, **모든** 작업 결과에 콜백을 수행함. 모든 작업에 수행하므로 `All Of`라는 이름이 붙였다. 이와는 조금 다른..
4. `anyOf()` : 이쪽은 뭐라도 완료하면 콜백을 수행하는 것! 그러니까, **여러 작업들 중 가장 빨리 끝난 "any" 작업에 콜백을 실행함**

최저 가격 애플리케이션을 구현한다고 가정하자. 각 가게마다 가격을 비동기로! 가져와 비교할 것이다. 

