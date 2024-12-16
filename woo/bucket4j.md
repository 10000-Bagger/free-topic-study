# Bucket4j
## Bucket4j란?
- 토큰 버킷 알고리즘에 기반한 Java 기반 rate-limiting 라이브러리이다.
- 고전적인 토큰 버킷 기반 구현체에서는 다뤄지지 않는 유용한 확장 기능들을 제공한다.
    - multiple limits per bucket
- 주요 특징
    - integer만을 사용하여 연산하기 때문에 연산의 정확도가 높다.
    - lock을 사용하지 않고 구현되어 있어 multi-threading 상황에 대한 확장이 용이하다.
    - 또한 별도의 concurrency 전략을 제공하기도 한다.
    - 최대한 원시 타입을 활용하여 boxing을 피했다.
    - monitoring / logging을 위한 API를 제공한다.
    - 내부 상태 조사를 위한 분석 API를 제공한다.
    - 버킷 구성을 쉽게 변경할 수 있다.
- 분산 환경의 특징
    -  JCache API(JSR 107) specification과 호환되는 GRID 솔루션을 지원한다.
    - RDMS 또는 key-value storage와 간편하게 통합할 수 있는 프레임워크를 제공한다.
    - thread blocking을 방지할 수 있도록 asynchronous API를 지원한다.

## 기본 개념
### (1) Bucket
- Bucket은 토큰 버킷 알고리즘 기반의 rate-limiter 구현체이다.
- Bucket은 아래 2가지로 구성된다.
    - BucketConfiguration: 불변 collection으로 bucket의 동작 규칙이 정의되어 있다.
    - BucketState: 가변 상태로 bucket의 현재 상태가 저장되어 있다. (이용 가능 횟수 등)

### (2) BucketConfiguration
- Bucket이 사용될 때 적용될 규칙들이 정의된 객체이다.
- BucketConfiguration은 불변이기 때문에 생성 이후 추가 혹은 삭제가 불가능하다.
- 하지만 BucketConfiguration을 신규 생성하여 Bucket에 새로 주입할 수 있다.(replaceConfiguration())
- 대체로 BucketConfiguration를 직접 생성하지는 않고 BucketBuilder에서 생성을 해준다.

### (3) Limitation / Bandwidth
- Bucket에서 사용되는 Limitation은 Bandwidth로 표시할 수 있다.
- Bandwidth는 아래와 같은 용어로 표시가 가능하다.

#### Capacity
- Bucket의 토큰량을 뜻하는 용어이다.

#### Refill
- Capacity만큼의 토큰을 다시 채워 넣는 주기를 뜻하는 용어이다
- Refill 방식에는 4가지가 존재한다.
    - Greedy: 가능한 빠르게 토큰을 채운다. 1초에 10개로 정책을 새우면 100 millisecond에 1개씩 넣는다.
    - Intervally: 설정된 주기마다 설정된 토큰을 넣어준다.
    - IntervallyAligned: Intervally와 동일하게 동작하지만, 추가적으로 첫번째 refill 시점을 설정할 수 있다.
    - RefillIntervallyAlignedWithAdaptiveInitialTokens: javadocs를 보라는데... 나중에 필요할 때 찾아보자..

#### Initial tokens
- 기본적으로 초기에 제공되는 token 수는 Capacity와 동일하다.
- 하지만 Initial tokens로 초기 token 수를 수정할 수 있다.

#### Bandwidth ID
- 용어 그대로 Bandwidth를 식별하는 식별자 값이다.
- 기본값은 null이고 Bucket에 2개 이상의 Bandwidth를 사용해야 할 때 사용하면 된다.

### (4) BucketState
- Bucket의 상태를 저장하는 공간을 뜻한다.
- 아래 2가지 데이터를 저장하고 변경한다.
    - 현재 이용 가능한 토큰 수
    - 최근 refill 시점


### (5) BucketBuilder
- 생성자를 통한 생성을 제한하기 위해 만들어진 객체이다.
- Builder를 두어 생성 시점과 사용 시점을 분리하려고 한 이유는 크게 2가지이다.
    - 미래에 내부 구현체를 바꾸더라도 구버전 호환이 가능하도록 하기 위해서
    - 최신 라이브러리 디자인 패턴에서 사용되는 풍부한 빌더 API를 제공하기 위해