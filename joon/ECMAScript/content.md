# ECMA Script (ES)

### ECMA

> European Computer Manufactures Association

## ECMA Script

> ECMA라는 기관에서 JavaScript를 표준화하기 위해 만든 script 언어. ECMA-262 표준를 따른다.

옛날옛적에 **넷스케이프 커뮤니케이션즈**라는 회사에서 브라우저에서 동작하는 가벼운 프로그래밍 언어 도입을 결정하여 **브랜든 아이크**라는 개발자분이 `JavaScript`를 개발하였다고 한다. (파이어폭스 만드신 분임 ㄷㄷ) <br/>
이후 마이크로소프트는 JavaScript에서 파생된 언어인 `JScript`를 인터넷 익스플로러에 탑재하였는데, 이때 문제가 발생였다. <br/>
마이크로소프트가 자사 브라우저인 인터넷 익스플로러의 시장 점유율을 높이기 위해 이 브라우저에서만 동작하는 기능들을 추가하여 호환성 문제가 발생한 것이다. <br/>
<strike>(태생부터 뭔가 좀 구린걸 보니 구데기인 이유가 있었다.)</strike>

따라서 브라우저에 따라 어떤 웹페이지는 정상적으로 동작하는데 어디서는 삐꾸가 나는 `크로스 브라우징 이슈`가 발생한 것이다. <br/>
이로 인해, 하나의 웹페이지이지만, 여러 브라우저에서 동작시키기 위한 코드가 필요해졌고, 결과적으로 웹 개발이 어려워졌다.

이러한 크로스 브라우징 이슈를 해결하기 위해 등장한 것이 `ECMAScript`이다. <br/>
모든 개발자가 하나의 언어로 웹 개발을 하기 위한 규약인 것이다. <br/>
어렵게 말하면 **다른 호스트 환경에서 실행되는 스크립트의 표준**이라고 하는데, 단순히 말하면 현재도 JavaScript 엔진은 브라우저마다 다른데 이 모든 엔진에서 돌아갈 수 있는 하나의 언어를 표준화한 약속이 `ECMAScript`인 것이다. <br/>
따라서 ECMAScript에는 **JavaScript의 기본 언어 기능과 문법이 정의**되어있다.

## 버전별 특징

그럼 버전별로 어떤 차이가 있는지 슬쩍 알아보자.

### ES1~3

JavaScript의 가장 기본 버전이다.

> hoisting, prototype, scope 등이 추가되었다. <br/>

(Prototype에 관한 이야기도 다룰 예정이니 To be continue...)

### ES5

ES5는 HTML5와 함께 나온 표준안(?)이다.

> **배열**에 **고차함수를 지원**

forEach, map, filter, reduce, some, every와 같은 고차함수가 추가되었다.

> `Object`와 관련된 다양한 함수 지원

- `getter / setter` 지원
- `Object.defineProperty()` : 객체의 속성을 정의하는 함수로, value, writable, enumerable, configurable, get, set 등의 속성을 정의하여 읽기 쓰기 권한 등을 변경할 수 있다.

  ```jsx
  const person = {};

  // params : obj, propertyName, descriptor
  Object.defineProperty(person, "name", {
    value: "unknown",
    writable: false,
    configurable: true,
    enumerable: true,
  });

  person.name = "sungIn"; // writable이 false이므로 수정 불가
  console.log(person.name); // name
  ```

- `Object.create()` : 주어진 객체를 `Prototype`으로 하는 객체 생성
  - `parameter`로는 생성될 객체의 `Prototype`으로 지정될 객체와 옵션이 들어간다.
  - `new`를 이용하면 `constructor`가 실행이 되지만, `create`의 경우에는 객체만 생성할뿐 `constructor`는 실행되지 않는다.

> JavaScript `strict 모드` 지원

`strict rule` 적용으로 오류를 방지하고, JS 엔진 최적화를 돕는다. <br/>
이로 인해 문법과 런타임 동작을 모두 검사하여 비교적 널널했던 동작에 대해 실수를 에러로 변환하고, 변수 사용을 단순화하였다. <br/>
script나 함수의 시작 부분에 `'use strict'` 를 선언하여 켤 수 있다.

