# Reactor Testing
## 1. StepVerifier를 사용한 테스팅

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