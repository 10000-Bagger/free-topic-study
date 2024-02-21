# Reactor Testing
## 1. StepVerifier를 사용한 테스팅
- StepVerifier란 Operator 체인의 다양한 동작 방식을 테스트하기 위한 API
### Signal 이벤트 테스트
```java
@Test
public void sayHelloReactorTest() {
    StepVerifier.create(Mono.just("Hello Reactor"))
            .expectNext("Hello Reactor") // emit 데이터의 기대값 평가
            .expectComplete() // onComplete Signal 기대값 평가
            .verify(); // 검증 실행
}
```
1. create()를 통해 테스트 대상 Sequence 생성
2. expect~() 메서드로 예상되는 Signal의 기대값 평가
3. verify()를 호출해 전체 Operator 체인의 테스트를 트리거

#### expectXXXX() 메서드
| 메서드                                           | 설명                                                            |
|-----------------------------------------------|---------------------------------------------------------------|
| expectSubscription()                          | 구독이 이루어짐을 기대한다                                                |
| expectNext()                                  | onNext Signal을 통해 전달되는 값이 파라미터로 전달된 값과 같음을 기대한다.              |
| expectComplete()                              | onComplete Signal이 전송되기를 기대한다.                                |
| expectError()                                 | onError Signal이 전송되기를 기대한다.                                   |
| expectNextCount(long count)                   | 구독 시점 또는 이전 expectNext()를 통해 기댓값이 평가된 데이터 이후부터 emit된 수를 기대한다. |
| expectNoEvent(Duration duration)              | 주어진 시간 동안 Signal 이벤트가 발생하지 않았음을 기대한다.                         |
| expectAccessibleContext()                     | 구독 시점 이후에 Context가 전파되었음을 기대된다.                               |
| expectNextSequence(Iterable <? extends T>)    | emit된 데이터들이 파라미터로 전달된 Iterable의 요소와 매치됨을 기대한다.                |

#### verifyXXXXX() 메서드
| 메서드                              | 설명                                                 |
|----------------------------------|----------------------------------------------------|
| verify()                         | 검증을 트리거한다.                                         |
| verifyComplete()                 | 검증을 트리거하고, onComplete Signal을 기대한다.                |
| verifyError()                    | 검증을 트리거하고, onError Signal을 기대한다.                   |
| verifyTimeout(Duration duration) | 검증을 트리거하고, 주어진 시간이 초과되어도 Publisher가 종료되지 않음을 기대한다. |

#### as를 활용한 실패 message logging
```java
private static Flux<String> sayHello() {
    return Flux.just("Hello", "Reactor");
}

@Test
public void sayHelloTest() {
    StepVerifier
            .create(sayHello())
            .expectSubscription()
            .as("# expect subscription")
            .expectNext("Hi") // 실패
            .as("# expect Hi")
            .expectNext("Reactor")
            .as("# expect Reactor")
            .verifyComplete();
}

// java.lang.AssertionError: expectation "# expect Hi" failed (expected value: Hi; actual value: Hello)
```
- as를 활용해 expectXXXXX() 메서드가 실패했을 때의 logging message를 설정할 수 있다.

#### 오류 발생을 기대할 때 expectError()
```java
public static Flux<Integer> divideByTwo(Flux<Integer> source) {
    return source.zipWith(Flux.just(2, 2, 2, 2, 0), (x, y) -> x/y);
}

@Test
public void divideByTwoTest() {
    Flux<Integer> source = Flux.just(2, 4, 6, 8, 10);
    StepVerifier
            .create(divideByTwo(source))
            .expectSubscription()
            .expectNext(1)
            .expectNext(2)
            .expectNext(3)
            .expectNext(4)
            .expectError()
            .verify();
}
```
- 마지막 항목에서 0으로 나누기를 수행에 오류가 나오지만
- expectError()는 오류를 기대하기 때문에 테스트는 passed

