NextJS는 기본적으로 모든 페이지를 `Pre-Rendering` 한다.<br/>
서버 단에서 미리 HTML을 생성하는 것이다.

그리고 생성된 HTML과 필요한 자바스크립트 번들을 클라이언트에게 응답한다.<br/>
이후 자바스크립트 코드가 실행되면서 HTML과 매칭되어사용자와 상호작용할 수 있게 되는데, 이 과정을 `Hydration`이라고 한다.

NextJS에서는 기본적으로 `SSG` 방식을 채택하여 사용한다고 한다.<br/>
그리고 Pre-Rendering의 방식에는 `SSG`와 `SSR`, `ISR`이 존재한다고 하는데, 크게 알아보지 않았던 개념들이고, 면접 때도 자주 물어본다고 하여 간단히 정리해보려고 한다.

## SSR

> Server Side Rendering

페이지 요청시 서버에서 **해당 페이지의 HTML을 만들어 응답**해준다.<br/>
즉, 런타임에 **새로운 HTML을 생성**하여 응답을 한다.<br/>
따라서 HTML이 생성될 때의 최신 데이터를 불러와 반영하기 때문에 동적이다.<br/>
하지만 페이지 **진입을 할 때마다 서버에서 해당 페이지의 HTML을 생성하는 오버헤드**가 존재하고, SSG, ISR에 비해 느리다.<br/>
또한 매번 렌더링이 진행되어 HTML이 변할 수 있기 때문에 CDN 캐싱을 할 수 없고, 페이지 이동시 화면이 깜빡거린다.

## SSG

> Static Site Generation

서버에서 **정적인 HTML을 미리 생성**해둔다.<br/>
HTML을 생성하는 시점은 **빌드 시점**이고, **CDN 캐싱**을 통해 빠르게 응답할 수 있다.<br/>
하지만 미리 빌드 단계에서 HTML을 만들어두기 때문에 최신 데이터를 반영하지 않을 수 있다.

## ISR

> Incremental Static Regeneration

ISR은 SSG 방식의 이점을 유지하면서 동적으로 데이터를 업데이트할 수 있도록 한다.<br/>
ISR에서는 정적인 페이지가 빌드 된 이후에도 **정해진 주기마다 새롭게 재생성**되며 최신 데이터를 반영할 수 있다.<br/>
이것을 `Revalidate`라고 부른다.<br/>
SSG와 마찬가지로 CDN 캐싱이 가능하며 이를 통해 빠르게 응답할 수 있다.<br/>

추가적으로 `Dynamic Static Pages` 라는 개념이 존재한다.<br/>
NextJS의 Page Router에서는 `getStaticPaths`와 `getStaticProps` 함수를 사용하여 `Dynamic Static Pages`를 생성할 수 있다.

`getStaticPaths` 를 통해 동적 경로를 가진 페이지에 대해 미리 생성할 경로를 정의한다.<br/>
이는 빌드시 모든 경로에 대해 페이지를 생성한다.

`getStaticProps` 를 통해 각 경로에 대해 정적 페이지를 생성하는데 필요한 데이터를 가져오고 **revalidate** 속성을 통해 **ISR**을 설정할 수 있다.

NextJS의 App Router에서는 app 하위의 layout 파일에

> export const revalidate = 3600

와 같이 명시하거나 fetch를 사용한다면 option에 revalidate 속성에 값을 넣어 사용할 수 있는 것 같다.
