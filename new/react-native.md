## 번들러
- 번들링: 여러 모듈과 파일을 단일 파일로 병합하여 최적화하는 과정
![image](https://github.com/10000-Bagger/free-topic-study/assets/80238096/b25904d3-fdc1-482a-b7d2-3b2d768a0a66)
- RN의 기본 번들러인 metro는 일반적인 자바스크립트 번들러와 유사하게
- 모듈 탐색 -> 코드 변환 -> 마무리 작업으로 진행

### 모듈 해석
- Module Resolve: 코드 내 import가 어느 모듈을 참조하는지 찾아 로드하는 과정

``` js
import { SafeAreaProvider } from 'react-native-safe-area-context';
```
다음과 같이 라이브러리를 사용하기 위해 import를 한 경우

#### `react-native-safe-area-context`가 어디에 위치하고 있는지 찾는 방식

- 기본적으로 NodeJS의 Resolve 알고리즘에 따라 프로젝트 내에 위치한 `node_modules` 폴더 안에서 모듈을 탐색
- 이후 metro 번들러는 모듈 `package.json` 파일의 `react-native`, `main`, `browser` 필드에 정의된 파일을 진입점으로 참조

``` json
// package.json

{
  "name": "react-native-safe-area-context",
  ...
  "main": "lib/commonjs/index.js",
  "module": "lib/module/index.js",
  "react-native": "src/index.tsx",
  "types": "lib/typescript/index.d.ts",
  "source": "src/index.tsx",
}
```

- metro가 모듈을 해석할 때, `react-native`, `main`, `browser` 에 해당하는 파일을 우선 참조
- 만약 `react-native` 필드가 없다면 -> `main` 참조 -> 없으면 `browser` 참조하는 방식으로 진행

### 주입
- RM는 모듈 뿐만 아니라 기본적인 실행 환경을 위해 볓가지 코드를 주입
- 여기에는 호환성, 기능 확장을 위한 폴리필과 초기화 코드가 포함
- metro의 구성에 따라, 기본적으로 `@react-native/js-polyfills`가 주입됨 (metro-config에서 확인 가능)
- 현재 RN에서는 세가지 폴리필이 존재
   - `Object.es8.js`: `Object.entries`, `Object.values`를 지우너하기 위한 폴리필
   - `console.js`: `console.log`에 대한 포맷 개선, 네이티브 로깅을 위한 기능 제공
      - 자바스크립트 컨텍스트에 몇가지 네이티브 기능을 노출하는데, 그 중 하나가 `global.nativeLoggingHook`
      - 이를 통해 `console.log` 메시지를 네이티브 로그에 함께 기록할 수 있도록 함
   - `error-guard.js`: 앱 실행 중 에러가 발생할 경우, 핸들러를 통해 에러를 처리하기 위한 기능을 제공
      - RN 초기화 시, 전역 에러 핸들러를 등록하는 과정을 거치는데 런타임에 예기치 못한 에러가 발생할 경우 에러 핸들러에게 위임하여 처리
    

### 변환
- 해석된 모듈과 주입 코드들은 RN 실행 환경에 맞게 변환 과정을 거치게 된다
- 코드 변환은 babel을 통해 처리됨
- Hermes 엔진을 사용 중인지, 클래스가 코드에 존재하는지, 비동기 함수가 코드에 존재하는지 등등 작성한 코드를 기준으로 변환이 필요한지 확인한 후 변환이 필요한 경우에 `extraPlugins`에 플러그인을 추가하여 코드를 변환한다
- 위 과정은 각 모듈마다 개별적으로 수행되는데, 모듈이 1000개가 있다고 하면 위의 작업이 1000번 수행됨
- 각 모듈별로 Babel 플러그인 변환 과정을 모두 거치기 때문에 metro 번들러의 성능이 낮다
- react native 팀에서도 이를 알고, 현재 babel 대신 [rust 기반의 swc를 사용할 수 있도록 개선하는 작업을 진행](https://github.com/facebook/metro/pull/948)하고 있음

> 이렇게 RN에 플러그인이 많은 이유
> - RN 내부에서 사용하는 Flow 구문 제거 필요
> - Hermes 엔진의 경우 제대로된 ES6 사양을 지원하지 않음
> - 엔진의 몇가지 버그들로 인해 코드 변환이 반드시 있어야함
>     - ex. `const`, `let`을 지원하는데 블록 스코프를 완전하게 지원하지는 않음 -> 2024년에 릴리즈한다고 했는데 아직..


---

## 번들 살펴보기

- 아래 명령어를 실행하면 직접 번들을 생성할 수 있음

``` bash
npx react-native bundle \
  --platform <ios|android> \
  --dev true \
  --minify false \
  --bundle-output bundle.js \
  --sourcemap-output budnle.js.map \
  --assets-dest <path> \
  --reset-cache \
  --verbose
```

### 전역변수
- 번들 최상단에는 전역 변수들이 선언되어있는 것을 확인할 수 있음

``` js
// bundle.js

// 번들 실행 시작 시간
var __BUNDLE_START_TIME__ = this.natviePerformanceNow 
  ? nativePerformanceNow()
  : Date.now(),
  __DEV__ = true,
  process = this.process || {},
  __METRO_GLOBAL_PREFIX__ = '',
  __requireCycleIgnorePatterns = [/(^|\/|\\)node_modules($|\/|\\)/];

// 개발 모드
process.env = process.env || {};
process.env.NODE_ENV = process.env.NODE_ENV || "development";
```

### 폴리필
- 전역 객체를 매개변수로 갖고 있는 IIFE로 래핑되어있으며 캡슐화되어있음
- 전역 변수, 폴리필은 코드의 최상단에 있고 번들 실행 시 가장 먼저 평가됨

### 모듈 정의
- 폴리필 코드 이후부터는 모듈 정의 코드들이 위치하고 있음
- 모든 모듈은 `__d`라는 함수로 래핑되어있음
   - 이는 metro 폴리필 내의 `define`이다
- metro 번들러가 변환한 모든 모듈에는 고유한 id가 있으며, 해당 id를 통해 모듈 간에 서로 참조 (`require`) 함

``` js
// bundle.js

__d(function (global, _$$_REQUIRE, _$$_IMPORT_DEFAULT, _$$_IMPORT_ALL, module, eports, _dependencyMap) {
  _$$_REQUIRE(_dependencyMap[1]) = 783;

  ...
  
}, 0, [1, 783, 18, 836, 5540], "index.js"
```

- `0`: `index.js`의 모듈 id
- `[1, 783, 18, 836, 5540]`: 모듈 의존성
- `index.js`에서 참조하고 있는 다른 모듈의 id가 포함되며, 내부에서는 `_dependencyMap`을 통해 모듈 id 값을 참조

### 모듈 참조
- `__d`와 동일하게, `metroResolve` 함수가 `__r`이라는 전역 프로퍼티로 정의되어 있음
- 이를 통해 정의한 모듈들을 참조할 수 있음

``` js
__d(function (...) {
  // module code
}, ..., [...], "path/to/module");

__r(57); // node_modules/react-native/Libraries/Core/InitializeCore.js
__r(0); // index.js
```

- 기본적으로 2개의 모듈을 참조
  - `initializeCore.js`
  - `index.js`

- 번들 코드가 실행되면
  1. 전역 변수, 폴리필 적용
  2. 모듈 정의
  3. 초기화 코드 실행
  4. 어플리케이션 코드 실행
