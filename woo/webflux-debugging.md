# Project Reactor - Debugging
```java
public static void main(String[] args) throws InterruptedException {

    String[] fruits = new String[] {"STRAWBERRY", "BANANA", "APPLE", "MELON"};

    Flux.fromArray(fruits)
        .map(String::toLowerCase)
        .map(fruit -> fruit.substring(9))
        .map(fruitLastAlphabet -> "과일의 마지막 알파벳은: " + fruitLastAlphabet) // (1)BANANA가 해당 Operator에 입력값으로 들어가면 오류 발생!
        .subscribe(data -> System.out.println(data));

    Thread.sleep(50000L);
}

// 과일의 마지막 알파벳은: y
// [ERROR] (main) Operator called default onErrorDropped - reactor.core.Exceptions$ErrorCallbackNotImplemented: java.lang.StringIndexOutOfBoundsException: String index out of range: -3
// reactor.core.Exceptions$ErrorCallbackNotImplemented: java.lang.StringIndexOutOfBoundsException: String index out of range: -3
// Caused by: java.lang.StringIndexOutOfBoundsException: String index out of range: -3
      at java.base/java.lang.String.substring(String.java:1841)
      (생략...)
      at other.Test.main(Test.java:22)
```
- Reactor는 기본적으로 선언형 프로그래밍 방식으로 구성되고 비동기적으로 실행되기에 디버깅이 쉽지 않다.
- 때문에 Reactor에서는 디버깅 환경을 조금이나마 개선하고자 몇 가지 방법을 제공해준다.

## 1. Debug 모드를 사용한 Debugging
```java
public static void main(String[] args) throws InterruptedException {
    Hooks.onOperatorDebug(); // (1)

    String[] fruits = new String[] {"STRAWBERRY", "BANANA", "APPLE", "MELON"};

    Flux.fromArray(fruits)
        .map(String::toLowerCase)
        .map(fruit -> fruit.substring(9))
        .map(fruitLastAlphabet -> "과일의 마지막 알파벳은: " + fruitLastAlphabet)
        .subscribe(data -> System.out.println(data));

    Thread.sleep(50000L);
}

// 과일의 마지막 알파벳은: y
// [ERROR] (main) Operator called default onErrorDropped - reactor.core.Exceptions$ErrorCallbackNotImplemented: java.lang.StringIndexOutOfBoundsException: String index out of range: -3
// reactor.core.Exceptions$ErrorCallbackNotImplemented: java.lang.StringIndexOutOfBoundsException: String index out of range: -3
// Caused by: java.lang.StringIndexOutOfBoundsException: String index out of range: -3
	at java.base/java.lang.String.substring(String.java:1841)
	Suppressed: The stacktrace has been enhanced by Reactor, refer to additional information below: 
// Assembly trace from producer [reactor.core.publisher.FluxMapFuseable] :
	reactor.core.publisher.Flux.map(Flux.java:6517) // (2)
	other.Test.main(Test.java:22) // (3)
// Error has been observed at the following site(s): // (4)
	*__Flux.map ⇢ at other.Test.main(Test.java:22)
	|_ Flux.map ⇢ at other.Test.main(Test.java:23)
// Original Stack Trace:
		at java.base/java.lang.String.substring(String.java:1841)
        (생략...)
		at other.Test.main(Test.java:24)
```
- (1)과 같이 Hooks.onOperatorDebug()를 사용해 Debug 모드를 실행할 수 있다.
- Debug 모드에서는 (2), (3)과 같이 오류가 발생한 Operator와 코드 라인이 추가로 제공된다.
- 또한 오류 전파 경로를 (4)와 같이 제공해주기 때문에 오류가 어디서 시작되어 어디까지 전파되었는지를 확인할 수 있다.

