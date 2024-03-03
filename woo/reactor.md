# 리액티브 프로그래밍
## 1. 리액티브 시스템과 리액티브 프로그래밍

### (1) 리액티브 시스템이란?
- Reactive라는 단어에서도 알 수 있듯이 반응을 잘 하는 시스템을 뜻한다.
- 반응을 잘 한다는 것은 `클라이언트의 요청에 즉각적으로 응답함으로써 지연 시간을 최소화하는 것`
- 핵심 가치 3가지
    - MEANS: 비동기 메시지 기반의 통신을 통해 구성 요소 간 느슨한 결합, 격리성, 위치 보장성이 보장되어야 함
    - FORM: 탄력성과 회복성을 가지는 시스템
        - 탄력성 - 시스템의 작업량이 변화해도 일정한 응답을 유지
        - 회복성 - 시스템에 장애가 발생하더라도 장애 발생 지점 이외의 시스템은 여전히 응답 가능하고, 발생 지점만 복구하면 된다는 의미
    - VALUE: 시스템의 처리량을 자동으로 확장/축소하는 탄력성을 확보함으로써 즉각적으로 응답 가능한 시스템을 구축할 수 있음을 의미
- 빠른 응답성을 바탕으로 확장이 용이한 시스템을 구축하는데 활용 가능

### (2) 리액티브 프로그래밍이란?
- 리액티브 시스템을 구축하는데 필요한 프로그래밍 모델
- Non-Bloccking I/O 방식의 통신을 사용
- 특징 2가지
    - 선언형 프로그래밍
        - Java Stream pipeline을 생각하면 쉽다
        - 동작을 구체적으로 명시하지 않고 목표만 선언한다
        - 여러 동작이 메서드 체인을 활용해 한 문장으로 표현됨
        - 메서드 체인은 데이터 흐름을 한 눈에 파악 가능해 가독성이 좋고 코드가 간결해진다 (어떻게 짜느냐에 따라 다를듯..)
        - 함수형 프로그래밍으로 구성된다
            - filter(number -> number > 6 && (number % 2 != 0))
    - data streams와 propagation of change
        - data streams - 데이터가 지속적으로 발생한다는 특징
        - propagation of change - 지속적으로 데이터가 발생할 때마다 이벤트를 발생시키면서 데이터를 계속 전달한다는 특징

### (3) 리액티브 프로그래밍 코드 구성
#### Publisher
- 입력으로 들어오는 데이터를 제공하는 역할
#### Subscriber
- Publisher가 제공한 데이터를 전달 받아서 사용하는 주체
#### Data Source / Data Stream
- Data Source: 최초로 생성되는 데이터 그 자체
- Data Stream: Publisher의 입력으로 들어오는 데이터 형태
- 둘은 같다고 봐도 무방하다
#### Operator
- Publisher와 Subscriber 사이에서 적절한 가공처리를 담당하는 주체


## 2. 리액티브 스트림즈
- 리액티브 라이브러리를 어떻게 구현할지 정의한 표준 사양을 뜻한다.
- 정확히는 데이터 스트림을 Non-Blocking이면서 비동기적인 방식으로 처리하기 위한 리액티브 라이브러리 표준 사양
### (1) 리액티브 스트림즈 구성 요소와 동작 방식
| 컴포넌트         | 설명                                                                                                                 |
|--------------|--------------------------------------------------------------------------------------------------------------------|
| Publisher    | 데이터를 생성하고 통지(발행, 게시, 방출)하는 역할                                                                                      |
| Subscriber   | 구독한 Publisher로부터 통지된 데이터를 전달받아서 처리하는 역할                                                                            |
| Subscription | Publisher에 요청할 데이터의 개수를 지정하고, 데이터의 구독을 취소하는 역할                                                                     |
| Processor    | Publisher와 Subscriber의 기능을 모두 가지고 있다. 즉, Subscriber로서 다른 Publisher를 구독할 수 있고, Publisher로서 다른 Subscriber가 구독할 수 있다. |


![publisher-subscriber.jpg](img/publisher-subscriber.jpg)
- Subscription.request를 통해 데이터 개수를 지정하는 이유
  - 실제 Publisher와 Subscriber는 다른 스레드에서 비동기적으로 상호작용하기 때문에 Produce와 Consume 속도를 맞추기 위한 작업이다.
### 코드로 보는 리액티브 스트림즈 컴포넌트
#### (1) Publisher
```java
public interface Publisher<T> {
    void subscribe(Subscriber<? super T> var1);
}
```
- 파라미터로 전달받은 Subscriber를 등록하는 역할의 subscribe()만 존재한다.
- Kafka의 Pub/Sub 구조와 다르게 Broker의 존재가 없기 때문에 구독 등록 메서드가 Publisher 내부에 존재하는 점이 특징이다.

#### (2) Subscriber
```java
public interface Subscriber<T> {
    void onSubscribe(Subscription var1);

    void onNext(T var1);

    void onError(Throwable var1);

    void onComplete();
}
```
- onSubscribe(Subscription var1): Subscription 객체를 바탕으로 구독 시작 시점에 `요청할 데이터 개수 지정`또는 `구독을 해지` 처리를 하는 역할
- onNext(): Publisher가 통지한 데이터를 처리하는 역할
- onError(): onNext() 과정에서 에러가 발생했을 때 에러를 처리하는 역할
- onComplete(): Publisher가 데이터 통지를 완료했음을 알릴 때 사용된다. 통지 완료 후 후처리 로직이 들어갈 수도 있다.
#### (3) Subscription
```java
public interface Subscription {
    void request(long var1);

    void cancel();
}
```
- request(long n): 구독 데이터의 개수를 요청하는 역할
- cancel(): 구독을 해지하는 역할
#### (4) Processor
```java
public interface Processor<T, R> extends Subscriber<T>, Publisher<R> {
}
```
- Processor의 경우 Subscriber와 Publisher를 상속하고 있다.
- 즉, Processor만의 기능은 따로 없고 Subscriber와 Publisher의 역할을 모두 수행할 수 있다는 특징이 있다.

