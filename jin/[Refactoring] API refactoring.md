# API 리팩터링
좋은 API란 무엇일까?
어떻게 이해하기 쉽고 사용하기 쉬운 API를 만들 수 있을까?

1. 질의 함수와 변경 함수 분리하기: 갱신 API와 질의 API의 분리
2. 함수 매개변수화하기: 값 하나 때문에 여러개로 나뉜 함수를 하나로 합치기 위한 기법
3. 플래그 인수 제거하기: 그저 함수의 동작 모드를 전환하기 위한 용도로 쓰이는 인수 제거
4. 객체 통째로 넘기기: 데이터 구조가 함수 사이를 건너 다니며 필요 이상으로 분해되는 것을 막고, 하나의 객체로 전달.
5. 매개변수를 질의 함수로 바꾸기, 질의 함수를 매개변수로 바꾸기
6. 세터 제거하기: 불변을 유지하는 방법
7. 생성자를 팩터리 함수로 바꾸기
8. 함수를 명령으로 바꾸기, 명령을 함수로 바꾸기: 많은 데이터를 받는 복잡한 함수를 잘게 쪼개기 위함. 적용하면 함수 추출이 수월해짐
9. 함수 매개변수화 하기
10. 플래그 인수 제거하기


## 11.1 CQRS
커맨트 쿼리 책임 분리를 통해 외부에서 관찰할 수 있는 Side Effect가 없는 조회 API를 만들 수 있다.
이런 API는 몇 번을 호출해도 문제가 없기 때문에, 우리가 신경 쓸 일이 확연히 줄어든다.

이러한 CQS에 대한 이야기는 아주 오래 전 부터 들어왔다. 하지만 처음 배웠을 때와 아주 나중에 DDD 관련 책에서 CQRS를 접했을 때는 완전히 다르게 느껴졌는데, CQRS의 대상을 DB 서버 레벨로 확장한 예시를 접했기 때문이다.

DB 서버를 다중화 할 때 서버 레벨에서 Read 서버와 Write 서버를 분리할 수 있다. 통계상 Read는 Write 보다 10배가 많다고 한다. 그리고 Write는 경우에 따라 매우 무거울 수 있다. 데이터 정합성을 위한 각종 Lock이나 트랜잭션, 인덱스 테이블 재구성 등의 다양한 이유로 Read보다 무거운 연산일 수 있다. <br>

따라서, DB를 다중화하고 Read용 서버와 Write용 서버를 분리하는 아이디어는 부하를 낮추는 관점에서 좋은 아이디어이다. 물론 Read DB와 Write DB가 분리되면서 데이터가 일시적으로 다를 수 있음에 유의해야 한다.

