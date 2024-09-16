# Call by **Sharing**

문득 갑자기 JavaScript는 `Call by Value`일까, `Call by Reference`일까라는 생각이 들었다.<br/>
C와 C++은 기본적으로 `Call by Value`를 따르지만, 메모리 값을 직접 접근할 수 있는 `Pointer`를 통해 `Call by Reference`를 사용할 수 있다.<br/>
Java는 객체지향 언어이고, 메모리에 직접 접근할 수 없지만, 참조를 통해 객체에 접근하기 때문에 당연히 `Call by Reference`라고 생각해왔다.<br/>
그렇다면 JavaScript는 어떤 방식을 따를까?<br/>

먼저, Call by Value와 Call by Reference에 대해 가볍게 짚고 가보자.

### Call by **Value**

대부분의 언어들은 `Call by Value`로 동작한다.<br/>
`Call by Value`는 함수에 인자를 전달할 때, 값 자체를 복사하여 새로운 변수로 전달하는 방식이다.<br/>
따라서 함수의 파라미터로 전달된 인자를 함수 안에서 조작한다고 하더라도 그 원본은 변하지 않는다.

```jsx
function square(x) {
  x = x * x;
  return x;
}

var n = 2;
console.log(n); // 2
square(n);
console.log(n); // 2
```

이러한 `Call by Value`를 사용하는 이유는 무엇일까?<br/>
변수에 저장된 데이터를 복사하여 전달하기 때문에 장점과 단점이 있을 것이다.
장점은 **원본 데이터를 보호**할 수 있어 안전하다는 것이다.
하지만, 단점은 새로운 변수에 데이터를 복사하여 전달하기 때문에 **메모리 사용량이 늘어나게 된다**.

### Call by **Reference**

`Call by Reference`는 Call by Value와 다르게, 실제 값이 존재하는 메모리 주소값을 전달한다.<br/>
따라서 함수 안에서 해당 변수를 조작할 경우, 데이터가 변경된다.

```cpp
#include <iostream>

using namespace std;

void Swap(int *a, int *b)
{
	int tmp = *a;
	*a = *b;
	*b = tmp;
}

int main()
{
	int a = 10;
	int b = 20;

	Swap(&a, &b);

	cout << "a : " << a << endl; // 20
	cout << "b : " << b << endl; // 10
}
```

장점은 메모리 복사가 이루어지지 않기 때문에 `Call by Value`에 비해 **빠르다.**<br/>
단점은 주소값 자체를 직접 참조하기 때문에 값이 수정될 경우, **디버깅이 어렵고 사이드 이펙트가 발생할 수 있어 안정성이 낮다.**

### Call by Sharing

Java는 `Call by Reference`를 따르는 줄로만 알았지만, 사실 `Call by Reference` 의 개념은 존재하지 않는다고 한다.<br/>
그 이유는 함수에 인자를 전달할 때, 실제 데이터를 참조하고 있는 주소값 자체를 복사하여 전달하기 때문이라고 한다.<br/>
(사실 말장난 같다.. 주소값을 한번 복사해서 주냐, 아니면 바로 전달하냐의 차이 정도..?)

이러한 개념을 `Call by Sharing`이라고 부른다고 한다.<br/>
JavaScript 또한 이를 따른다고 하는데, 예시를 통해 알아보자.

```jsx
function manipulatePropA(obj, data) {
  obj.a = data;
}

const test = { a: 1 };
manipulatePropA(test, 125);
console.log(test.a); // ?
```

위의 예시에서 마지막 출력문의 답은 뭘까?

만약 JavaScript가 `Call by Value`를 따른다면, `1`이 출력될 것이고, `Call by Reference`를 따른다면 `125`가 출력될 것이다.<br/>
정답은 `125`이다.

그럼 JavaScript가 `Call by Reference`를 따르는구나!라고 생각할 수 있지만, 이는 오산이다.

```jsx
function changeObject(obj) {
  obj = { a: 365 };
}

const test = { a: 1 };
changeObject(test);
console.log(test.a); // ?
```

그럼 위의 예시의 답은 뭘까?<br/>
`Call by Reference`를 따르니까 당연히 “`365`지!” 라고 생각할 수 있다.

하지만 정답은 `1`이다.

> ??????????????

GPT 선생님피셜으로는

> "Call by sharing"은 값에 의한 호출(Call by value)과 레퍼런스에 의한 호출(Call by reference)의 중간 형태로 간주될 수 있습니다.

라고 한다.

왜냐하면 `Call by Value`처럼 함수로 전달된 파라미터들은 값을 복사하여 전달한다.<br/>
하지만 그 값이 참조형(Reference Type)일 경우, 참조 변수 자체를 복사하여 전달하기 때문에 직접적으로 주소값을 전달하는 `Call by Reference`와는 차이가 있다.<br/>
이 방식이 바로 `Call by Sharing`이다.<br/>
Java, JavaScript Python 등의 언어가 이 방식을 따른다고 한다.

그럼 위의 예시를 다시한번 짚어보자.

```jsx
function changeObject(obj) {
  obj = { a: 365 };
}

const test = { a: 1 };
changeObject(test);
console.log(test.a);
```

현재 test라는 변수는 `{ a : 1 }` 이라는 객체를 참조하고 있다.<br/>
이후 changeObject 함수에 파라미터로 전달되는데, 이때 test라는 참조 변수를 복사하여 obj라는 함수에 전달하는 것이다.

```jsx
test -----> { a: 1 }
         ----^
        /
obj ---/
(copied by test)
```

다시 함수로 돌아와 함수 내부 코드를 실행하면

```jsx
test -----> { a: 1 }

obj ------> { a: 365 }
(copied by test)
```

다음과 같은 결과를 얻을 수 있다.<br/>
따라서 위의 예시 코드가 `365`가 아닌 `1`이 출력되는 것이다.
