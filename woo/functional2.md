# 일급함수 1

## 리팩터링 기법 1: 암묵적 인자 드러내기
```js
function setPriceByName(cart, name, price) {
  var item = cart[name];
  var newItem = objectSet(item, 'price', price);
  var newCart = objectSet(cart, name, newItem);
  return newCart;
}

function setQuantityByName(cart, name, quant) {
  var item = cart[name];
  var newItem = objectSet(item, 'quantity', quant);
  var newCart = objectSet(cart, name, newItem);
  return newCart;
}

function setShippingByName(cart, name, ship) {
  var item = cart[name];
  var newItem = objectSet(item, 'shipping', ship);
  var newCart = objectSet(cart, name, newItem);
  return newCart;
}
```
- 책에서는 `암묵적 인자 드러내기`라는 리팩터링 기법을 소개한다.
- 해당 기법을 적용할 수 있는 곳에서는 아래와 같은 특징이 있다.
    - 함수 구현의 거의 똑같다.
    - 함수 이름이 구현의 차이를 만든다.
- 위 3가지 메서드를 보면 Price, Quantity, Shipping이라는 메서드 내의 단어가 구현의 차이를 만든다.
- 이 단어들이 암묵적인 인자를 뜻한다.
  <br></br>

```js
function setFieldByName(cart, name, field, value) {
  var item = cart[name];
  var newItem = objectSet(item, field, value);
  var newCart = objectSet(cart, name, newItem);
  return newCart;
}
```
- 인묵적 인자를 메서드 명에서 드러내고 메서드 파라미터로 바꾸면 3개의 개별적인 메서드는 하나의 메서드로 리팩터링이 가능하다.
- 이는 메서드 명에 존재하던 필드명이라는 인자를 `일급값`으로 만든 것.
    - 일급값: 함수에 인자로 넘길 수 있고, 함수 리턴값으로 사용할 수 있고, 변수에 넣을 수 있는 값을 뜻한다.
- 단, field 값의 정확성을 위해서는 컴파일 타임 혹은 런타임에 검사하는 로직을 추가하면 좋다.
    - 컴파일 타임: 정적 타입 시스템에서 Java의 Enum과 같은 타입을 이용하면 된다.
    - 런타임: Set 구조에 가능한 field를 담아두고 매 요청마다 검사를 진행한다.

<br></br>

## 리팩터링 기법 2: 본문을 콜백으로 바꾸기
```js
function cookAndEatFoods() {
  for (var i = 0; i < foods.length; i++) {
    var food = foods[i];
    cook(food);
    eat(food);
  }
}

function cleanDishes() {
  for (var i = 0; i < dishes.length; i++) {
    var dish = dishes[i];
    wash(dish);
    dry(dish);
    putAway(dish);
  }
}
```
- 2개의 메서드는 반복문을 포함한 비슷한 로직을 수행한다.
- 우선 1차적으로 리팩터링 기법 1을 적용해 암묵적 인자를 드러내보자
  <br></br>

```js
function cookAndEatArray(array) {
  for (var i = 0; i < array.length; i++) {
    var item = array[i];
    cook(item);
    eat(item);
  }
}

function cleanArray(array) {
  for (var i = 0; i < array.length; i++) {
    var item = array[i];
    wash(item);
    dry(item);
    putAway(item);
  }
}
```
- 암묵적 인자 드러내기를 통해 Foods와 Dishes를 일급값(array)로 변경했다.
- 하지만 메서드 명에는 여전히 암묵적 인자가 존재해 보인다.
- 이번 인자는 특정 데이터가 아닌 동작을 뜻하기 때문에 해당 동작을 드러내 변수로 변경해보자
  <br></br>

```js
function forEach(array, f) {
  for (var i = 0; i < array.length; i++) {
    var item = array[i];
    f(item);
  }
}

function cookAndEat(food) {
  cook(food);
  eat(food);
}

function clean(dish) {
  wash(dish);
  dry(dish);
  putAway(dish);
}
```
- 이렇게 리팩터링이 마무리 됐다.
- 결과적으로 forEach()는 고차 함수로 정의되었다.
    - 고차 함수: 인자로 함수를 받거나 함수를 리턴하는 것
- 지금까지 진행된 본문을 콜백으로 바꾸기는 리팩터링은 아래와 같은 단계를 거친다.
    - 본문과 본문의 앞/뒤를 구분한다.
    - 전체를 함수로 빼낸다.
    - 본문을 빼낸 함수의 인자로 전달한다.
- 이번 장에서는 2가지 리팩터링 방법과 일급 값, 일급 함수, 고차 함수라는 개념을 배웠다.
- 앞으로 이 개념들을 활용하는 것의 강점에 대해 설명해줄듯


# 일급함수 2
## 콜백 빼내기 리팩터링의 장점
```js
function withArrayCopy(array, modify) {
  var copy = array.slice();
  modify(array);
  return copy;
}

// 활용
function arraySet(array, idx, value) {
  return withArrayCopy(array, function(copy) {
    copy[idx] = value;
  })
}
```
- withArrayCopy()는 배열과 콜백 메서드를 인자로 받고, 배열에 카피-온-라이트를 적용한 후 콜백 메서드를 수행하고 반환한다.
- 즉, 카피-온-라이트를 적용해주는 메서드이다. 이렇게 구현하면 카피-온-라이트가 필요한 곳에 매번 구현할 필요 없이 withArrayCopy()를 사용하면 된다.
- 또한 카피-온-라이트에 대한 코드를 한 곳에서 관리할 수 있고, 함수의 동작을 최적화하기 편리하다.
  <br></br>
## 콜백 빼내기 리팩터링의 단점
- 하지만 이러한 방식에도 2가지 문제점이 존재한다.
    1. 어떤 부분에 카피-온-라이트를 적용하는 것을 깜빡할 수 있다.
    2. 모든 코드에 수동으로 withArrayCopy()를 적용해야 한다.
       <br></br>


## 해결책: 함수 팩토리를 활용하라
```js
function wrapWithArrayCopy(f) {
  return function(array, arg1, arg2, arg3) {
    var copy = array.slice();
    f(array, arg1, arg2, arg3);
    return copy;
  }
}

var arraySetWithCopy = wrapWithArrayCopy(arraySet);
```
- 책에서는 함수를 리턴하는 함수 팩토리를 사용하는 방식을 제안한다.
- 함수 팩토리는 함수에 콜백 인자를 추가하는 대신 해당 함수를 새로운 함수로 감싼다.
- 이 경우 카피-온-라이트가 적용된 메서드인지 명확히 알 수 있다 (카피-온-라이트로 감싼 함수를 만들고, 카피-온-라이트 동작에 대한 내용을 메서드 명으로 식별한다.)
- 단, 모든 코드에 적용이 필요한 점은 변하지 않는다.
- 함수 팩토리는 적절하게 사용하면 유용하지만 코드를 복잡하게 만드는 요소이기도 하기 때문에 꼭 필요한 때인지를 고민하며 사용하자.