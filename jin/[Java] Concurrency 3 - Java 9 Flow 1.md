# Java 9 Flow

자바 9에서 리액티브 프로그래밍을 위한 `Flow`클래스가 추가 되었다. 이 클래스는 정적 컴포넌트 하나를 포함하고 있고, (싱글톤) 인스턴스화 할 수 없다. <br>

Flow는 리액티브 스트림 프로젝트의 표준에 따라, Pub-Sub Model 구현을 위한 4가지 인터페이스를 제공한다.
1. Publisher : 항목을 발행한다. 역압력에 의해 발행 속도는 제한된다.
2. Subscriber : 항목을 소비한다. Publisher가 발행한 이벤트의 리스너로 자신을 등록할 수 있다.
3. Subscription : 항목을 발행하고 소비하는 과정을 관리한다! Publisher와 Subscriber의 제어 흐름과 역압력을 관리한다
4. Processor


## 1. Subscriber


![image](https://github.com/depromeet/amazing3-be/assets/71186266/17dc8e7c-17aa-4d37-b0f5-8ea046c87ac7)

<br>

Subscriber인터페이스는 Publisher가 자신이 수신중인 이벤트를 발행할 때 호출될 수 있는 콜벡 메서드 4개를 제공한다.
```java
public interface Subscriber<T> {
  void onSubscribe(Subscription s);
  void onNext(T t);
  void onError(Throwable t);
  void onComplete();s
}
```

1. `onSubscribe`는 항상 처음에 호출된다.
2. 이어서 `onNext(T t)`는 여러번 호출될 수 있다.
3. **스트림은 영원히 지속되거나, `onComplete()`를 통해 더 이상의 데이터가 없고 종료됨을 알릴 수 있다.**
4. Publisher에 장애가 발생하는 경우, `onError()`를 호출할 수 있다. 

이를 아래와 같은 프로토콜 정의로 나타낼 수 있다.
```
onSubscribe onNext* (onError | onComplete)?
```


<br>

Subscriber가 Publisher에 자신을 등록할 때, Publisher가 최초 `onSubscribe(Subscription s)`를 호출해서 `Subscription 객체`를 전달한다. <br>

### Subscription 객체

Subscription 인터페이스는 메서드 두개를 가지고 있다.
```java
public interface Subscription {
  void request(long n);
  void cancel();
}
```

1. `request(long n)` : Subscription은 첫 번째 메서드로 Publisher에게 n개의 이벤트를 처리할 준비가 되어 있음을 알릴 수 있다.
2. 두 번째 메서드로 Subscription을 취소할 수 있는데, Publisher에게 더 이상 이벤트를 받지 않겠다고 통지한다.


이 Subscription 객체를 통해 Publisher와 Subscriber는 서로 통신할 수 있다.



### Processor
Processor 인터페이스는 단지 Publisher와 Subscriber를 상속 받을 뿐 아무런 메서드도 추가하지 않는다. <br>
이 인터페이스는 이벤트의 변환 단계를 나타낸다. Processor가 에러를 수신하는 경우, 이로 부터 회복하거나 `onError()`를 호출해 모든 Subscriber에 에러를 전파할 수 있고, 마지막 Subscriber가 Subscription을 취소하면, Processor는 자신의 Subscription을 취소함으로써 취소 신호를 전파할 수 있다.

## 2. Pub-Sub 객체간 협력 규약
Flow의 명세에는 Publisher, Subscriber의 인터페이스의 구현들이 서로 어떻게 협력해야 하는지 규칙 집합을 정의했다. <br>
이 인터페이스들을 구현할 때는 아래의 규칙들을 따라야 한다. <br>
책에는 아래 규칙들이 알 수 없는 기준으로 순서가 뒤섞여있다. 기준을 이해 못햇지만, 일단 객체를 기준으로 분류해보겠다.

### 2.1 Publisher 규약
1. Publisher는 Subscription의 request 메서드에 정의된 갯수 이하의 요소만 Subscriber에 전달해야 한다.
2. Publisher는 지정된 갯수보다 적은 수의 요소를 onNext로 전달할 수 있다.
3. 동작이 끝나면 onComplete를 호출하고, 문제가 발생하는 경우 onError를 호출해 Subscription을 종료할 수 있다.


### 2.2 Subscriber 규약 
1. Subscriber는 요소를 받아 처리할 수 있는 경우 Publisher에 알려야 한다. <br> -> Subscriber는 Publisher에 역압력을 행사할 수 있다! Subscriber가 따로 관리할 필요 없이 한번에 너무 많은 요소를 받게 되는 일을 피할 수 있다.
2. onComplete나 onError 신호를 처리하는 상황에서 "Subscriber"는 다른 Publisher나 "Subscription"의 어떤 메서드도 호출할 수 없다. <br> **그리고 Subscription이 취소 되었다고 가정해야 한다.**
3. Subscriber는 Subscription request() 메서드 호출 없이 언제든 종료 시그널을 받을 준비가 되어 있어야 한다.
4. Subscriber는 Subscription cancel()이 호출된 이후에도 한 개 이상의 onNext를 받을 준비가 되어 있어야 한다.
2. Subscriber는 onSubscribe와 onNext 메서드에서 Subscription의 `request()`를 동기적으로 호출할 수 있어야 한다.

### 2.3 Subscription 규약
1. Publisher와 Subscriber는 정확하게 Subscription을 공유해야 한다.
3. `Subscription.cancel()`은 몇 번을 호출해도 한 번 호출한 것과 같은 효과를 가져야 하고, 스레드 안전해야 한다.

## 3. 왜 구현체가 없는가?
자바는 왜 Flow API의 구현체를 제공하지 않을까? 보통 Java는 인터페이스를 제공하는 경우 구현체를 같이 제공한다. 예를 들어 List<T> 인터페이스는 아주 다양한 구현체를 제공한다. <br>
하지만 Flow의 구독자 발행자 등은 구현체가 제공되지 않는다. <br>
이는 단순히 Flow 개발 당시 다양한 리액티브 스트림 자바 코드 라이브러리가 이미 존재하기 때문이다. 원래 같은 발행-구독 사상에 기반해서 리액티브 프로그래밍을 구현했지만, 이들 라이브러리는 독립적으로 개발되었다. 그리고 이들은 공직적으로 자바 Flow를 기반으로 리액티브 개념을 구현하도록 진화했다. <br>
리액티브 스트림 구현은 매우 복잡하므로, 기존 구현을 사용하는 것을 추천한다. 대표적으로 RxJava는  Java 9를 활용해 넷플릭스에서 개발한 라이브러리이다. 이제 RxJava를 알아보자.

