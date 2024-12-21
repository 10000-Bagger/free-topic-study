> One of TypeScript’s core principles is that type checking focuses on the *shape* that values have.<br/>
> This is sometimes called “duck typing” or “structural subtyping”.<br/>
> In TypeScript, interfaces fill the role of naming these types, and are a powerful way of defining contracts within your code as well as contracts with code outside of your project.

위는 타입스크립트 공식 문서의 첫 문장이다.<br/>
타입스크립트의 가장 중요한 원칙 중 하나는 타입을 확인할 때 값의 `shape`에 집중하고, 이를 `duck typing` 혹은 `구조적 서브타이핑(structural subtyping)`이라 소개한다.<br/>
그럼 이게 무엇이길래 타입스크립트에서는 강조할까?

### 타이핑 vs 서브타이핑

먼저, 용어를 구글링하다보니 언제는 타이핑, 언제는 서브타이핑…<br/>
처음 타이핑이라는 단어를 들었을때는 “타자를 치다”의 타이핑으로 해석하여 프로그래밍 기법 중 하나라고 생각했다.<br/>
그럼 서브타이핑은 뭔데?<br/>
둘이 어떤 차이가 있길래 용어가 다를까 싶어 GPT 선생님께 여쭤봤다.

```
[ 타이핑 ]

타이핑은 프로그램 내에서 변수, 함수, 객체 등에 타입을 부여하는 과정을 의미합니다.
타입은 데이터의 종류와 해당 데이터에 수행할 수 있는 연산을 정의합니다.
예를 들어, 정수(int), 문자열(string), 부동 소수점(float) 등이 타입의 예입니다.
타입 시스템은 프로그램이 실행되기 전에 타입 오류를 검출함으로써 프로그램의 안전성을 높이는 데 도움을 줍니다.

[ 서브타이핑 ]

서브타이핑은 하나의 타입이 다른 타입의 서브타입(subtype)일 때, 즉 특정 타입의 객체가 다른 타입의 객체로 사용될 수 있는 관계를 의미합니다.
서브타입은 슈퍼타입(supertype)의 모든 속성과 동작을 상속하지만, 추가적인 속성과 동작을 가질 수 있습니다.
```

선생님의 설명은 단어 뜻 그대로였다.

**타이핑**은 코드에서 값들의 타입을 **언제** 결정하는지를 말하는 것이었다.<br/>
예를 들면,<br/>
`JavaScript`는 **런타임**에 타입이 결정되는 동적 타이핑 언어이다.<br/>
따라서 변수 선언시 따로 타입을 명시하지 않아도 런타임 과정에서 동적으로 해석한다.<br/>
반면 `TypeScript`는 **컴파일타임**에 타입이 결정되는 정적 타이핑 언어이다.<br/>
따라서 코드가 실행되기 이전에 타입을 먼저 검사하여 에러를 발견할 수 있는 것이다.

반면, **서브타이핑**은 값들의 포함 관계, 즉, **상속 관계**를 나타내는 것이었다.<br/>
따라서 **다형성**과 관련하여 어떻게 특정 타입이 다른 타입의 서브셋인지를 판단하고, 사용될 수 있는지를 결정하는 정책과 관련이 있다.

타이핑이 서브타이핑보다 좀더 넓은 개념의 타입을 지정하는 방식이라는 생각이 들어 딱히 나눠서 생각할 필요는 없을 것 같다는 느낌을 받았다.

### 덕 타이핑

그럼 타입스크립트의 공식 문서에서 언급한 덕 타이핑에 대해 먼저 알아보자.

> 덕 타이핑은 동적 타이핑의 한 종류로, 객체의 변수 및 메소드의 집합이 객체의 타입을 결정하는 것을 말한다.<br/>
> 클래스 상속이나 인터페이스 구현으로 타입을 구분하는 대신, 덕 타이핑은 객체가 어떤 타입의 걸맞는 변수와 메소드를 지니면 객체를 해당 타입에 속하는 것으로 간주한다.