## 2. checkpoint()를 사용한 Debugging
```java
public static void main(String[] args) throws InterruptedException {
    String[] fruits = new String[] {"STRAWBERRY", "BANANA", "APPLE", "MELON"};

    Flux.fromArray(fruits)
        .map(String::toLowerCase)
        .map(fruit -> fruit.substring(9)) // (1) 오류 발생!
        .map(fruitLastAlphabet -> "과일의 마지막 알파벳은: " + fruitLastAlphabet)
        .checkpoint() // (2)
        .subscribe(data -> System.out.println(data));

    Thread.sleep(50000L);
}

// 과일의 마지막 알파벳은: y
// [ERROR] (main) Operator called default onErrorDropped - reactor.core.Exceptions$ErrorCallbackNotImplemented: java.lang.StringIndexOutOfBoundsException: String index out of range: -3
// reactor.core.Exceptions$ErrorCallbackNotImplemented: java.lang.StringIndexOutOfBoundsException: String index out of range: -3
// Caused by: java.lang.StringIndexOutOfBoundsException: String index out of range: -3
	at java.base/java.lang.String.substring(String.java:1841)
	Suppressed: The stacktrace has been enhanced by Reactor, refer to additional information below: 
// Assembly trace from producer [reactor.core.publisher.FluxMapFuseable] : (3)
	reactor.core.publisher.Flux.checkpoint(Flux.java:3559)
	other.Test.main(Test.java:24)
// Error has been observed at the following site(s): (4)
	*__checkpoint() ⇢ at other.Test.main(Test.java:24)
// Original Stack Trace:
    at java.base/java.lang.String.substring(String.java:1841)
    at other.Test.lambda$main$0(Test.java:22)
    (생략...)
    at other.Test.main(Test.java:25)
```
- Debug 모드는 모든 Operator에서 스택트레이스를 캡처하는 반면 checkpoint()는 특정 Operator 체인 내의 스택 트레이스만 캡처한다.
- 위 코드와 같이 (1)에서 오류가 발생하였고 (2) 위치까지 오류는 전파될 것이다.
- 때문에 (3), (4)를 보면 checkpoint() 코드 라인에 오류가 전파되었음을 확인할 수 있다.
- 단, 위 로그만으로는 정확한 오류 위치를 파악할 수 없기에 checkpoint() 위치를 바꿔가며 확인해보면 좋을 것 같다.
- 추가로 checkpoint("체크 포인트 1")와 같이 파라미터로 Description을 주어 로그 확인을 용이하게 할 수 있다.

## 3. log()를 사용한 Debugging
```java
public static void main(String[] args) throws InterruptedException {

    String[] fruits = new String[] {"STRAWBERRY", "WATERMELON", "BANANA", "APPLE"};

    Flux.fromArray(fruits)
        .map(String::toLowerCase)
        .log()
        .map(fruit -> fruit.substring(9))
        .map(fruitLastAlphabet -> "과일의 마지막 알파벳은: " + fruitLastAlphabet)

        .subscribe(data -> System.out.println(data));

    Thread.sleep(50000L);
}

// [ INFO] (main) | onSubscribe([Fuseable] FluxMapFuseable.MapFuseableSubscriber)
// [ INFO] (main) | request(unbounded)
// [ INFO] (main) | onNext(strawberry)
// 과일의 마지막 알파벳은: y
// [ INFO] (main) | onNext(watermelon)
// 과일의 마지막 알파벳은: n
// [ INFO] (main) | onNext(banana)
// [ INFO] (main) | cancel()
// [ERROR] (main) Operator called default onErrorDropped - reactor.core.Exceptions$ErrorCallbackNotImplemented: java.lang.StringIndexOutOfBoundsException: String index out of range: -3
// reactor.core.Exceptions$ErrorCallbackNotImplemented: java.lang.StringIndexOutOfBoundsException: String index out of range: -3
// Caused by: java.lang.StringIndexOutOfBoundsException: String index out of range: -3
	at java.base/java.lang.String.substring(String.java:1841)
	at other.Test.lambda$main$0(Test.java:22)
    (생략...)
	at other.Test.main(Test.java:25)
```
- log()는 Reactor Sequence의 동작을 로그로 출력한다.
- 위 코드를 보면 log() 메서드는 .map(String::toLowerCase) Operator에서 발생한 Signal을 로그로 출력한다.
- 로그를 통해 "STRAWBERRY"와 "WATERMELON" 값들은 정상 처리되었음을 알 수 있다.
- 또한 "banana"값이 정상적으로 이후 Operator에 전달되었고 이후 오류가 발생하였음을 추론할 수 있다.