# DOM 이벤트 관리

> 웹 어플리케이션은 고정된 그림이 아닌 시간이 지남에 따라 변경되는 것

→ 변경 사항을 발생시키는 것이 바로 **“이벤트”**

## YAGNI 원칙

필자는 프로젝트 진행시 다음과 같이 접근한다.

> 먼저 가장 중요한 기능에 초점을 맞춰 개발하고 새로운 요구사항에 따라 아키텍처를 지속적으로 발전시킨다.

이것이 바로 **“YAGNI 원칙”**이다.

> You Aren’t Gonna need it. - 정말 필요하지 않다면 기능을 추가하지 마라.

XP의 창시자 중 한 분인 론 제프리스도 다음과 같이 이야기하였다.

> 당신이 필요하다고 예측할 때가 아니라 실제로 필요할 때 구현하라.

프레임워크가 없는 개발에서는 이는 매우 중요하다.

아키텍처가 과도하게 **오버 엔지니어링**될 수 있기 때문이다.

## DOM 이벤트 API

- 마우스 - 클릭, 더블 클릭 등
- 키보드 - 키다운, 키업 등
- 뷰 - 크기 조정, 스크롤 등

(전체는 모질라에서 확인하자.)

시스템 자체에서도 이벤트를 생성할 수 있으며,

이벤트에 반응하기 위해선, 이벤트를 트리거한 DOM 요소에 이벤트 핸들러(콜백)를 연결해주어야 한다.

### 속성에 핸들러 연결

> on 속성을 이용한 이벤트 핸들러 연결 방식

```jsx
const button = document.querySelector("button");
button.onclick = () => {
  /* event */
};
```

- 빠르지만 다소 지저분할 수 있다.
- onClick, onBlur, onFocus 등등..

잘 동작하긴 하지만, 한번에 하나의 핸들러만 연결이 가능하기 때문에 `addEventListener` 메서드를 사용하는 편이 나을 수 있따.

### addEventListener로 핸들러 연결

> `addEventListener` 메서드를 통해 이벤트 핸들러를 DOM 노드에 추가하는 방식

```jsx
const button = document.querySelector("button");
button.addEventListener("click", () => {
  /* event */
});
```

- 이벤트 타입과 이벤트 핸들러를 파라미터로 받는다.
- 속성 방식과 달리 모든 핸들러를 연결할 수 있다.

메모리 릭을 방지하고자 DOM 요소가 사라지면 이벤트 리스너 또한 삭제해주어야 하는 번거로움이 존재한다.

이때 `removeEventListener` 메서드를 사용하며 이벤트 리스너를 파라미터로 전달해야하기 때문에 참조를 잘 유지해주어야한다.

### 이벤트 객체

이벤트 핸들러에는 DOM 노드나 시스템에서 생성한 이벤트를 나타내는 파라미터를 포함할 수 있다.

```jsx
const button = document.querySelector('button');
button.addEventListener('click', **event** => {
	/* event */
	console.log(event);
});
```

위의 예시 코드의 **`event`**가 바로 이벤트 객체로, 포인터 좌표, 이벤트 타입, 이벤트 트리거 요소 등 다양한 정보가 포함되어 있다.

### DOM 이벤트 라이프사이클

`addEventListener` 메서드는 `useCapture`라고 불리는 3번째 파라미터를 받을 수 있으며, 기본값은 false이다.

옵셔널 파라미터이지만, 폭넓은 브라우저 호환성을 위해 포함하는게 좋다고 한다.

```html
<div>
  <button>Click</button>
</div>
```

```jsx
const button = document.querySelector("button");
const div = document.querySelector("div");

div.addEventListener("click", () => {
  console.log("div clicked");
});

button.addEventListener("click", () => {
  console.log("button clicked");
});
```

위와 같은 경우 div 내부에 button이 존재하여 button부터 시작하여 부모 노드로 올라가며 이벤트 핸들러가 모두 호출되는 `이벤트 버블링`이 발생한다.

이는 `stopPropagation` 메서드를 통해 버블 체인을 중지할 수 있다.

여기서 만약 useCapture 파라미터를 true로 변경한다면 button부터 이벤트 핸들러가 불리는 것이 아닌, **반대로 부모부터 button 순서로 핸들러가 호출**된다.

요약하자면,

- 캡처 단계: 이벤트가 HTML에서 목표 요소로 이동
  - 핸들러가 하향식(top-down)으로 처리됨
- 버블 단계: 이벤트가 목표 요소에서 HTML로 이동
  - 핸들러가 상향식(bottom-up)으로 처리됨
- 목표 단계: 이벤트가 목표 요소에 도달한다.
  - 뜬금없이 책에서 등장하여 무슨 말인지 잘 모르겠다.

### 사용자 정의 이벤트 사용

DOM 이벤트 API에서는 사용자 정의 이벤트 타입을 정의하고 다른 이벤트처럼 처리할 수 있다.

이는 도메인에 바인딩되고 시스템 자체에서만 발생한 DOM 이벤트를 생성할 수 있다.

로그인, 로그아웃, 리스트에 새 레코드를 생성하는 등 데이터 집합에서 발생한 이벤트에 대한 이벤트 핸들러를 생성할 수도 있다.

```jsx
const EVENT_NAME = "FiveCharInputValue";
const input = document.querySelector("input");

input.addEventListender("input", () => {
  const { length } = input.value;

  if (length === 5) {
    const time = new Date().getTime();
    const event = new CustomEvent(EVENT_NAME, {
      detail: { time },
    });

    input.dispatchEvent(event);
  }
});

input.addEventListener(EVENT_NAME, (e) => {
  console.log("handling custom event...", e.detail);
});
```

위 예시에서는 input의 value 길이가 5라면 `FiveCharInputValue`라는 커스텀 이벤트를 발생시킨다.

## 이벤트 위임

하나의 요소 안에 여러 요소들이 존재하고 각 하위 요소마다 이벤트를 연결할 경우, 이벤트 위임을 통해 상위 요소에서 이벤트를 관리할 수 있다.

이를 통해 성능과 메모리 사용량을 개선시킬 수 있다.

```html
<div id="Menu">
  <button data-action="save">저장하기</button>
  <button data-action="reset">초기화 하기</button>
  <button data-action="load">불러오기</button>
</div>
```

```jsx
const $Menu = document.getElementById("Menu");

const ActionFunctions = {
  save: () => alert("저장하기"),
  reset: () => alert("초기화하기"),
  load: () => alert("불러오기"),
};

$Menu.addEventListener("click", (e) => {
  const action = e.target.dataset.action;
  if (action) {
    ActionFunctions[action]();
  }
});
```
