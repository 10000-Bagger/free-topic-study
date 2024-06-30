## Object.keys()로 알아보는 구조적 서브 타이핑

### TL;DR
- 타입스크립트는 구조적 서브 타이핑을 채택하고 있다.
- `Object.keys()`는 `string[]` 타입으로 추론된다.

### Object.keys()

- Object.keys 메서드를 사용하면 항상 key 값이 `string`으로 추론된다.

``` ts
interface MyObject {
  first: number;
  second: string;
  third: boolean;
}

Object.keys(object).forEach((key) => {
  // Element implicitly has an 'any' type because expression of type 'string' can't be used to index type 'MyObject'.
  // No index signature with a parameter of type 'string' was found on type 'MyObject'.(7053)
  const curValue = object[key];
});
```

- 이를 해결하기 위해 타입 단언 (Type Assertion)을 하게 된다.

``` ts
const keyList = Object.keys(obj) as Array<keyof typeof obj>;
```

> `string` 으로 타입 추론 되었기 때문에 타입 단언이 필요하다.

``` ts
// TypeScript/src/lib/es2015.core.d.ts

interface ObjectConstructor {
  keys(o: {}): string[];
}
```

- `Object.keys<T>()` 제네릭 타입을 제공하지 않기 때문에 제네릭 타입 추론이 어렵다.

---

### 구조적 서브 타이핑
- 타입스크립트가 구조적 서브 타이핑을 기반으로 한다.

- 자바스크립트는 덕 타이핑을 기반으로 하는 동적 타이핑 언어이다.
- 따라서, 타입스크립트는 자바스크립트의 특성인 "유연한 동적 타입"을 해치지 않으면서 타입을 강제해야한다.

``` ts
type Book = {
  name: string;
}
```

- 객체 타입 `Book`을 선언하게 되면 일반적인 명목적 타입 시스템에서는 반드시 `Book { name: string }` 형태의 타입만 와야한다.

``` ts
const getName = (book: Book) => {
  return book.name;
};
 
const book1 = { name: '123' };
const book2 = { name: '123', model: 'wow' };
const book3 = { name: '123', model: 'wow', wow: 'line' };
 
getName(book1); // ✅
getName(book2); // ✅
getName(book3); // ✅
```

- 하지만 타입스크립트에서는 모든 형태의 객체가 가능하다.

- 이것이 바로 구조적 서브 타이핑이다.

- 구조적 타입 시스템의 주요 특성은 **값을 할당할 때 정의된 타입에 필요한 속성을 갖고 있다면 호환된다**이다.
- 구조적 타입 시스템에서 타입은 값의 집합이다.

``` js
class MyObject {
  // object 타입은 원시 타입을 제외한 모든 값이 될 수 있다.
  keys<T extends object>(o: T): (keyof T)[];
}
const keys = MyObject.keys<Book>(book1); // "name"[]
const keys = MyObject.keys<Book>(book2); // "name"[]
const keys = MyObject.keys(book3); // ("name" | "model" | "wow")[]
```

- 자바스크립트의 덕 타입으로 인해 객체는 런타임에서 더 많은 속성을 가질 수 있다.

- 구조적 서브 타이핑은 필요한 속성을 갖고 있다면 확장된 집합과 호환되며 에러를 노출하지 않는다.

- 그렇기 때문에 타입스크립트는 객체 인자에 `T` 타입의 값만 존재한다는 보장을 할 수 없다.

``` ts
for (const key of Object.keys(book1)) {
  // No index signature with a parameter of type 'string' was found on type 'Book'.(7053)
  const value = book1[key];
}
```

- 따라서 타입스크립트는 런타임에서 안정성을 찾기 위해 좁은 타입의 `(keyof T)[]`가 아닌 넓은 타입인 `string[]`으로 추론된다.
  - 관련 이슈 https://github.com/microsoft/TypeScript/pull/12253#issuecomment-263132208

### 더 나은 타입 추론
- `Object.keys`는 타입 단언이 아닌 다른 방법으로도 타입을 추론할 수 있다.

#### 타입 가드를 통한 타입 좁히기

``` ts
const book: Book = { name: 'foo' };
const book2: Book = { name: 'foo', key: 'bar' };
 
// 타입 좁히기
const isBook = (key: string): key is keyof Book => {
  return Object.keys(book).includes(key);
};
 
for (const key of Object.keys(book2)) {
  // 타입 가드로 타입이 존재하는 컨디션 블록이 생기게 됨
  if (isBook(key)) {
    // Book 타입의 키
  } else {
    // 구조적 서브 타이핑으로 확장된 키
  }
}
```

- 타입 가드를 통해 타입 좁히기를 하면 타입 단언을 하지 않아도 적절히 타입을 추론할 수 있다.

---


### 유니온 타입과 교차 타입에 대한 타입 추론

``` ts
type Book = { name: string };
type Car = { model: string };
 
const BookOrCar = {} as Book | Car;

BookOrCar.name;
// Property 'model' does not exist on type 'BookOrCar'.
// Property 'model' does not exist on type 'Book'.(2339)
BookOrCar.model;
// Property 'model' does not exist on type 'BookOrCar'.
// Property 'model' does not exist on type 'Book'.(2339)

type A = 'A';
type B = 'B';
 
type AorB = A | B; // 'A' | 'B'
```

- `Book | Car` 은 `{ name: string }` 또는 `{ model: string }` 타입이 되기 때문에 두 값이 공존한다고 생각할 수 있다.
- 하지만 타입 스크립트에서는 두 값 모두 추론하지 못한다.

``` ts
const BookAndCar = {} as Book & Car;
BookAndCar.name; // string
BookAndCar.model; // string

type AandB = A & B; // never
```

- `Book & Car`은 모든 값을 가지지만, `AandB`에서는 `never` 타입이 추론된다.

각 타입을 값의 집합으로 나열해본다.

``` ts

// Book 타입에 충족하는 타입: name이 존재하는 객체

{ name: "foo" };
{ name: "foo", model: "bar" };
{ name: "foo", model: "bar", last: 'za' };
```

``` ts

// Car 타입에 충족하는 타입: model이 존재하는 객체

{ name: "foo" };
{ name: "foo", model: "bar" };
{ name: "foo", model: "bar", last: 'za' };
```

``` ts

// Book | Car 타입에 충족하는 타입

{ name: "foo" };
{ name: "foo", model: "bar" };
{ name: "foo", model: "bar", last: 'za' };
// name이 존재하는 객체

{ name: "foo" };
{ name: "foo", model: "bar" };
{ name: "foo", model: "bar", last: 'za' };
// model이 존재하는 객체
```

- `Book | Car`의 경우, **항상 존재하는 값**이 없다
  - `name` 혹은 `model`이 반드시 있어야하는 경우가 없음

``` ts

// Book & Car 타입에 충족하는 타입

{ name: "foo" };
{ name: "foo", model: "bar" };
{ name: "foo", model: "bar", last: 'za' };
```

- **항상 존재하는 값**이 있다.

- 따라서, 항상 존재하는 값의 유무에 따라 두 값이 모두 존재하는지, 아닌지가 결정된다.
