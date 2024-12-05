# Don’t hardcode Coroutine Dispatchers when creating new coroutines

## 개요

coroutine을 사용하면서 `withContext(Dispatchers.IO)` 과 같이 hardcode된 dispatcher를 사용했는데, 해당 방식이 지양해야한다는 피드백을 받아 관련 내용을 공부했습니다.

참고 링크:
- https://developer.android.com/kotlin/coroutines/coroutines-best-practices#inject-dispatchers
- https://docs.spring.io/spring-framework/reference/languages/kotlin/coroutines.html

## DO inject Dispatcher, DO NOT hardcode Dispatchers

구글의 예제나 안드로이드 공식 문서 등 코루틴 예시들을 보면, 새로운 코루틴을 생성하거나 `withContext` 를 호출할 때 `Dispatchers` 를 하드코딩하는 경우를 많이 찾아볼 수 있다.

하지만 Android의 코루틴 권장사항 문서를 보면 [Don’t hardcode `Dispatchers` when creating new coroutines](https://developer.android.com/kotlin/coroutines/coroutines-best-practices#inject-dispatchers) 라는 내용이 가장 먼저 등장한다.

```kotlin
// DO inject Dispatchers
class NewsRepository(
    private val defaultDispatcher: CoroutineDispatcher = Dispatchers.Default
) {
    suspend fun loadNews() = withContext(defaultDispatcher) { /* ... */ }
}

// DO NOT hardcode Dispatchers
class NewsRepository {
    // DO NOT use Dispatchers.Default directly, inject it instead
    suspend fun loadNews() = withContext(Dispatchers.Default) { /* ... */ }
}
```

위 내용에 따르면 실제 애플리케이션에서는 디스패처를 주입해서 사용해야 한다고 권장한다. 왜일까?

- Dependency Injection(의존 관계 주입, DI)은 객체를 직접 생성하지 않고 외부로부터 필요한 객체를 받아서 사용함으로써 객체의 생성과 사용을 분리할 수 있게 해준다.
- 디스패처를 주입해서 사용하면 디스패처를 구성(configurable)할 수 있게 되고,
- 단위 테스트에서 디스패처를 테스트 디스패처로 쉽게 교체해서 테스트를 더 유연하게 만들 수 있으므로 테스트하기가 더욱 쉬워진다는 장점이 있다.

### 용어 정리

- Dispatcher
    - Threaddp Operation을 분배하는 역할을 수행
    - Dispatcher의 종류는 아래와 같다.
        - Default: 기본 Thread Pool. 별도의 설정이 없을 시, CPU의 Core 개수와 같은 thread를 가진다.
        - IO: IO용 Thread Pool. 별도의 설정이 없을 시, 64개의 thread를 가진다. 이 thread는 Default Dispatcher와 공유될 수 있다.
        - Main: UI Thread에서만 동작시킨다.
- Context
    - Dispatcher와 연결되어 여러가지 추가 기능을 부여하는 역할을 한다.
        - 연결되는 속성들은 ContextElement라 한다. 자주 사용되는 종류는 아래와 같다.
            - SupervisorJob: 일반 Job은 Coroutine이 실패할 경우, Parent Coroutine 까지 Cancel 시키는 것이 기본 동작이다. SupervisorJob은 해당 Coroutine의 Child만 취소하도록 한다.
            - CoroutineName: Coroutine 디버깅을 위한 이름을 붙일 수 있다.
    - 새로운 Coroutine은 Parent Coroutine의 Context를 상속받는다.
- Scope
    - Coroutine의 LifeCycle을 관리한다.
    - 기본적으로 GlobalScope를 제공하며, 이 Scope는 Application 자체와 LifeCycle을 함께한다.
        - SpringBoot 애플리케이션은 기본적으로 애플리케이션 전체가 아닌 Spring과 LifeCycle을 함께 해야하기 때문에, 기본적으로 제외하고 생각하는 것이 좋음.
    - Scope는 최소한의 범위에서 작동하는 것이 좋다.
- Job
    - Coroutine 실행의 결과물. 대기 / 취소 등의 작업이 가능하다.

## WebFlux와 Coroutine