### (2) 리액티브 스트림즈 관련 용어 정리
#### Signal
- Publisher와 Subscriber간에 주고받는 상호작용
- onSubscribe, onNext, onComplete, onError, request, cancel 메서드를 Signal이라 표현한다.
- onSubscribe, onNext, onComplete, onError: Publisher가 Subscriber에게 보내는 Signal
- request, cancel: Subscriber가 Publisher에게 보내는 Signal

#### Demand
- Subscriber가 Publisher에게 요청한 데이터이며 Publisher가 아직 전달하지 않은 데이터를 뜻한다.

#### Emit
- Publisher가 Subscriber에게 데이터를 전달하는 것을 의미한다.
- 즉, 데이터를 내보낸다는 의미 정도로 이해하면 됨

#### Upstream/Downstream
```java
public static void main(String[] args) {
    Flux
        .just(1, 2, 3, 4, 5, 6, 7)
        .filter(n -> n % 2 == 0)
        .map(n -> n * 2)
        .subscribe(System.out::println)
}
```
- 리액티브 프로그래밍에서는 위와 같은 메서드 체인 방식으로 코드가 작성된다.
- 메서드 체인으로 작성될 수 있는 이유는 각 메서드의 반환 객체가 동일하게 Flux이기 때문이다.
- 이때 특정 Flux를 기준으로 자신보다 상위에 있는 Flux는 Upstream, 하위에 있는 Flux는 Downstream이 된다.

#### Sequence
- Publisher가 emit하는 데이터의 연속적인 흐름
- 즉, 다양한 Operator로 생겨난 데이터의 연속적인 흐름을 뜻한다.

#### Operator
- 위 예시 코드에서 사용된 연산자(just, filter, map)들을 통틀어 Operator로 지친한다.

#### Source
- 최초라는 의미로 사용되며 Original이라고도 불린다
- 즉, 가장 먼저 생성된 무언가로 생각하면 될 것 같다.

### (3) 리액티브 스트림즈 구현 규칙

#### Publisher 구현 규칙
- 개수 제한: Subscriber로 보내는 onNext signal의 개수는 Subscriber가 요청한 데이터 개수보다 항상 작거나 같아야 한다.
- 종료 조건: Subscriber가 요청한 것보다 적은 수의 onNext signal을 보내고 onComplete 또는 onError를 호출하여 구독을 종료할 수 있다.
- 오류 처리: 데이터 처리에 실패할 경우 onError signal을 보내야 한다.
- 성공 처리: 데이터 처리가 성공적으로 종료되면 onComplete signal을 보내야 한다.
- 취소 조건: Publisher가 onError 또는 onComplete signal을 보내는 경우 해당 구독은 취소된 것으로 간주되어야 한다.
- 취소 이후 동작: 
  - 종료 상태 signal(onError, onComplete)을 받으면 더 이상 signal이 발생ㅎ되지 않아야 한다.
  - 구독 취소 이후에 Subscriber는 signal을 받는 것을 중지해야 한다.

#### Subscriber 구현 규칙
- 구독 조건: onNext signal을 수신하기 위해 request(n)을 통해 Demand signal을 Publisher에게 보내야 한다.
- 종료 메서드 조건: onComplete(), onError(Throwable t) 메서드에서 Subscription, Publisher의 메서드를 호출해서는 안 된다.
- 종료 메서드 역할: onComplete(), onError(Throwable t) signal 수신 이후는 구독이 취소된 것으로 간주해야 한다.
- cancel()의 역할: 구독이 필요하지 않은 경우 cancel() 메서드를 호출해야 한다.
- onSubscribe() 호출 제한: Subscriber.onSubscribe()는 지정된 Subscriber에 대해 최대 1번만 호출되어야 한다.
  - 동일 구독자는 최대 1번만 구독 가능하다는 의미

#### Subscription 구현 규칙
- Subscription.request: 
  - Subscriber가 onNext, onSubscriber 내에서 동기적으로 Subscription.request를 호출하도록 허용해야 한다.
  - 구독 취소 이후의 request(long n)은 효력이 없어야 한다.
  - 구독 취소 이전에 request(long n)의 n이 0보다 작거나 같으면 IllegalArgumentException과 함께 onError signal을 보내야 한다.
- Subscription.cancel():
  - 구독 이후의 cancel() 호출은 효력이 없어야 한다.
  - 구독이 취소되지 않은 동안에는 Publisher가 Subscriber에게 보내는 signal을 결국 중지하도록 요청하는 역할을 한다.
  - 또한 Publisher가 해당 Subscriber에 대한 참조를 삭제하도록 요청해야 한다.
- cancel(), request()호출에 대한 응답으로 예외를 던질 수 없다.
- 구독은 무제한 수의 request 호출이 가능해야 하고, 2^62-1rodml Demand를 지원해야 한다.

### (4) 리액티브 스트림즈 구현체

##  Blocking I/O와 Non-Blockinig I/O