#### 오류 실패 시 원하는 시나리오 명을 출력하고 싶을 떄
```java
public static Flux<Integer> takeNumber(Flux<Integer> source, long n) {
    return source.take(n);
}

@Test
public void test() {
    Flux<Integer> source = Flux.range(0, 1000);
    
    StepVerifier.create(
                    takeNumber(source, 500),
                    StepVerifierOptions.create().scenarioName("Verify from 0 to 499") // 옵션 값으로 실패할 경우 출력할 시나리오 명을 추가
            ).expectSubscription() // 구독 발생을 기대
            .expectNext(0)   // 0이 emit됨을 기대
            .expectNextCount(498) // 498개의 숫자가 emit됨을 기대
            .expectNext(500) // 500이 emit됨을 기대
            .expectComplete() // onComplete Signal이 전송됨을 기대
            .verify();
}

// java.lang.AssertionError: [Verify from 0 to 499] expectation "expectNext(500)" failed (expected value: 500; actual value: 499)
```

### 시간 기반(Time-based) 테스트
- Virtual Time를 활용해 미래에 실행되는 Reactor Sequence의 시간을 앞당겨 테스트할 수 있다.

#### 시간을 앞당겨서 테스트하는 예시
```java
private static Flux<Tuple2<String, Integer>> getCOVID19Count(Flux<Long> source) {
    return source.flatMap(
            notUse -> Flux.just(
                    Tuples.of("서울", 10),
                    Tuples.of("경기", 20),
                    Tuples.of("부산", 30),
                    Tuples.of("대구", 40),
                    Tuples.of("제주", 50)
            )
    );
}

@Test
public void getCOVID19CountTest() {
    StepVerifier
            .withVirtualTime(
                    () -> getCOVID19Count(Flux.interval(Duration.ofHours(1)).take(1)) // 1시간 뒤에 데이터를 emit
            ).expectSubscription()
            .then(() -> VirtualTimeScheduler.get().advanceTimeBy(Duration.ofHours(1))) // 시간을 1시간 앞당기는 메서드
            .expectNextCount(5)
            .expectComplete()
            .verify();
}
```

#### verify Timeout을 두는 예시
```java
@Test
public void getCOVID19CountTest() {
    StepVerifier
            .withVirtualTime(
                    () -> getCOVID19Count(Flux.interval(Duration.ofHours(1)).take(1)) // 1시간 뒤에 데이터를 emit
            ).expectSubscription()
            .expectNextCount(5)
            .expectComplete()
            .verify(Duration.ofSeconds(3));
}
```
- verify에 지정한 3초라는 시간 안에 기대값에 대한 평가를 마쳐야 테스트가 pass한다.

#### expectNoEvent()를 활용한 시간 앞당김
```java
@Test
public void getCOVID19CountTest2() {
    StepVerifier
            .withVirtualTime(
                    () -> getVoteCount(Flux.interval(Duration.ofSeconds(1)))
            ).expectSubscription()
            .expectNoEvent(Duration.ofSeconds(1))
            .expectNoEvent(Duration.ofSeconds(1))
            .expectNoEvent(Duration.ofSeconds(1))
            .expectNoEvent(Duration.ofSeconds(1))
            .expectNoEvent(Duration.ofSeconds(1))
            .expectNextCount(5)
            .expectComplete()
            .verify();
}
```
- expectNoEvent()는 파라미터로 지정한 시간 동안 어떤 Signal도 발생하지 않았음을 기대한다.
- 또한 지정한 시간만큼 시간을 앞당기는 역할도 한다.
### Backpressure 테스트
```java
private static Flux<Integer> generateNumber() {
    return Flux.create(emitter -> {
        for(int i = 1; i <= 100; i++) {
            emitter.next(i);
        }
        emitter.complete();
    }, FluxSink.OverflowStrategy.ERROR); // Backpressure 전략으로 ERROR 사용
}

@Test
public void backpressureTest() {
    StepVerifier
            .create(generateNumber(), 1) // 2번째 파라미터: 데이터 요청 개수
            .thenConsumeWhile(num -> num >= 1)
            .expectError() // 에러가 터지는 결과 기대
            .verifyThenAssertThat() // 검증을 Trigger한 뒤
            .hasDroppedElements(); // 요소를 버리기를 기대한다
}
```
- 데이터를 1개만 요청했는데 100개를 emit하기 때문에 OverflowException이 발생한다.
- 때문에 expectError()의 기대값을 충족시킨다.
- 이후 버려지는 요소를 확인하기 위해 hasDroppedElements() 활용한다.