”만약 어떤 새가 오리처럼 걷고, 헤엄치고, 꽥꽥거리는 소리를 낸다면 나는 그 새를 오리라고 부를 것이다.” - [위키백과](https://ko.wikipedia.org/wiki/%EB%8D%95_%ED%83%80%EC%9D%B4%ED%95%91)

>

이 말은 즉슨, 내가 사용할 파라미터에 타입을 명시하였더라도 파라미터로 들어온 값이 명시한 타입에 존재하는 속성과 메서드를 포함하고 있다면 같은 타입으로 보겠다!라는 말이다.<br/>
아래는 [마이구미님의 블로그](https://mygumi.tistory.com/367)에서 잘 작성해주신 예시이다.

```tsx
interface Quackable {
  quack(): void;
}

class Duck implements Quackable {
  quack() {
    console.log("Quack");
  }
}

class Person {
  quack() {
    console.log("Quack");
  }
}

function inTheForest(quackable: Quackable): void {
  quackable.quack();
}

inTheForest(new Duck()); // OK
inTheForest(new Person()); // OK
```

inTheForest 함수에서 파라미터의 타입을 `Quackable`로 정확히 명시하였다.<br/>
하지만, 가장 마지막줄에서 `Person`이라는 class는 `Quackable`을 상속 받지 않았지만 정상적으로 동작한다.<br/>
그 이유는 `Quackable` 언터페이스에 존재하는 quack이라는 함수가 `Person`에도 존재하기 때문에 같은 타입으로 간주되기 때문이다.<br/>
따라서 정상 동작하는 코드라면 위와 같이 타입을 정확히 명시하지 않아도 같은 타입으로 간주하여 유연하게 대응하여 타입을 호환하는 것이 더 좋을 수 있기 때문에 타입스크립트는 이러한 시스템을 따른다고 생각한다.

[토스 테크 블로그](https://toss.tech/article/typescript-type-compatibility)에서도 타입 시스템의 유연성 허용 범위를 어느 범위까지 허용할지에 한정하기 위한 방식으로 TypeScript 공식 문서에서 언급한 `구조적 서브타이핑`을 포함하여 `명목적 서브타이핑` 을 함께 설명한다.

### 명목적 서브타이핑

“명목적 서브타이핑”은 **타입 정의시 상속 관계으로 명시를 해야한 경우에만 타입 호환이 가능한 방식**이다.<br/><br/>
상속 관계를 통해 **타입의 이름으로 호환 가능한 타입을 명시**하기 때문에 타입의 구조가 같더라도 다른 타입으로 취급한다.

```tsx
/** 상속 관계 명시 */
type Food = {
  protein: number;
  carbohydrates: number;
  fat: number;
};

type Burger = Food & {
  burgerBrand: string;
};

const burger: Burger = {
  protein: 29,
  carbohydrates: 48,
  fat: 13,
  burgerBrand: "버거킹",
};

function calculateCalorie(food: Food) {
  return food.protein * 4 + food.carbohydrates * 4 + food.fat * 9;
}

const calorie = calculateCalorie(burger);
/** 타입검사결과 : 오류없음 (OK) */
```

### 구조적 서브타이핑

“구조적 서브타이핑”은 **오직 멤버만으로 타입을 관계시키는 방식**이다.<br/>
타입 시스템이 객체의 속성을 체크하는 과정을 수행해주므로써, 명목적 서브타이핑과 동일한 효과를 내면서도 개발자가 상속 관계를 명시해주어야 하는 수고를 덜어준다.

```tsx
const burger = {
  protein: 29,
  carbohydrates: 48,
  fat: 13,
  burgerBrand: "버거킹",
};

const calorie = calculateCalorie(burger);
/** 타입검사결과 : 오류없음 (OK) */
```

따라서 읽다보니 위에서 알아본 덕타이핑이랑 같은데? 라고 생각했는데 진짜로 구조적 서브타이핑을 “덕 타이핑”이라고도 부른다고 한다.<br/>
다른건줄 알았는데 같아버렸다;

### 정리

여태까지의 내용을 정리해보자.<br/>
TypeScript에서 “구조적 서브타이핑”은 핵심 규칙 중 하나이다.<br/>
구조적 서브타이핑은 특정 값의 타입을 비교할 때, 명시된 이름이 아닌 구조, 즉, 속성과 메서드가 일치하는지 **모양을 비교하여 유연하게 타입 호환성을 제공**한다.<br/>
생각해보면 이러한 구조적 서브타이핑이 막상 장점만 존재할 것 같지는 않다.<br/>
선택적으로 속성이나 메서드가 존재할 수도 있고, 엄청 많은 언터페이스나 타입이 합쳐져 확장된 타입 또한 존재할 수 있을텐데, 이때 타입을 특정하거나 코드를 이해하기 힘들 수 있을 것 같다는 생각이 들었기 때문이다.