- [CQRS](https://github.com/binary-ho/TIL-public/blob/main/%EB%8F%84%EB%A9%94%EC%9D%B8%20%EC%A3%BC%EB%8F%84%20%EA%B0%9C%EB%B0%9C%20%EC%8B%9C%EC%9E%91%ED%95%98%EA%B8%B0/11.%20%EB%AA%A8%EB%8D%B8%20%EB%8B%A8%EC%9C%84%20CQRS.md)

## 11.2 함수 매개변수화하기 
값 하나 때문에 여러개로 나뉜 함수를 하나로 합치기 위한 기법이다.

예를 들어 아래와 같은 두 함수를 하나로 합치자는 것이다.

```js
const tenPercent = 1.1;
const fivePercent = 1.05;

function raiseTenPercent(person) {
    person.salary = person.salary.multiply(tenPercent);
}

function raiseFivePercent(person) {
    person.salary = person.salary.multiply(fivePercent);
}
```

```js
function raise(person, factor) {
    person.salary = person.salary.multiply(1 + factor);
}
```

### 장점
책에서 말하는 장점은 다음과 같다.
1. 함수의 범용성이 증대된다.
2. 중복을 없앨 수 있다.

<br>

하지만 나는 반대로 쓰는 경우가 더 많은 것 같다.
Util 객체의 함수인 경우나, 실제로 어떤 값이 들어올지 정해지지 않은 경우 당연히 위와 같이 합친다.

하지만, 5퍼센트, 10퍼센트 인상만 있는 경우 함수 사용을 제한하기 위해 반대로 `raiseFivePercent`, `raiseTenPercent`와 같이 함수를 분리한다

또한 조금은 결합도를 높이는 일로 느껴진다. 왜냐하면 호출하는 쪽에서 factor값을 정확히 알고, 인터페이스 내부에서 정확히 어떤 일이 일어나는지 알 수 있는 상황에서 저 함수를 사용하는 것 처럼 보인다. <br>

하지만 `raiseFivePercent` 이렇게 되어 있다면.. 안에서 무슨 일이 일어나는지는 모르겠지만 five percent가 raise되겠군... 할 수 있을 것 같다.

구체적인 예시를 들자면, 어떤 주문의 상태를 바꿀 때
`changeOrderState(OrderState.배송_완료)` 이런 식으로 쓰지 않고, `changeOrderState_배송_완료()`를 더욱 선호한다.

이렇게 하면 누군가 상태를 바꿀 때, 잘못된 Enum 상수를 넣어줘서 실수하는 일도 방지할 수 있고, 배송 상태를 배송 완료 상태로 변경하는 지점들을 더 빨리 찾아낼 수 있다. 왜냐하면 인텔리제이와 같은 IDE는 함수를 사용하는 부분을 아주 빠르게 찾아주기 때문이다.

<br>


## 11.3 플래그 인수 제거
옛날에 직접 정리했던 플레그 인수 제거 방법을 옮겨보겠다.

<Br> <br>

플래그 인수 제거는 인수 하나를 제거해 매개변수를 없애고, 함수를 좀 더 분명하게 이해하는 것을 돕는다. <br>
어떤 조건 단 하나로, 함수의 동작 방식이 바뀌는 경우가 있다. 이를 플래그 인수라고 한다. <br> 


예를 들어 손에 포크를 들고 있는지, 젓가락을 들고 있는지에 따라 먹는 방식이 달라지는 함수가 있다. 그리고 손에 어떤 식기를 들고 있는지 인수로 받아서 함수 안에서 if문이나 switch문으로 확인해 동작을 바꾼다고 생각해보자. 이 경우, 플래그는 `손에 든 식기`이다. <br> 


플래그 인수는 잘 만들지 않으면, 어떤 플래그가 있고 플래그별로 어떻게 행동이 다른지 알기 어렵다. <br> 예를 들어 아래 코드를 확인해보자.

```java
deliveryDate = getDeliveryDate(order, true);

...

deliveryDate = getDeliveryDate(order, false);
```

여기서 메서드의 2번째 파라미터가 플래그로써 쓰이는데, 대체 이게 뭘 의미할까

```java
// 예제이기 때문에 냄새 포인트가 많아도 너그럽게 용서 바랍니다!!
public LocalDate getDeliveryDate(Order order, boolean isRush) {
  if (isRush) {
    int deliveryTime;
    if (order.getState() == OrderState.MA || order.getState() == OrderState.CT) deliveryTime = 1;
    else if (order.getState() == OrderState.NY || order.getState() == OrderState.NH) deliveryTime = 2;
    else deliveryTime = 3;

    return order.getPlaceOn.plusDays(1 + deliveryTime);
  }

  int deliveryTime;
    if (order.getState() == OrderState.MA || order.getState() == OrderState.CT || order.getState() == OrderState.NY) deliveryTime = 2;
    else if (order.getState() == OrderState.ME || order.getState() == OrderState.NH) deliveryTime = 3;
    else deliveryTime = 4;

    return order.getPlaceOn.plusDays(2 + deliveryTime);
}
```

이 코드에서 일단 조건문을 분해해보자. <br>

```java
// 예제이기 때문에 냄새 포인트가 많아도 너그럽게 용서 바랍니다!!
public LocalDate getDeliveryDate(Order order, boolean isRush) {
  if (isRush) {
    return getRushDeliveryDate(order);
  }
  return getRegularDeliveryDate(order);
}

private LocalDate getRushDeliveryDate(Order order) {
  int deliveryTime;
  if (order.getState() == OrderState.MA || order.getState() == OrderState.CT) {
    deliveryTime = 1;
  }
  else if (order.getState() == OrderState.NY || order.getState() == OrderState.NH) {  
    deliveryTime = 2;
  }
  else { 
    deliveryTime = 3;
  }

  return order.getPlaceOn.plusDays(1 + deliveryTime);
}

private LocalDate getRegularDeliveryDate(Order order) {
  int deliveryTime;
  if (order.getState() == OrderState.MA || order.getState() == OrderState.CT || order.getState() == OrderState.NY) {
    deliveryTime = 2;
  }
  else if (order.getState() == OrderState.ME || order.getState() == OrderState.NH) {
    deliveryTime = 3;
  }
  else {
    deliveryTime = 4;
  }

  return order.getPlaceOn.plusDays(2 + deliveryTime);
}
```
책에선 여기까지만 했는데, 더 나눠보면 좋을거 같다. 
```java
// 예제이기 때문에 냄새 포인트가 많아도 너그럽게 용서 바랍니다!!
public LocalDate getDeliveryDate(Order order, boolean isRush) {
  if (isRush) {
    return getRushDeliveryDate(order);
  }
  return getRegularDeliveryDate(order);
}

private LocalDate getRushDeliveryDate(Order order) {
  int deliveryTime = getRushDeliveryTime(order.getState());
  return order.getPlaceOn.plusDays(1 + deliveryTime);
}

private int getRushDeliveryTime(OrderState state) {
  if (state == OrderState.MA || state == OrderState.CT) {
    return 1;
  }
  if (state == OrderState.NY || state == OrderState.NH) {  
    return 2;
  }
  return 3;
}

private LocalDate getRegularDeliveryDate(Order order) {
  int deliveryTime = getRegularDeliveryTime(order.getState());
  return order.getPlaceOn.plusDays(2 + deliveryTime);
}

private int getRushDeliveryTime(OrderState state) {
  if (state == OrderState.MA || state == OrderState.CT || state == OrderState.NY) {
    return 2;
  }
  if (state == OrderState.ME || state == OrderState.NH) {
    return 3;
  }
  return 4;
}
```


그 다음 아래와 같이 플래그를 없앨 수 있을 것이다.

```java
// Before
deliveryDate = getDeliveryDate(order, true);
... 생략
deliveryDate = getDeliveryDate(order, false);


// After
deliveryDate = getRushDeliveryDate(order);
... 생략
deliveryDate = getRegualarDeliveryDate(order);
```

이렇게하면 더 의도도 잘 드러나고, 파라미터가 많은 경우 파라미터도 줄일 수 있다.


## 11.4 객체를 통째로 넘기기
이 책에서 여러번 다룬 여러 인수들을 묶어 하나의 객체로 만드는 방법과는 조금 다른 방법이다. 그냥 객체에서 값을 추출해 다른 함수에 전달할 때, 추출하기 전의 객체를 전달해서 해당 함수에서 꺼내 쓰도록 만드는 기법이다. 예를 들어 아래와 같은 코드를 바꾸는 것인데

```js
// As-Is
const low = room.daysTemperature.low;
const high = room.daysTemperature.high;

if (!plan.withinRange(low, high)) {
    alert_온도_범위_이탈();
}

// To-Be
if (!plan.withinRange(room.daysTemperature)) {
    alert_온도_범위_이탈();
}
```

**책에서는 이렇게 하면 변경에 유연하다고 하는데,** <br>
**나는 이런 구현을 싫어하는 편이다.** <br>
업무중 이런 식으로 구성되어 있는 레거시 코드를 너무나도 많이 보는데, 많은 단점을 체감한다. <br>

예를 들어 어떤 객체가 있고 수많은 필드를 가지고 있다고 생각해보자.
1. 구매자 아이디
2. 구매자 이름
3. 다수의 상품 정보 (하나로 표현했지만 여러개의 필드임)
4. 다수의 판매자 정보
5. 다수의 결제 정보

간단하게 적었지만 얼추 15 ~ 20개의 필드가 있는 상황으로 생각해 주면 좋겠다. <br>
레거시 코드를 살펴보면 이 객체의 일부 필드만 사용함에도 불구하고 이 객체를 Input 객체로써 많은 곳에서 재활용한다는 것이다. 예를 들어 위 20여개의 필드들 중에서 겨우 7개만 사용함에도 Input 파라미터로써 사용하는 것이다. <br>
문제는 보통 함수도 길고 길고 복잡하게 쓰여져 있다. 그러면 나는 이 함수를 재활용 할 때 고민거리가 많아진다. **실제로 이 함수가 문제 없이 동작하기 위해 어떤 필드가 필수적으로 필요하고, 어떤 필드가 Option이며 (사실 이런 필드는 존재해선 안된다..), 어떤 필드가 불필요한지 전혀 전혀 전혀 알 수가 없다..** <br>
긴 긴 함수를 해독하며 어떤게 필요하고 어떤게 불필요한지 이해해야 한다. <br>

좋은 함수 설계란 무엇일까?  <br>
나는 사용하는 사람이 이 함수에 대해 아주 정확히 이해하고 있지 않아도 이름, 파라미터, 반환형 만으로 "언제" "어떻게" 사용하면 되는 함수인지 빠르게 파악할 수 있는 함수라고 생각한다.  <br>

따라서, 나는 이 기법을 싫어한다.

## 11.5 매개변수를 질의 함수로, 질의 함수를 매개변수로

1. 매개변수를 질의 함수로 바꾸기 
    매개변수 A가 값 필드 B를 가지고 있을 때, `callFunction(A, A.B);`와 같이 호출하지 않고, `callFunction(A)`와 같이 호출해서, Function이 그 안에서 A에게 B를 질의하는 방식인 것이다. <br> 어차피 B라는 값을 A에서 얻어야 한다면 좋은 방법인 것 같다. 다만 어떤 때는 B에 해당하는 값을 꼭 A에서 꺼내 쓰고 싶지 않을 수도 있을 것 같은데, 이러한 몇가지 경우에서는 좋지 않은 방법일 수도 있을 것 같다.
2. 질의 함수를 매개변수로 바꾸기
    간혹 함수 안에서 전역 "변수"를 참조하는 경우가 있다. 혹은 이 함수 안에서 어떤 값을 얻기 위해 다른 객체의 질의 함수를 통해 값을 얻어올 때가 있다. <Br> 만약 이 함수에서 이러한 참조들을 없애고 싶다면, 함수 내부에서 값을 구하는 대신 함수의 매개변수로 만들어 호출하는 쪽에서만 이 객체를 의존하게 할 수 있다.

## 11.6 생성자를 팩토리 함수로 만들기
일반적인 생성자만으로는 부족할 때 사용한다고 한다. 생성자는 몇 가지 강제 사항이 있다
1. 생성자를 정의한 클래스의 인스턴스만을 반환할 수 있다.
2. 이름이 제한된다.
3. new라는 특별한 연산자를 사용함으로써, 일반 함수처럼 사용할 수 없다

팩터리 함수에는 이런 제한이 없다.

나도 생성자에 적절한 이름을 붙여주고 싶을 때 많이 사용한다. -> [정리했던 내용](https://github.com/binary-ho/TIL-public/blob/main/Effective%20Java/Item%201.%20%EC%83%9D%EC%84%B1%EC%9E%90%20%EB%8C%80%EC%8B%A0%20%EC%A0%95%EC%A0%81%20%ED%8C%A9%ED%84%B0%EB%A6%AC%20%EB%A9%94%EC%84%9C%EB%93%9C%EB%A5%BC%20%EA%B3%A0%EB%A0%A4%ED%95%98%EB%9D%BC.md)

## 11.7 명령을 함수로, 함수를 명령으로

여기서 "명령"이란 무엇일까.
이 책에서는 어떤 객체가 스스로 가지고 있는 함수를 "함수"로, 다른 객체의 함수를 호출하는 행위를 "명령"으로 표현했다.

만약 명령이 그리 복잡하지 않다면, 함수로 바꿀 것을 권하고 있다. 이는 참조하는 객체 하나를 줄일 수 있다는 점에서 매우 좋다고 생각한다. 하지만, 응집도가 낮아짐에 매우 주의해야 할 것이다. 그래서 자주 사용할 일은 없을 것 같다.

반대로 함수를 다른 객체로 옮겨 명령으로 바꿀 수 있다.
이는 아주 많은 장점을 제공한다.
1. 책임의 분리, 응집도의 증가
2. 캡슐화 (이젠 호출하는 쪽에서 신경 쓸 부분이 확연히 준다.)
