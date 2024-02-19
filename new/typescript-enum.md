## Enum

> TL;DR
> - 타입스크립트 enum은 트리쉐이킹 안된다
> - const enum을 사용하면 트리쉐이킹이 되지만 실행되지 않는 환경이 있음
> - 유니온 타입을 사용하자

- 타입스크립트의 enum은 열거형

``` ts
enum Direction {
  UP,
  DONW,
  LEFT,
  RIGHT
}

Direction.UP // 0
Direction.DOWN // 1
Direction.LEFT // 2
Direction.RIGHT // 3
```
- enum은 자동으로 0, 1, 2 등 숫자를 부여해서
- 문자열 enum을 만들기 위해서는 문자열을 일일이 작성해줘야함 

``` ts
enum Direction {
  UP = 'UP',
  DONW = 'DOWN',
  LEFT = 'LEFT',
  RIGHT = 'RIGHT',
}
```

## Enum의 문제점
> 요약
> - 트리쉐이킹이 안됨
> - 개발자의 의도와 다르게 동작하는 경우가 많음
> - 타입 안정성 떨어짐

- 자바스크립트에서는 enum의 개념이 없기 때문에
- 위 코드를 자바스크립트로 변환하게 되면 `즉시실행함수(IIFE)`로 변환

``` js
'use strict'
var Direction
;(function (Direction) {
  Direction['UP'] = 'UP'
  Direction['DONW'] = 'DOWN'
  Direction['LEFT'] = 'LEFT'
  Direction['RIGHT'] = 'RIGHT'
})(Direction || (Direction = {}))
```

- IIFE는 **트리쉐이킹이 안됨**
    > 트리쉐이킹: 사용하지 않는 코드를 삭제하는 기능
  - [rollup 번들러 예제 코드](https://rollupjs.org/repl/?version=2.26.11&shareable=JTdCJTIybW9kdWxlcyUyMiUzQSU1QiU3QiUyMm5hbWUlMjIlM0ElMjJtYWluLmpzJTIyJTJDJTIyY29kZSUyMiUzQSUyMmltcG9ydCUyMCU3QkRpcmVjdGlvbiU3RCUyMGZyb20lMjAnLiUyRmVudW0uanMnJTVDbmltcG9ydCUyMCU3QmhlbGxvJTdEJTIwZnJvbSUyMCcuJTJGdHJlZXNoYWtlZCclNUNuaW1wb3J0JTIwJTdCaGklN0QlMjBmcm9tJTIwJy4lMkZub3RUcmVlc2hha2VkJyU1Q24lNUNuY29uc29sZS5sb2coaGVsbG8pJTVDbiUyMiUyQyUyMmlzRW50cnklMjIlM0F0cnVlJTdEJTJDJTdCJTIybmFtZSUyMiUzQSUyMmVudW0uanMlMjIlMkMlMjJjb2RlJTIyJTNBJTIyJ3VzZSUyMHN0cmljdCclNUNuZXhwb3J0JTIwdmFyJTIwRGlyZWN0aW9uJTVDbiUzQihmdW5jdGlvbiUyMChEaXJlY3Rpb24pJTIwJTdCJTVDbiUyMCUyMERpcmVjdGlvbiU1QidVcCclNUQlMjAlM0QlMjAnVVAnJTVDbiUyMCUyMERpcmVjdGlvbiU1QidEb3duJyU1RCUyMCUzRCUyMCdET1dOJyU1Q24lMjAlMjBEaXJlY3Rpb24lNUInTGVmdCclNUQlMjAlM0QlMjAnTEVGVCclNUNuJTIwJTIwRGlyZWN0aW9uJTVCJ1JpZ2h0JyU1RCUyMCUzRCUyMCdSSUdIVCclNUNuJTdEKShEaXJlY3Rpb24lMjAlN0MlN0MlMjAoRGlyZWN0aW9uJTIwJTNEJTIwJTdCJTdEKSklMjIlN0QlMkMlN0IlMjJuYW1lJTIyJTNBJTIydHJlZXNoYWtlZC5qcyUyMiUyQyUyMmNvZGUlMjIlM0ElMjJleHBvcnQlMjB2YXIlMjBoZWxsbyUyMCUzRCUyMCdoZWxsbyclMjIlN0QlMkMlN0IlMjJuYW1lJTIyJTNBJTIybm90VHJlZXNoYWtlZC5qcyUyMiUyQyUyMmNvZGUlMjIlM0ElMjJleHBvcnQlMjB2YXIlMjBoaSUyMCUzRCUyMCdoaSclMjIlN0QlNUQlMkMlMjJvcHRpb25zJTIyJTNBJTdCJTIyZm9ybWF0JTIyJTNBJTIyZXMlMjIlMkMlMjJuYW1lJTIyJTNBJTIybXlCdW5kbGUlMjIlMkMlMjJhbWQlMjIlM0ElN0IlMjJpZCUyMiUzQSUyMiUyMiU3RCUyQyUyMmdsb2JhbHMlMjIlM0ElN0IlN0QlN0QlMkMlMjJleGFtcGxlJTIyJTNBbnVsbCU3RA==)
  - [TypeScript enum을 사용하지 않는 게 좋은 이유를 Tree-shaking 관점에서 소개합니다.](https://engineering.linecorp.com/ko/blog/typescript-enum-tree-shaking)

- 사실 enum은 문제가 더 많음
  - [숫자형 enum에서 타입이 의도되로 안되는 동작](https://github.com/microsoft/TypeScript/issues/38294#event-3305063822)
  - 값이 올바르더라도 문자형 enum이 필요한 함수나 객체에 값을 전달할 수 없음
  - enum간의 값 비교 안됨: 같은 값이여도 enum 내에 있으면 값이 비교 안됨
  - 기타 등등.. (코드 길어져서 짜증남)
  
## const enum
- enum보다 간결하고 트리쉐이킹도 되는 `const enum`이 있다

``` ts
const enum Direction {
  UP = 'UP',
  DOWN = 'DOWN',
  LEFT = 'LEFT',
  RIGHT = 'RIGHT',
}

const left = Direction.LEFT
```

위 코드는 
``` js
'use strict'
const left = 'LEFT' /* Left */
```
이렇게 변환된다. 하지만 문제가 있다

### 문제 1: Isloated modules
- `const enum`을 사용하는 코드가 각각 다른 모듈에 있다면 해당 코드가 존재하는 모듈도 실행해야한다
- `--isolatedModule` 옵션이 켜져있으면 위 작업을 할 수 없다

### 문제 2: babel에서 const enum
- babel에서 `const enum`을 사용하기 위해서는 추가로 플러그인을 설치해야한다

## 결론: 유니온 타입
``` ts
type Direction = 'UP' | 'DOWN' | 'LEFT' | 'RIGHT'
```

- 깔끔하게 유니온 타입 쓰면 된다

만약 enum을 쓰고 싶어 미치겠으면 `const`, `as const`, `Values<T>`의 헬퍼 타입을 쓸 수 있음


``` ts
const Direction {
  UP = 'UP',
  DOWN = 'DOWN',
  LEFT = 'LEFT',
  RIGHT = 'RIGHT',
} as const
```