### Context 테스트
```java
private static Mono<String> getSecretMessage(Mono<String> keySource) {
    return keySource
            .transformDeferredContextual(
                    (mono, ctx) -> mono.map(notUse -> ctx.get("secretMessage"))
            );
}

@Test
public void getSecretMessageTest() {
    Mono<String> source = Mono.just("hello");

    StepVerifier
            .create(
                    getSecretMessage(source)
                            .contextWrite(context -> context.put("secretMessage", "Hello, Reactor"))
            ).expectSubscription()
            .expectAccessibleContext()
            .hasKey("secretMessage")
            .then()
            .expectNext("Hello, Reactor")
            .expectComplete()
            .verify();
}
```
- expectAccessibleContext()는 구독 이후에 Context가 전파되었음을 기대한다.
- hasKey()는 Context 내에 원하는 key값이 존재하는지를 판단한다.

### Record 기반 테스트
- emit된 데이터를 단순 기댓값 평가만이 아닌 구체적인 조건으로 Assertion해야 하는 경우에 사용한다.
- recordWith()는 파라미터로 전달한 Java의 컬렉션에 emit된 데이터들을 추가한다.
```java
private static Flux<String> getCapitalizedCountry(Flux<String> source) {
    return source
            .map(country -> country.substring(0, 1).toUpperCase() + country.substring(1));
}

@Test
public void getCountryTest() {
    StepVerifier
            .create(getCapitalizedCountry(
                    Flux.just("korea", "england", "canada", "india")
            )).expectSubscription()
            .recordWith(ArrayList::new) // 파라미터로 전달한 Java Collection에 emit된 데이터를 추가
            .thenConsumeWhile(country -> !country.isEmpty()) // 조건 일치 데이터만 다음 단계에서 소비 가능
            .consumeRecordedWith( // Collection에 기록된 데이터를 소비한다.
                    countries -> {
                        assertTrue(countries.stream().allMatch(country -> Character.isUpperCase(country.charAt(0))));
                    }
            ).expectComplete()
            .verify();
}

@Test
public void getCountryTest2() {
    StepVerifier.create(getCapitalizedCountry(
            Flux.just("korea", "england", "canada", "india")
    )).expectSubscription()
      .recordWith(ArrayList::new)
      .thenConsumeWhile(country -> !country.isEmpty())
      .expectRecordedMatches(countries -> countries.stream().allMatch(country -> Character.isUpperCase(country.charAt(0))))
      .expectComplete()
      .verify();
}
```
- 1번 테스트 consumeRecordedWith() + assertXXXX() 조합
- 2번 테스트 expectRecordedMatches() + Predicate 조합

## 2. TestPublisher를 사용한 테스팅
- reactor-test가 지원하는 테스트 전용 Publisher이다.
- 아래와 같은 Signal 유형을 발생시킨다.
  - next(T) 또는 next(T, T, ...): 1개 이상의 onNext Signal
  - emit(T ...): 1개 이상의 onNext Signal을 발생시킨 후, onComplete Signal을 발생시킨다.
  - complete(): onComplete Signal을 발생시킨다.
  - error(Throwable): onError Signal을 발생시킨다.

### 정상 동작하는(Well-behaved) TestPublisher
```java
// 테스트 대상이 되는 메서드
private static Flux<Integer> divideByTwo(Flux<Integer> source) {
    return source.map(data -> data/2);
}


@Test
public void divideByTwoTest() {
    TestPublisher<Integer> source = TestPublisher.create(); // TestPublisher 생성

    StepVerifier
            .create(divideByTwo(source.flux())) // Flux로 동작하도록
            .expectSubscription()
            .then(() -> source.emit(2, 4, 6, 8, 10)) // emit할 데이터 정의
            .expectNext(1, 2, 3, 4, 5)
            .expectComplete()
            .verify();
}
```
- 프로그래밍 방식으로 Signal을 발생시키며 원하는 상황을 미세하게 재연이 가능하다.
- 위 테스트에서는 큰 의미가 없어보일 수 있지만 테스트 상황이 복잡할 때 조건을 미세하게 수정하며 작업하기 편리하다.

