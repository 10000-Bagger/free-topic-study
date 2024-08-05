# Feature-Sliced-Design (FSD)


> 기능 분할 설계(Feature-Sliced Design, FSD)는 애플리케이션의 복잡성을 관리하고 코드의 유지 보수성을 높이기 위한 설계 방식입니다. FSD는 기능을 기준으로 코드를 모듈화하고, 각 모듈이 독립적으로 개발 및 테스트될 수 있도록 합니다.

FSD는 3개의 계층으로 이루어집니다.

- **레이어(Layers)**
- **슬라이스(Slices)**
- **세그먼트(Segments)**

## Layers

app, pages, widgets, features, entities, shared로 구성

```jsx
// FSD Layers 폴더 구조
src/
  ├── app/
  ├── ~~processes~~(사용 X)/
  ├── entities/
  ├── features/
  ├── pages/
  ├── widgets/
  └── shared/
```


> **하위 레이어는 상위 레이어를 참조(import)할 수 없습니다.**
>
> 예시: 
>
> - entities 레이어에서 widgets 레이어 참조 불가
> - app 레이어는 모든 하위 레이어 참조 가능
    

1. `App`
    - 앱의 진입점과 전역 설정을 포함한 폴더
    
    - 라우팅, 전역 스타일, 프로바이더 등 포함
    - everything that makes the app run — routing, entrypoints, global styles, providers.
2. `Pages`
    - 전체 페이지 또는 중첩 라우팅의 큰 부분을 담당하는 컴포넌트를 포함하는 폴더
    
    - 화면 구성 요소를 포함하며, 특정 경로에서 사용자에게 보여지는 UI 담당
    - 한 페이지는 여러 기능을 포함할 수 있음
    - full pages or large parts of a page in nested routing.
3. `Widgets`
    - 큰 단위의 기능이나 UI를 포함하는 폴더
    - 하위의 레이어(entities, features)를 이용하여 특정 피쳐에서 사용할 수 있는 UI 포함
    
    - 해당 도메인에 widget layer가 불필요하다면 생략 가능
    - 특정 의존성과 강결합 되어있기 때문에 여러 페이지에서 재사용하지 못할 수 있음
    - 엔티티에 속하지 않고 features에 속하지 않으면서 이 둘을 합쳐서 활용하는 곳
    - 리액트에선 컴포넌트와 훅이 대표적
    - large self-contained chunks of functionality or UI, usually delivering an entire use case.
4. `Features`
    - 유저의 인터렉션과 관련된 로직, 특정 비즈니스 로직이 담겨있는 레이어
    - 재사용 가능한 기능 단위
    - 각 기능은 독립적으로 작동하며 특정 도메인 로직 수행
    - 애플리케이션의 주요 기능 모듈화
    - 데이터를 UI의 상태 (리액트의 state 등)으로 변환하거나 그러한 값들을 비즈니스 값으로 변환하는 곳
    - 주로 이벤트 리스터, 훅, 상태관리도구, 리액트 쿼리 등이 위치
    
    - 동사형으로 폴더명 생성 (ex. GetSellerList, SendComment…)
    - *reused* implementations of entire product features, i.e. actions that bring business value to the user.
5. `Entities`
    - 도메인 모델과 관련된 핵심 개념 포함
    - 간단하게 말하면, 비즈니스 로직의 주체
    - 특정 프레임워크나 방법론에 속하지 아닌 범용적인 비즈니스 로직
    
    - 해당 도메인과 연관된 api 호출 함수 정의
    - 프로젝트에서 다루는 비즈니스 엔티티를 나타내는 폴더
        - ex. User, Product, Order 등
    - business entities that the project works with, like `user` or `product`.
6. `Shared`
    - 프로젝트 전반에 걸쳐 재사용 가능한 기능을 포함하는 폴더
    
    - 특정 비즈니스 로직에 의존하지 않는 일반적인 유틸리티나 컴포넌트 포함
    - reusable functionality, especially when it's detached from the specifics of the project/business, though not necessarily.

## Slices

비즈니스 도메인을 폴더로 나눈 것 (ex. User, Seller, PreSeller…)

각 슬라이스 폴더의 도메인은 index 파일로 export 한다.

```tsx
└── features/               #
       ├── Seller/          # Internal structure of the feature
       |     ├── ui/        #
       |     ├── model/     #
       |     ├── {...}/     #
       ├── **index.ts**         # Entrypoint features with its public API
```

## **Segments**

세그먼트의 이름은 ui, model, lib, api 등이 될 수 있다.

- api: api를 호출하기 위한 코드
- ui: UI 컴포넌트
- model: 비즈니스 로직, data aggregation 함수
- lib: infra structure code

```bash
├── features/
+    |   ├── add-to-cart/ {ui, model, lib}
+    |   ├── choose-delivery/ {ui, model, lib}
├── entities/{...}
+    |   ├── delivery/ {ui, model, lib}
+    |   ├── cart/ {ui, model, lib}
+    |   ├── product/ {ui, model, lib}
├── shared/
+    |   ├── api/
+    |   ├── lib/    # helpers
+    |   ├── config/ # constants
```

### 기존 리액트 폴더 구조에서 마이그레이션 예시

![Untitled](Feature-Sliced-Design%20(FSD)%20c2bbec66564e423394352f64335f6e0e/Untitled%203.png)

### react-query와 적용하기

참고 링크: https://feature-sliced.design/docs/guides/tech/with-react-query

```bash
src/                                        #
├── app/                                    #
|   ...                                     #
├── pages/                                  #
|   ...                                     #
├── entities/                               #
|     ├── {entity}/                         #
|    ...     └── api/                       # Query-factory
|                 ├── `{entity}.query`      # where are the keys & functions
|                 ├── `get-{entity}`        # Entity getter function
|                 ├── `create-{entity}`     # Entity creation function
|                 ├── `update-{entity}`     # Entity update function
|                 ├── `delete-{entity}`     # Entity delete function
|                ...                        #
|                                           #
├── features/                               #
|   ...                                     #
├── widgets/                                #
|   ...                                     #
└── shared/                                 #
    ...                                     #
```
