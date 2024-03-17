## Interface의 목적
- 어떻게 구현 되었는가로부터 무엇을 구현했는가를 불리시켜 추상화가 가능하다
- 모듈화를 통해 재사용 가능한 코드이다
- 구현체가 어떤 역할을 할 지 구체화한다
## 1개의 구현체를 가진 Interface를 쓰는 이유
### 1. 결합을 느슨하게 만들여 유연성을 높인다
- 사용부에서 Interface를 의존하기 때문에 구현체와의 의존성이 느슨해진다.
- 이는 곧 구현체가 얼마든지 추가될 수 있고 추가되어도 사용부의 변화가 없다는 의미
- 즉, 확장에 용의하다
### 2. 구체적인 행동을 강제할 수 있다.
### 3. 테스트를 위한 구현체를 그때 그때 만들 수 있어 테스트와 Mocking에 용의하다

## 1개의 구현체를 위한 Interface의 단점
- 복잡도를 증가시키고 코드를 더 많이 작성해야 한다.
- 구현체가 절대 늘어나지 않는다면 큰 이점이 없을 수 있다.
- 구현체가 추가될 때 Interface를 만드는 게 나을 수도 있다.
- 타 모듈에 대한 종속성이 없을 경우 인터페이스의 이점이 적을 수 있다.

## Reference
- [Should We Create an Interface for Only One Implementation?](https://www.baeldung.com/java-interface-single-implementation)