### 오동작하는(Misbehaving) TestPublisher
- 오동작하는 TestPublisher를 만들어 Reactive Streams의 사양을 위반하는지 테스트가 가능하다.
- 오동작하는 Publisher란 리액티브 스트림즈 사양 위반 여부를 사전에 체크하지 않는다는 뜻.
- 즉, 사양을 위반해도 데이터를 emit할 수 있다.
```java
@Test
public void divideByTwoTest2() {
    TestPublisher<Integer> source = TestPublisher.createNoncompliant(TestPublisher.Violation.ALLOW_NULL); // 데이터가 null이라도 정상 동작하는 TestPublisher
    // TestPublisher<Integer> source = TestPublisher.create(); 정상 동작 Publisher를 사용하면 emit 과정에서 NullPointerException이 나온다

    var dataSource = Arrays.asList(2, 4, 6, 8, null);

    StepVerifier
            .create(divideByTwo(source.flux()))
            .expectSubscription()
            .then(() -> {
                dataSource.stream()
                        .forEach(data -> source.next(data));
                source.complete();
            })
            .expectNext(1, 2, 3, 4)
            .expectError()
            .verify();
}
```
- Well-behaved TestPublisher를 사용할 때와 Misbehaving TestPublisher를 사용할 때 NullPointerException이 발생하는 시점이 달라진다.
- 추가적인 위반 조건
  - ALLOW_NULL: 데이터가 null이어도 emit
  - CLEANUP_ON_TERMINATE: Terminal Signal(onComplete, onError, emit)을 연달아 여러 번 보낼 수 있도록 한다.
  - REQUEST_OVERFLOW: 요청 개수보다 더 많은 Signal일 발생해도 IllegalStateException이 발생하지 않고 다음 호출 진행


## 3. PublisherProbe를 사용한 테스팅
- Sequence의 실행 경로를 테스트할 수 있다.
- 주로 조건에 따라 Sequence가 분기되는 경우, Sequence의 실행 경로를 추적해 정상 동작했는지 테스트가 가능하다.
```java
// 테스트 대상 메서드 
private static Mono<String> processTask(Mono<String> main, Mono<String> stanby) {
    return main.flatMap(message -> Mono.just(message)).switchIfEmpty(stanby);
}

private static Mono<String> supplyMainPower() {
    return Mono.empty();
}

private static Mono sulpplyStandbyPower() {
    return Mono.just("# supply Stanby Power");
}

@Test
public void publisherProbeTest() {
    PublisherProbe<String> probe =
            PublisherProbe.of(sulpplyStandbyPower()); // 테스트 대상 Publisher를 PublisherProbe.of()로 래핑

    StepVerifier
            .create(processTask(supplyMainPower(), probe.mono()))
            .expectNextCount(1)
            .verifyComplete();

    probe.assertWasSubscribed(); // sulpplyStandbyPower()가 구독되었는가?
    probe.assertWasRequested(); // sulpplyStandbyPower() 요청을 했는가?
    probe.assertWasNotCancelled(); // sulpplyStandbyPower() 중간에 취소는 없었는가?
}
```
- PublisherProbe.of() 메서드로 테스트 대상 Publisher를 래핑한다.
- 이후 mono나 flux로 사용이 가능하다.
- 이후 assertWas~ / assertWasNot~ 메서드를 통해 대상 Publisher가 원하는 방식으로 동작했는지 확인이 가능하다.
- 위 테스트는 결론적으로 processTask()의 2번째 인자로 PublisherProbe가 사용되어 switchIfEmpty() 메서드가 동작했는지를 확인할 수 있다.