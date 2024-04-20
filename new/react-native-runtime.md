## React Native Runtime
### 기본 아키텍처
- 리액트 네이브의 기본적인 아키텍처를 살펴보면 아래와 같다

![image](https://github.com/10000-Bagger/free-topic-study/assets/80238096/bf28e21e-3721-4f69-82f9-d40728683567)

- 자바스크립트와 네이티브 간의 상호작용은 브릿지를 통해서 이루어진다.
- 하지만 이 브릿지에는 몇가지 성능 이슈가 있다
1. 상호작용을 위해 JSON으로 직렬화/역직렬화가 필요하고
2. 모든 작업이 비동기로 처리된다.


### 새로운 아키텍처
- 이러한 문제를 개선하기 위해 RN팀에서 새로운 아키텍처에 대해 발표했다.
- 새로운 아키텍처가 발표된 후에는 브릿지를 -> JSI(Javascript Interface)가 대체하게 될 것이라 예상했다.

#### JSI
- 현재 RN은 자바스클비트 런타임과 상호작용하는 코어 로직이 JSI 기반으로 대체되었고, 여전히 브릿지는 유효하다
- 브릿지 또한 JSI 기반으로 동작하고 있기 때문에 새로운 아키텍처에서만 JSI가 사용된다는 것은 잘못된 사실이다.

#### 브릿지
> 기존 아케턱처의 브릿지와 새로운 아키텍처의 구성요소들은 모두 JSI 기반으로 동작하며, 이들은 추가적인 JSON 직렬화 과정 없이 JSI와 동기적으로 상호작용하거나 비동기적(Bridge)로 상호작용한다.
- 브릿지에서 JSON 형태로 직렬화/역직렬화하는 로직도 JSI 기반으로 대체되었다.
   - AS-IS: `callNativeModule`
      - JSON 직렬화/역직렬화 과정 존재 
   - TO-BE: `dynamicForValue`
      - JSI 값으로 처리( JSON 직렬화/역직렬화 과정 X)
- JSI 기반으로 변경된 로직에서 브릿지가 동작하고 있는데, 기존 브릿지 동작 매커니즘에 대한 변경은 없다.
- 여전히 남아있는 브릿지의 단점을 해결하기 위해서는 Native Modules를 Turbo Modules로 마이그레이션하거나, C++(JSI) 기반으로 코드를 재작성하는 작업 등이 필요하다.


### JNI
![image](https://github.com/10000-Bagger/free-topic-study/assets/80238096/eac4fe6a-c7d4-4042-b531-f6e0abc66c8d)

- JSI(Javascript Interface): 자바스크립트 런타임 엔진은 성능을 위해 대부분 C/C++ 기반으로 구현되어있다.
- JNI(Java Native Interface): Java와 네이티브(C/C++) 간의 상호작용을 가능하게 하는 기술이다.
- 안드로이드의 경우, 자바 혹은 코틀린 언어를 기반으로 네이티브를 구현하는데
- 이 언어들이 컴파일되고 실행되는 JVM에서는 C/C++ 기반으로 작성된 네이티브 코드를 실행할 수 없기 때문에 JNI를 사용하여 네이티브 코드를 실행가능하게한다.

### 자바스크립트 런타임
- RN에서는 JSC(Javscript Core) 혹은 Hermes 엔진을 어플리케이션 내부에 포함시키고 이를 통해 번들을 실행시킨다.

#### JSC
- JSC는 사파리 브라우저에서 사용되고 있는 자바스크립트 엔진이다
- RN 0.70.0 이전에서는 기본적으로 JSC 엔진이 사용되었으나, 이후부터는 Hermes가 기본 엔진으로 변경되었다.

#### Hermes
- 메타에서 개발한 RN을 위한 경량 엔진이다.
- Hermes 디버깅을 위한 프록시 런타임도 존재한다.
- 실제 어플리케이션 내에 존재하는 Hermes 엔진을 통해 구동하는 것이 아니라, 개발 모드로 연결되어 있는 PC의 크롬에서 구동된다.
- 즉, V8이 런타임이 된다.

#### JSIExecutor
- 자바스크립트와 네이티브 간의 상호작용을 위한 기능이 구현되어 있다
- 런타임 초기화시, 몇 가지 기능들을 자바스크립트 전역 컨텍스트에 노출시킨다.

``` cpp
void JSIExecutor::initializeRuntime() {
  runtime_ -> global().setProperty(
    *runtime_,
    "nativeModuleProxy", ...);
  ...
}
```

- JSC, Hermes 모두 `JSExecutorFactory`를 통해 런타임 인스턴스가 생성된다.
