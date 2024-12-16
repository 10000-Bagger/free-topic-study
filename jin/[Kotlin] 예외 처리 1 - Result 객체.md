# Kotlin Result

Result는 오류 또는 데이터를 표현할 수 있는 타입이다. Java Optional이 Null이 될도 수 있는 타입을 표현했다면 Result는 실패 가능성이 있는 계산의 결과를 표현한다! <br>
Optional을 사용하는 논리와 비슷하게, 같이 외부 서비스 의존 로직이라 예외 발생이 빈번하거나, 해당 컴포넌트에서 에러가 발생할 수 있다는 것을 클라이언트에게 알리고 싶은 곳에서 사용하면 좋다. <br>

## 1.1 runCatching
가장 쉽게 사용하는 방법은 `runCatching`을 사용하는 방법이다.  <br>
아래와 같은 로직을 살펴보자.

```kotlin
return runCatching {
  loginApiClient.login(request)
}.onFailure { e ->
  if (e.errorCode != "INVALID_PASSWORD") throw e
}.getOrNull()
```
직관적으로 읽힌다, `runCatching`의 중괄호 내부에서 예외가 발생한다면 `onFailure`로 가게 된다. 에러코드에 따라 예외를 발생시키고 있다. 같은 코드를 java로 표현한다면 아래와 같다.

```java
try {
  loginApiClient.login(request)
} catch (e: LoginException) {
  if (e.errorCode == "INVALID_PASSWORD") {
    return null
  } else {
    throw e
  }
}
```
코틀린쪽이 의도 파악이 좀 더 쉽다.
성공했을 떄의 행동 또한 onSuccess로 지정할 수 있다.

```kotlin
val response = runCatching {
  login()
}.onSuccess {
  logger.info("성공!")
}.onFailure {
  logger.info("실패!")
}.getOrThrow()
```

성공시 "성공!"을 실패시 "실패!"를 내뱉는다. 이후 `getOrThrow()`라는 Optional에서 많이 본듯한 메서드를 호출해 예외를 발생시킬 수 있다.

## 1.2 Result 내부 동작 확인 onSuccess, onFailure
Result의 내부 동작을 가장 빨리 이해하는 방법은 runCatching과 onSuccess, onFailure 코드를 확인하는 것이다.

![image](https://github.com/binary-ho/BaekjoonRecord/assets/71186266/f8caad46-5cae-4e0e-af88-110500bef5ff)

runCatching은 단순하게 어떤 코드를 실행시킨 다음 결과를 Result로 Wrapping하고 있다. 성공한 경우 success로, 실패한 경우 failure로..

![image](https://github.com/binary-ho/BaekjoonRecord/assets/71186266/c6c117b8-322f-4669-bcef-d2e6cb043f10)

success의 경우 단순히 결과를 value로 갖는 Result 객체를 생성하고, failure의 경우 `createFailure`를 호출하는데, 단순히 아래와 같이 생겼다. 위 사진에 있는 internal class Failure로 감싸는 것이다. <br>

```kotlin
/**
 * Creates an instance of internal marker [Result.Failure] class to
 * make sure that this class is not exposed in ABI.
 */
@PublishedApi
@SinceKotlin("1.3")
internal fun createFailure(exception: Throwable): Any =
    Result.Failure(exception)
```

Failure 클래스는 내부적으로 exception을 가진다. <br>

![image](https://github.com/binary-ho/BaekjoonRecord/assets/71186266/a731a20d-90c7-4213-a0b0-9eb3a62e6a7c)

그리고 runCatching에서 호출했던 두 메서드는, 각각 exceptionOrNull과 isSuccess를 통해 결과를 확인하고, 받은 action을 수행한다. exceptionOrNull은 단순히 객체가 Failure 객체인지 확인한다. <br>
이런 로직들은 Result 내부적으로 많은데, 마치 Optional에서 isPresent isEmpty를 호출한느 것과 비슷하다.

![image](https://github.com/binary-ho/BaekjoonRecord/assets/71186266/9c1a9a1e-38cf-414b-be6b-1f84d669f237)

표시한 부분들을 살펴보면, is를 통해 Failure의 인스턴스인지 확인하고 결과를 반환한다. <br>

## 1.3 제공 API
이제 Result의 대략적인 내부 동작도 이해 갔을 것이다. 이제 Result의 다양한 메서드를 살펴보자. "이런 것이 있구나" 정도만 알아도 실제 구현할 때는 유연하게 생각할 수 있다.

1. `getOrNull` : 성공인 경우 결과를 가져오고, 실패인 경우 Null을 가져온다.
2. `exceptionOrNull` : 실패인 경우 exception을 발생시키고, 성공인 경우에 Null을 반환한다.
3. `getOrDefault` : 성공시엔 값을, 실패시엔 Default값을 지정해 반환한다.
4. `getOrElse` : 실패시엔 수신자 객체로 Throwable을 전달 ㅂ다는다. 
5. `getOrThrow` : 성공시엔 값을, 실패시엔 예외를 발생시킨다.
#### 6. map
성공시 원하는 값으로 변경한다. runCatching이 성공하는 경우, map을 통해 값을 변경할 수 있다. 
```kotlin
val result = runCatching { "진호" }
    .map {
        it + "짱"
    }.getOrThrow()
```

<Br>

자매품 mapCatching은 map과정에서의 실패를 catch할 수 있다.
```kotlin
val result = runCatching { "진호" }
    .mapCatching {
        함수호출()
    }.getOrDefault("바보")
        
```



#### 7. recover
map의 반대로, 실패인 경우 (예외 발생의 경우) 원하는 값으로 변경한다.
```kotlin
val result = runCatching { "진호" }
    .recover {
        it + "바보;"
    }.getOrThrow()
```
map처럼 recover도 catching이 가능하다

```kotlin
val result = runCatching { 함수1() }
    .recoverCatching {
        함수2()
    }.getOrDefault("복구")
```

## 2. 예외와 결과
오류가 발생하면, 데이터가 없다. 단지 예외만을 봔환할 뿐이고, 그 과정에서 어떤 객체를 사용했기 때문에 예외가 발생했는지는 추적하기 힘들다.
Kotlin이 Null을 다루는 방식에 대해 대해 알아봤지만 [링크](https://github.com/10000-Bagger/free-topic-study/blob/jin/kotlin-1/jin/%5BKotlin%5D%20%EC%BD%94%ED%8B%80%EB%A6%B0%EA%B3%BC%20Null.md) 
예외가 발생하는 경우, 데이터가 없는 이유를 제공하기 쉽지 않다.
데이터가 없는 모든 경우를 같은 Case로 취급하고, 어떤 이유로 데이터가 없을지 호출한 쪽에서 추측해야만 한다.. <br>
하지만 실제 개발 과정에서는 상황 얼마나 다양하겠는가? 결과가 Null인 이유를 정확히 추측하기 어려운 경우가 더욱 많을 수 밖에 없다. <br>

다음 글에서 이런 상황에 대한 Either와 그 활용을 알아보겠다. 공식적인 기능은 아니지만, 유용하다
