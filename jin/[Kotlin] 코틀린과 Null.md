# 옵셔널에서 널이 될 수 있는 타입으로

## 1. "없음"에 대한 표현 - Optional
자바 8 이전의 자바 개발자들은 별도로 표시하지 않으면 참조는 Null이 될 수 없다고 간주했다. 그래서 Null이될 수 있는 경우 `addressLineOrNull`와 같이 필드 이름 뒤에 OrNull을 붙여가며 Null 가능성을 표기했다. <br> 

이러한 방법은 코드가 번잡스러워지고, 계속해서 NullPointer Exception에 대한 경계를 늦추지 못하게 만들었다. 이후 어노테이션으로 확인하는 등 다양한 방법이 도입됐었으나, Java 8에 Optional이 도입되면서 사용되지 않게 되었다. <br>

자바는 null이라는 무거운 짐에 시달리고 있었고, 스칼라의 "없음"을 표시할 수 있는 기능을 차용해 **선택적인 타입 Optional을 도입하게 되었다.**  <br> <br>

이러한 Optional은 항상 논의의 대상이었다. 안전하게 null을 다룰 수 있지만, Wrapping하는 오버헤드가 있고, 사용하는데 있어 여러 주의를 요했다. => [Item 55. 옵셔널 반환은 신중히 해라.](https://github.com/binary-ho/TIL-public/blob/main/Effective%20Java/Item%2055.%20%EC%98%B5%EC%85%94%EB%84%90%20%EB%B0%98%ED%99%98%EC%9D%80%20%EC%8B%A0%EC%A4%91%ED%9E%88%20%ED%95%B4%EB%9D%BC.md) 



## 2. 코틀린의 Null


반대로 코틀린은 Null을 포용한다! 선택성을 라이브러리가 아닌 타입 시스템의 일부로 넣었다. 덕분에 일관성 있게 "없음"을 다룰 수 있다.  <Br>

코틀린에서는 널이 될 수 있는 타입을 구분할 수 있다. **만약 어떤 `Int`변수가 nullable이라면, `Int?`와 같이 표기하면, 이 값은 null을 가질 수 있다.** <br>

또한 코틀린 타입 시스템 안에서 T는 T?의 하위 타입으로 구현 되어 있기 때문에, 널이 될 수 없는 타입을 널이 될 수 있는 타입 T?가 필요한 곳에 항상 사용할 수 있다. 반환타입을 강화해도 호환성이 유지된다. 그냥 Optional을 사용해버리면 이런 변환이 쉽지 않다. <br>

우리는 Non-nullable 타입을 사용하면, NullPointerException에 대해 걱정하지 않아도 되서 너무 좋다 ㅎㅎ

## 3. nullable 다루기

코틀린은 Nullable을 다루기 위한 여러 장치를 제공한다.
### 3.1 Safe Call
nullable 변수의 내부에 접근할 때, 단순이 `.`  참조 연산자를 사용할 수 없다. 왜냐하ㅕㅁㄴ 해당 변수가 Null인 경우 NullPointerException이 발생할 수 있기 때문이다. 따라서 아래와 같은 `?.`연산자 Safe Call을 제공한다!
```kotlin
// 불가능
return cheering.count

// safe call!
return cheering?.count ?: 0
```

만약, Safe Call을 한 객체가 Null이라면 어떻게 작동할까? **단순하게, Call을 없던 일로 하고, Null을 반환한다.** <br>
그래서 엘비스 연산자와 응용하면 좋다.
### 3.2 엘비스 연산자
엘비스 연산자 `?:`를 통해 어떤 값이 null인 경우, 다른 값으로 대체할 수 있다. Java Optional의 `Optional.getOrElse()`와 동일한 역할을 하는 것이다.

```kotlin
return cheering?.count ?: 0
```

위 코드는 
1. cheering이 null인 경우 count를 호출하지 않고 null을 반환한다.
2. 엘비스 연산자가 `?:` 값이 null임을 확인하고, 0을 기본 값으로 반환한다.
3. 즉, cheering이 null인 경우 return은 0이다.

### 3.3 Null아님 표시
아래와 같이 `!!`를 통해 이 Nullable은 null이 아님을 assert할 수도 있다. <br>
물론 책임은 모두 프로그래머가 지고, null인 경우 NPE가 발생한다.
```kotlin
return cheering!!.count
```


### 3.4 완벽하지 않은 코틀린 널 처리
NPE는 아무것도 가리키지 않는 Null Pointer의 식별자를 역참조 할 때 발생한다. 데이터가 필요해 신나게 가지러 갔는데, 아무 것도 없다는 사실을 발견하면 이런 버그가 발생한다. 이때 식별자가 Null을 가리키고 있다고 이야기하며, 이는 Null 참조를 허용하는 프로그램에서 가장 자주 발생하는 버그이. <br> <br>

토니 호어가 발명해낸 개념인 Null은 그를 후회하게 만들었다. 그는 Null의 발명을 십억 불짜리 실수라고 부른다. 본래 컴파일러가 참조 사용이 안전한지 확신하기 위해 도입했고, 구현이 너무 쉬웠기 때문에 일단 구현했다. 이로 인해 수많은 오류와 취약점, 시스템 고장이 생겨났고, 지난 40년간 모두가 고통 받았다. <br> <br>

그래서 지금 null을 쓰지 말자는 것이 상식인가? 그렇지 않다. 자바 표준 라이브러리 Socket의 생성자 중에서는 파라미터에 null이 들어오는 것이 올바른 경우도 있다. 이런 경우를 Business Null이라고 부르거나 Sentinal Value라고 부른다. 없음을 표현하기 위해 불가피한 상황이 있다는 것이다. 이 밖에도 자바 표준 라이브러리에서 데이터의 없음을 Null로 표현하는 경우가 많다. (그 흔한 Map에도 있음) <br>

Kotlin 표준 라이브러리 또한 마찬가지다. 널이 될 수 있는 타입을 파라미터로 받고, 반환한다. <br>

이는 자바와의 하위 호환성 유지에 대한 집착으로 인해 발생하는데, 아래 코드들은 널 처리 방식이 다르다.


1. Map<K, V>.get(key) : 값이 없는 경우 null을 반환한다
2. List<T>.get(index) : 값이 없는 경우 indexOutOfBoundsException을 던진다
3. Iterable<T>.first() : null을 반환하는 대신, NoSuchElementException을 발생시킨다.

