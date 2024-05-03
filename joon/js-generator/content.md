`async/await` 동작 원리에 대해 알아보는 도중에 `async/await` 가 내부적으로 **즉시 실행 함수**와 `generator`, `Promise`가 합쳐진 것이라는 것을 보아 알아보고자 한다.

# Generator

일반적으로 함수는 하나의 값만을 반환하지만 제너레이터는 필요에 따라 여러 값을 반환할 수 있다. 그리고 중간에 원하는 부분에서 멈추었다가, 다시 그 부분부터 실행할 수 있는 능력을 가진 함수이다.

제너레이터는 `function*` 라는 문법을 통해 생성하고 `yield` 라는 문법을 통해 여러 개의 값을 반환할 수 있다.<br/>
먼저, 정의하는 방법은 다음과 같다.

```jsx
function* generatorTest() {
  yield 1;
  yield 2;
  return 3;
}
```

Generator는 일반 함수와 다르게 호출시 코드가 실행되는 것이 아니라 제너레이터 객체가 반환된다.<br/>
그리고 `next()` 메서드를 통해 값을 얻을 수 있는데, `next()` 가 호출되면 가장 가까운 `yield`를 만날 때까지 제너레이터가 진행된다.<br/>
`next()` 메서드는 `value`와 `done`으로 구성된 객체를 반환하는데, `value`는 `yield`를 통해 **산출된 값**이고, `done`은 제너레이터 코드의 실행이 끝났다면 **true**, 끝나지 않았다면 **false**를 반환한다.<br/>
이렇게 `next()`를 통해 제너레이터 함수의 값을 얻게 되므로, 함수의 제어권은 함수 호출자에게 양도된다.

제너레이터는 **이터러블**이기 때문에 `for…of`를 통해 값을 얻을 수 있다.

```jsx
function* generatorTest() {
  yield 1;
  yield 2;
  return 3;
}

let generator = generatorTest();

for (let value of generator) {
  alert(value); // 1, 2가 출력됨
}
```

3이 출력되지 않는 이유는 **done이 true일 때의 값을 무시하기 때문**이다.<br/>
따라서 모든 값을 `for…of`로 얻기 위해선 모두 `yield`를 통해 값을 반환해야 한다.<br/>
`for…of`도 가능하기 때문에 `스프레드 연산자(…)`도 사용이 가능하다.

```jsx
function* generatorTest() {
  yield 1;
  yield 2;
  yield 3;
}

let sequence = [0, ...generateSequence()];

alert(sequence); // 0, 1, 2, 3
```

## 제너레이터 컴포지션(Generator Composition)

제너레이터 안에 제너레이터를 `임베딩(embedding, composing)`할 수 있게 해주는 제너레이터의 특별 기능이다.<br/>
제너레이터의 특수 문법 `yield*`를 사용하면 제너레이터를 다른 제너레이터에 **끼워 넣을 수 있다.**

```jsx
function* generateSequence(start, end) {
  for (let i = start; i <= end; i++) yield i;
}

function* generatePasswordCodes() {
  // 0..9
  yield* generateSequence(48, 57);
  // for (let i = 48; i <= 57; i++) yield i; // 이렇게 표현해도 결과는 같음

  // A..Z
  yield* generateSequence(65, 90);

  // a..z
  yield* generateSequence(97, 122);
}

let str = "";

for (let code of generatePasswordCodes()) {
  str += String.fromCharCode(code);
}

alert(str); // 0..9A..Za..z
```

`yield`는 제너레이터 밖으로 산출된 값을 내보낼 뿐만 아니라 안으로 전달할 수도 있다.

```jsx
function* gen() {
  // 질문을 제너레이터 밖 코드에 던지고 답을 기다립니다.
  let result = yield "2 + 2 = ?"; // (*)

  alert(result);
}

let generator = gen();

let question = generator.next().value; // <-- yield는 value를 반환합니다.

generator.next(4); // --> 결과를 제너레이터 안으로 전달합니다.
```

제너레이터 함수가 호출되어 제너레이터 객체가 생성되고 난 후, `next()`를 통해 `“2 + 2 = ?”`라는 결과를 반환 받고 제너레이터는 `(*)`라고 표기된 줄에서 실행을 잠시 멈춘다.<br/>
그리고 그 다음 라인에서 `next(4)`를 통해 제너레이터 안으로 `4`라는 값을 전달하고, 제너레이터는 이를 받아 result에 저장한 후 alert문을 통해 출력한다.

## generator.throw

값 뿐만이 아니라 에러를 제너레이터 안으로 전달할 수도 있다.<br/>
`yield` 안으로 에러를 전달하기 위해서는 `generator.throw(err)` 함수를 호출해야 한다.

```jsx
function* gen() {
  try {
    let result = yield "2 + 2 = ?"; // (1)

    alert(
      "위에서 에러가 던져졌기 때문에 실행 흐름은 여기까지 다다르지 못합니다."
    );
  } catch (e) {
    alert(e); // 에러 출력
  }
}

let generator = gen();

let question = generator.next().value;

generator.throw(new Error("데이터베이스에서 답을 찾지 못했습니다.")); // (2)
```

`next()` 이후 `(2)`으로 표기된 `generator.throw`를 통해 `(1)`의 `yield`에 에러를 던진다.<br/>
만약 제너레이터 내부로 던져진 에러를 제너레이터 내부에서 잡지 못한다면 에러는 외부로 나가게 된다.
