# Typescript: enum, const enum, as const

## enum

- enum: Enumerated Type
- typescript는 숫자기반 뿐만아니라 문자열 기반의 열거형까지도 지원.

typescript 구현

```tsx
enum booleanType {
  False = 0,
  True = 1,
}
```

내부 구현

```tsx
"use static";
var booleanType;
(function (booleanType) {
  booleanType[booleanType["False"] = 0] = "False";
  booleanType[booleanType["True"] = 1] = "True";
})(booleanType || (booleanType = {}));
```

** 설명: 위 코드는 아래의 객체를 반환하는 즉시 실행 함수

```tsx
var booleanType = {
  "0": "False",
  "1": "True",
  "False": 0,
  "True": 1,
}
```

따라서, enum은 JS로 컴파일되는 과정에서 Key-Value의 관계가 양방향으로 구현됨.

```tsx
booleanType['False'] // 0
booleanType['True'] // 1
booleanType[0] // "False"
booleanType[1] // "True"
```

### enum의 자동 할당 기능

- 첫번째 Member(key-value)의 경우, 초기화되지 않는다면 자동으로 key의 value 값으로 0이 할당된다.
- 어떤 Member가 초기화 되지 않았지만, 바로 이전 member가 숫자 상수였다면, 해당 member는 ‘이전 member의 값 + 1’을 값으로 갖는다.

```tsx
enum DirectionNotInit {
  Up, // 0
  Down, // 1
  Left, // 2
  Right, // 3
}

enum DirectionFirstMemberInit {
  Up = 1,
  Down, // 2
  Left, // 3
  Right, // 4
}
```

### enum의 장점

- 생산성과 가독성 향상 (작성자의 의도 파악, key-value 양방향 관계 구현 등)
- 의도하지 않는 에러 방지 (정의한 key-value 관계만 성립할 수 있기 때문에, value의 값을 변경하지 못함 = readonly)

### enum의 단점

- 컴파일 시 코드의 양 증가 (key-value의 양방향 정의가 필요하지 않으면 불필요한 코드가 추가되는 것)
- Tree-shaking 불가 (사용하지 않는 코드를 제거하여 코드를 가볍게 만드는 최적화 과정)

## const enum

> In most cases, enums are a perfectly valid solution. However sometimes requirements are tighter. To avoid paying the cost of extra generated code and additional indirection when accessing enum values, it’s possible to use const enums. Const enums are defined using the const modifier on our enums.
> 

enum의 단점을 개선하고자 존재하는 개념.

예제:

```tsx
const enum Enum {
  A = 1,
  B = A * 2,
}
 
// .JS
"use strict";
 
 
enum Enum {
  A = 1,
  B = A * 2,
}
 
// .JS
"use strict";
var Enum;
(function (Enum) {
    Enum[Enum["A"] = 1] = "A";
    Enum[Enum["B"] = 2] = "B";
})(Enum || (Enum = {}));
```

동일한 코드를 작성했음에도 const modifier가 붙은 enum은 JS로 컴파일 후 어떤 코드도 남지 않는다.

하지만 Typescript 공식 문서에서도 [const enum 사용에 위험성](https://www.typescriptlang.org/docs/handbook/enums.html#const-enum-pitfalls)이 있다고 설명하고 있고 아래의 단점을 가지고 있어 사용에 주의해야 함.

> const enums can only use constant enum expressions and unlike regular enums they are completely removed during compilation. Const enum members are inlined at use sites. This is possible since const enums cannot have computed members.
> 
- const enum은 computed member를 갖지 못한다. = value는 string이나 숫자형 같은 정적인 값만 가능(컴파일 시 코드가 사라져 버리기 때문에)
- const enum member는 linlined 되어 해당 코드가 호출되는 곳에 곧장 inline 대상 코드를 치환하여 컴파일된다.

### Typescript의 const enum과 inline

```tsx
const enum Direction {
  Up,
  Down,
  Left,
  Right,
}
 
let directions = [
  Direction.Up,
  Direction.Down,
  Direction.Left,
  Direction.Right,
];
 
 
// .JS
"use strict";
let directions = [
    0 /* Direction.Up */,
    1 /* Direction.Down */,
    2 /* Direction.Left */,
    3 /* Direction.Right */,
];
```

** 설명: Direction 이라는 enum이 inlined 되어 처리된 결과.

### const enum의 특징

- enum과 다르게 key-value의 관계가 양방향이 되지 않는다.
- inlined 되기 때문에, 코드가 가벼워지고, tree-shaking도 가능하다.

굳이 key-value 간의 양방향 mapping이 필요 없는 상황에서, object의 key로 접근하여 value만들 가져와서 그 값을 type으로 정해주고 싶을 때 주로 사용됨. (단순히 value 값을 받아오는 게 아니라, 그 value 값을 type으로 정해주기 위해서 const enum과 같은 문법이 필요한 것)

## as const

const enum 사용 위험성으로 인해 as const를 사용하는 방식이 Typescript 3.4 버전에 추가됨.

const assertion = “원래 상수가 아닌 것을 상수인 것으로 선언해주는 기능”

- let으로 선언된 변수는 string 타입으로 추론된다.

<img width="302" alt="Screenshot 2024-06-16 at 3 56 09 AM" src="https://github.com/10000-Bagger/free-topic-study/assets/34956359/8ffd11c5-1424-4aca-9927-800ff4fd66bf">

- const로 선언된 변수는 “NLP”로 추론된다.

<img width="298" alt="Screenshot 2024-06-16 at 3 56 27 AM" src="https://github.com/10000-Bagger/free-topic-study/assets/34956359/82ed74b8-8269-4da8-adaf-81f0b30d59b0">


따라서 const로 선언된 변수에 다른 값을 재할당하게 되면 Type 에러가 발생하는 것. 

### as const의 특징

Object의 value는 상수가 아니다:

- Obkect는 구조화된 데이터 형태로서 가변적인 데이터 값을 저장하기 위해 탄생했기 때문에, 특정 Object에 특정 Key가 존재해야 한다고 지정해줄 수는 있지만 특정 key에 와야하는 value를 구체적으로 지정할 수는 없다.

하지만 Object를 Object 본래 용도가 아닌 enum으로 활용하고 싶을 때, as const 문법을 사용한다.

```tsx
const Direction = {
  Up: 'Up',
  Down: 'Down',
  Left: 'Left',
  Right: 'Right',
} as const;
```

## References

- [우리 팀의 우아한 타입스크립트 컨벤션 정하기 여정](https://techblog.woowahan.com/9804/)
- [Handbook - Enums](https://www.typescriptlang.org/docs/handbook/enums.html#const-enum-pitfalls)
- [Typescript의 enum, const enum, as const에 대해 알아보자](https://xpectation.tistory.com/218)
- [내가 타입스크립트에서 Enum을 잘 쓰지 않는 이유](https://yceffort.kr/2022/03/typescript-use-union-types-instead-enum)