> JSON 지원

이전까지는 XML만을 지원하다 JSON이 추가되었다.

- `JSON.stringify()`
- `JSON.parse()`

> `bind` 함수 추가

`this`를 원하는 scope에서 원하는 값으로 고정이 가능해졌다. <br/>
이전까지는 `call`과 `apply`를 이용하여 `this`를 변경하였다고 한다.

### ES6

대격변의 시작을 알린 ES6라고 한다.

> 변수 선언 키워드 추가

`var` 외에 변수 선언시, `let`과 `const` 키워드가 추가되었다. <br/>
`var`와 다르게 block 범위 (함수 단위 scope) 내에서 정의할 수 있고, 재정의는 불가능하다. <br/>
`let`은 **재할당**이 가능하지만 `const`는 불가능하다.

> `arrow function` 문법 추가

편하고 간결한 코드 작성이 가능해졌다. <br/>
this Binding이 불가능하고, 선언된 scope의 this를 가리킨다. <br/>
`Prototype` 객체를 가지지 않기 때문에 `new`로 호출이 불가능하다. <br/>
이 말은 즉, `contructor`로 사용 불가능하다는 이야기이다.

> 함수 parameter의 기본값 지정 가능

```javascript
function addToCart(item, size = 1) {
  // ...
}
```

> `Class` 추가

`class` 키워드를 이용하여 클래스를 정의할 수 있게 되었다. <br/>
`constructor`를 항상 포함해야 하며,`extends`를 이용하여 쉽게 상속이 가능해졌다.

> **구조 분해 할당** 지원

> iterator / generator 추가

> module `import / export` 추가

- 이전까지는 require을 사용

> 비동기 처리 패턴인 `Promise` 도입

이전까지 사용하던 콜백은 비동기 요청이 처리된 이후에 동작할 함수를 전달받아 실행하는 형식이였다. <br/>
때문에 비동기 로직 혹은 데이터 처리 로직이 복잡해지는 경우 `콜백 헬`이 발생할 수 밖에 없다. <br/>
따라서 `Promise`를 도입하여 이를 개선하고자 하였다.

> 템플릿 리터럴 제공

**백틱(`)**을 이용하여 문자열을 감싸 표현하는 기능이 추가되었다.

> 객체 리터럴

객체의 속성에 값을 대입할 때, 변수명과 속성의 이름이 같다면 생략 가능해졌다.
또한, 새로운 메서드 표기법이 추가되었다.

```javascript
// var obj = { name: name, age: age, email: email };  // 기존 표기법
var obj = { name, age, email }; // 속성명과 변수명이 같을 경우 개선된 표기법

let p1 = {
  // ...
  order: function () {
    // 기존 메서드 표기법
    if (!this.amount) {
      this.amount = this.quantity * this.price;
    }
    console.log("주문금액 : " + this.amount);
  },
  discount(rate) {
    // 새로운 메서드 표기법
    if (rate > 0 && rate < 0.8) {
      this.amount = (1 - rate) * this.price * this.quantity;
    }
    console.log(100 * rate + "% 할인된 금액으로 구매합니다.");
  },
  // ...
};
```

> `super` 호출이 가능해짐

> Prototype 직접 설정 가능

`__proto__`에 직접 접근하여 가능하다.

### ES7

> 제곱 연산자 `**` 제공

> Array.includes 제공

배열에 해당 요소가 존재하는지 확인하는 고차함수가 추가되었다.

### ES8

> `async / await` 추가

새로운 비동기 처리 패턴인 `async / await`가 추가되었다. <br/>
Promise도 then으로 처리하는 로직이 길어진다면 에러 확인이 어렵고 콜백과 마찬가지로 가독성이 떨어진다. <br/>
`async / await`는 코드를 마치 동기적인 것처럼 읽을 수 있게 되어 가독성이 향상되었고, 에러 또한 같은 이유로 찾기가 쉬워졌다.
