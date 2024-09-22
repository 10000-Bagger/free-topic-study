# Learning Javascript Design Patterns

## 4. 안티 패턴

### 4.1 안티 패턴이란?
> 안티 패턴은 겉으로만 해결책처럼 생긴 패턴을 뜻합니다.

- 디자인 패턴이 모범 사례라면, 안티패턴은 잘못된 패턴

- 나쁜 디자인 패턴이 안티 패턴이라는 것을 빠르게 인지할 수 있다면 패턴을 잘못 도입하는 실수를 줄일 수 있다.
- 소위 "완벽한" 설계도 잘못된 상황에서 사용된다면 안티패턴이 될 수 있다.
- 안티패턴은 반면교사로 활욯하기 위해 문서화하여 기록해야하는 나쁜 디자인 패턴

---

### 4.2 자바스크립트 안티 패턴
- 신속한 구현을 위해 임시방편을 선택하기도 하는데, 이러한 선택은 결국 기술 부채가 되어 안티패턴이 됨
- 자바스크립트는 느슨한 타입 언어이기 때문에 이러한 경향이 더 두드러짐

#### 자바스크립트를 사용하며 마주했을 수도 있는 안티 패턴의 예시
1. 전역 컨텍스트에서 수많은 변수를 정의하여 전역 네임스페이스를 오염시키기

> - **이름 충돌**: 동일한 이름의 변수를 다른 곳에서 정의할 경우 충돌이 발생할 수 있음
> - **예측 불가능한 동작**: 전역 변수의 값이 예상치 못하게 변경될 수 있음
> - **테스트 어려움**: 전역 변수를 사용하는 함수는 독립적으로 테스트하기 어려움

``` js
/* 안티 패턴: 전역 변수 */

const userName = "John Doe";
const userAge = 30;
const userEmail = "john.doe@example.com";
const userAddress = "123 Main St, Anytown, USA";

function displayUserInfo() {
    console.log("Name: " + userName);
    console.log("Age: " + userAge);
    console.log("Email: " + userEmail);
    console.log("Address: " + userAddress);
}

displayUserInfo();
```

위 코드를 다음과 같이 바꿀 수 있다.

- 모듈 패턴을 사용하면 객체를 통해 변수와 함수를 캡슐화

- ES6의 모듈 시스템을 사용하면 자연스럽게 전역 네임스페이스 오염을 피하기

``` js
/* 해결 방식 */
/* 1. 모듈 패턴 사용 */

const UserModule = (() => {
    const userName = "John Doe";
    const userAge = 30;
    const userEmail = "john.doe@example.com";
    const userAddress = "123 Main St, Anytown, USA";

    function displayUserInfo() {
        console.log("Name: " + userName);
        console.log("Age: " + userAge);
        console.log("Email: " + userEmail);
        console.log("Address: " + userAddress);
    }

    return {
        displayUserInfo: displayUserInfo
    };
})();

UserModule.displayUserInfo();


/* 2. ES6 모듈 사용 */

// user.js
export const userName = "John Doe";
export const userAge = 30;
export const userEmail = "john.doe@example.com";
export const userAddress = "123 Main St, Anytown, USA";

export function displayUserInfo() {
    console.log("Name: " + userName);
    console.log("Age: " + userAge);
    console.log("Email: " + userEmail);
    console.log("Address: " + userAddress);
}

// main.js
import { userName, userAge, userEmail, userAddress, displayUserInfo } from './user.js';

displayUserInfo();
```


2. setTimeout이나 setInterval에 함수가 아닌 문자열을 전달해서 내부적으로 `eval()` 실행되게 하기

> - 보안 문제: 문자열을 평가하는 것은 코드 인젝션 공격에 취약
> - 디버깅 어려움: 문자열로 전달된 코드는 디버깅이 어렵고, 구문 오류를 미리 감지할 수 없음
> - 성능 문제: `eval()`은 다른 JavaScript 코드보다 느림

``` js
/* 안티 패턴 */

setTimeout("console.log('This is a bad practice!')", 1000);
setInterval("console.log('This is also a bad practice!')", 1000);
```

다음과 같은 방법으로 위 코드를 해결할 수 있다.
- 익명 함수를 사용하여 setTimeout과 setInterval에 직접 함수 참조를 전달

``` js
/* 해결 방법 */
/* 함수 참조 전달 */

setTimeout(() => {
    console.log('This is a better practice!');
}, 1000);

setInterval(() => {
    console.log('This is also a better practice!');
}, 1000);
```

3. Object 클래스의 프로토타입을 수정하기

> - 호환성 문제: 다른 라이브러리나 코드가 동일한 프로퍼티 이름을 사용한다면, 충돌이 발생할 수 있습니다.
> - 예측 불가능한 동작: 객체의 원래 구조를 예상하기 어렵게 만들어 디버깅이 어려워집니다.
> - 성능 문제: 모든 객체에 추가된 프로퍼티가 영향을 미쳐 성능 저하를 일으킬 수 있습니다.

``` js
/* 안티 패턴 */

Object.prototype.sayHello = function() {
    console.log('Hello, world!');
};

const obj = {};
obj.sayHello(); // "Hello, world!" 출력

const anotherObj = { name: 'Alice' };
anotherObj.sayHello(); // "Hello, world!" 출력
```

다음과 같은 방식으로 해결할 수 있다.

1.  프로토타입을 수정하는 것이 아니라 유틸 함수로 사용하기
2.  클래스 상속 이용하기
   - 특정 객체 타입에만 메서드를 추가
3.  믹스인 패턴 적용하기
   - 필요한 메서드를 객체에 직접 추가하는 믹스인 패턴을 사용

``` js
/* 해결 방식 */

/* 1. 유틸 함수 사용 */

function sayHello(obj) {
    console.log('Hello, ' + (obj.name || 'world') + '!');
}

const obj = {};
sayHello(obj); // "Hello, world!" 출력

const anotherObj = { name: 'Alice' };
sayHello(anotherObj); // "Hello, Alice!" 출력


/* 2. 클래스 상속 이용 */

class Person {
    constructor(name) {
        this.name = name;
    }

    sayHello() {
        console.log('Hello, ' + this.name + '!');
    }
}

const person = new Person('Alice');
person.sayHello(); // "Hello, Alice!" 출력


/* 3. 믹스인 패턴 사용 */

const sayHelloMixin = {
    sayHello() {
        console.log('Hello, ' + this.name + '!');
    }
};

const obj = { name: 'Alice' };
Object.assign(obj, sayHelloMixin);
obj.sayHello(); // "Hello, Alice!" 출력
```

4. 자바스크립트를 인라인으로 사용하여 유연성 떨어뜨리기

> - 유지보수성 저하: HTML과 JavaScript가 섞여 있어 코드를 읽고 이해하기 어려움
> - 재사용성 부족: 동일한 동작을 다른 요소에 적용하려면 매번 인라인으로 코드를 작성해야함
> - 보안 문제: 인라인 스크립트는 크로스 사이트 스크립팅(XSS) 공격에 취약
> - 테스트 어려움: 인라인 코드의 테스트와 디버깅이 어려움

``` html
/* 안티 패턴 */

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Document</title>
</head>
<body>
    <button onclick="alert('Hello, world!')">Click me</button>
</body>
</html>
```

- 이 방식은 HTML에서 js를 분리하는 방식으로 해결할 수 있다.
- 외부 스크립트 파일을 사용하는 방식을 통해 HTML과 JavaScript 간의 결합을 줄인다.
