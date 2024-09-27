## react native 번들러
> 회사에서 react native 번들러 PoC를 진행하고 있어서 관련 내용 작성해봅니다
>
> 기존의 babel 기반 번들러를 esbuild 기반으로 변경하는 내용입니다


### react native 동작 방식
- native 코드는 사용자의 기기에서 직접 실행될 수 있지만
- 자바스크립트 코드는 가상 머신이 필요함
- iOS에서는 JavascriptCore라는 빌트인 자바스크립트 엔진이 있지만, 안드로이드에는 없음
- Bridge를 통해 Java/Obj-C와 자바스크립가 JSON으로 정보를 주고 받음

![image](https://github.com/10000-Bagger/free-topic-study/assets/80238096/9e85b98a-ca3d-40c3-b64e-de6ed3786617)

- 앱을 빌드하면 Java/Obj-C는 각각 Java, C++로 컴파일됨
- 자바스크립트 코드는 metro 번들러에 의해 번들됨

### metro
- metro 번들러는 일반적인 웹 개발에서 웹팩과 유사한 역할을 함
- 즉, 자바스크립트 파일을 하나로 모아 제공하는 번들러

#### 주요 3가지 단계로 동작
1. resolution
   - 파일 간의 의존성을 찾기 위해 Resolver를 사용
  
2. Transformation
   - babel을 사용해 react native에서 이해할 수 있는 형식으로 변환

3. Serialization
   - transformation을 거친 모든 모듈은 serialization이 수행됨
   - 모듈을 결합하여 하나 또는 여러개의 번들을 생성
  
### metro가 느린 이유
- 위 3가지 단계 중 transformation 과정에서 오랜 시간이 걸림
- 코드를 변환하는 것 자체에도 비싼 연산이 드는데, babel을 이용하기 때문에 더욱 오래 걸림
- 대부분의 node module은 commonJS 지원을 포함하기 때문에 babel 연산이 불필요함

### esbuild
- 메트로와 같은 번들러 역할을 하지만, Go로 작성되어 속도가 더빠르다
   - 대부분의 번들러는 자바스크립트로 작성되어 있음
   - Go와 자바스크립트는 모두 병렬적으로 동작하는 GC가 있지만
   - Go의 힙은 모든 스레드 간에 공유되고, 자바스크립트는 스레드마다 별도의 힙이 있어
   - 자바스크립트 워커 스레드에서 가능한 병렬 처리 양이 줄어듦
- 메모리 효율
   - 컴파일러는 많은 양의 데이터를 처리하는 경우, 메모리 액세스 속도가 성능에 큰 영향을 미침
   - 데이터를 전달하는 횟수를 최소화해야 컴파일러의 성능을 향상 시킬 수있음
   - esbuild는 JS AST를 세번만 처리함 
