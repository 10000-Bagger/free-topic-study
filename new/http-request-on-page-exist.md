# 사용자가 페이지를 떠날 때 안정적으로 HTTP 요청 보내기

> ### TL;DR
> 1. promise
> 2. fetch keepalive
> 3. Navigator.sendBeacon()
> 4. ping

사용자가 다른 페이지로 이동하거나 특정 행동을 할 때, 로깅할 데이터가 포함된 HTTP 요청을 전송해야 하는 경우가 있음

- 예시: 링크를 클릭하면 정보를 외부 서비스로 전송하는 경우


```html
<a href="/some-other-page" id="link">Go to Page</a>

<script>
document.getElementById('link').addEventListener('click', (e) => {
  fetch("/log", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    }, 
    body: JSON.stringify({
      some: "data"
    })
  });
});
</script>
```

- 링크가 동작하기 전, `click`하면 `POST` 요청이 발생
- 요청이 성공적으로 처리된 것처럼 보임. 하지만 항상 그렇지 않음

## 브라우저는 열린 HTTP 요청의 보존을 보장하지 않습니다.

브라우저의 페이지를 종료시킬 때, 진행 중인 HTTP 요청이 성공적으로 처리된다는 보장 없음
  - 참고: [페이지 생명 주기의 "terminated" 및 다른 상태](https://developer.chrome.com/blog/page-lifecycle-api/)


## 근데 왜 취소될까요?

- XHR 요청(`fetch` 혹은 `XMLHttpRequest`에 의한)은 비동기적이고 블로킹이 없기 때문
  - 요청이 대기열에 들어가자마자, 요청의 실제 *작업*은 백그라운드에서 브라우저 레벨의 API로 전달

- 즉, 페이지가 "terminated" 상태가 될 때, 그 어떤 백그라운드 작업도 완료된다는 보장이 없다.

> **[Google 이 라이프 사이클 상태](https://developer.chrome.com/blog/page-lifecycle-api/#states) 요약 내용**
>
> 브라우저 메모리에서 내려가고 지워지기 시작하면 페이지는 terminated 상태가 됩니다.
> 
> 이 상태에서는 [새로운 작업](https://html.spec.whatwg.org/multipage/webappapis.html#queue-a-task)이 시작되지 않으며, 진행 중인 작업이 너무 오래 실행될 경우 중지될 수 있습니다.
> 
> 간단히 말해서, 브라우저는 페이지가 삭제될 때, 페이지에 의해 대기 중인 백그라운드 프로세스를 계속 처리할 필요가 없다는 가정 하에 설계되었습니다.

## 그래서, 우리가 선택할 수 있는 건 무엇일까요?

- 가장 명확한 접근 방법은 요청이 응답을 반환할 때까지 사용자 작업을 지연시키는 것
- `XMLHttpRequest`에서 지원하는 [synchronous 플래그](https://xhr.spec.whatwg.org/#synchronous-flag)를 사용하는 잘못된 방식으로 했었음
   - 이 방법은 메인 스레드를 완전히 차단시키고
   - 여러 성능 문제가 발생
     -  [관련 글](https://macarthur.me/posts/use-web-workers-for-your-event-listeners) 참고
     -  [Chrome v80+에서는 이미 제거됨.](https://developer.chrome.com/blog/chrome-80-deps-rems/)


- 대신, 이런 접근 방식을 사용할 경우 응답이 반환되어 `Promise` 가 resolve 될 때까지 기다리는 것이 좋음

```js
document.getElementById('link').addEventListener('click', async (e) => {
  e.preventDefault();

  // 응답이 돌아오기를 기다리고...
  await fetch("/log", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    }, 
    body: JSON.stringify({
      some: 'data'
    }),
  });

  // ...나서 페이지를 이동한다.
   window.location = e.target.href;
});
```

- 작업은 완료할 수 있지만 단점 있음

1. 지연으로 인한 사용자 경험을 손상.
2. 몇몇 종료 동작은 프로그래밍 방식으로 지연시킬 수 없음 
   - 예를 들어 `e.preventDefault()`는 브라우저 탭을 닫는 것을 지연시킬 때는 효과가 없음


## 브라우저에 미처리 요청을 보존하도록 지시하기

- 미처리 HTTP 요청을 *보존*할 수 있는 옵션이 있고
- 대부분의 브라우저에 내장되어 있으며 사용자 경험을 손상시키지 않음

### Fetch 의 `keepalive` 플래그 사용하기

`fetch()`를 사용할 때 [keepalive](https://fetch.spec.whatwg.org/#request-keepalive-flag) 플래그가 `true`면, 해당 요청을 시작한 페이지가 종료되더라도 해당 요청이 열린 상태로 유지됨


```html
<a href="/some-other-page" id="link">Go to Page</a>

<script>
  document.getElementById('link').addEventListener('click', (e) => {
    fetch("/log", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }, 
      body: JSON.stringify({
        some: "data"
      }), 
      keepalive: true
    });
  });
</script>
```

- 일반적으로 사용되는 브라우저 API의 일부인 경우 이 방식으로 쉽게 해결 가능
- 그러나 더 단순한 인터페이스를 가진 더 집중적인 옵션을 찾고 있다면, 브라우저 지원을 받는 다른 방법도 있음

### `Navigator.sendBeacon()` 사용하기

- `Navigator.sendBeacon()` 함수는 단방향 요청을 전송하기 위해 사용 가능 ([beacons](https://w3c.github.io/beacon/#sec-processing-model)).

```js
navigator.sendBeacon('/log', JSON.stringify({
  some: "data"
}));
```

- 하지만 커스텀 헤더 불가능
- 그래서 데이터를 “application/json” 로 전송하려면 `Blob`을 사용해애함

```html
<a href="/some-other-page" id="link">Go to Page</a>

<script>
  document.getElementById('link').addEventListener('click', (e) => {
    const blob = new Blob([JSON.stringify({ some: "data" })], { type: 'application/json; charset=UTF-8' });
    navigator.sendBeacon('/log', blob);
  });
</script>
```

- `fetch()` 보다 나은 점: 비콘은 낮은 우선순위로 전송

`keepalive` 가 있는 `fetch()`와 `sendBeacon()`이 동시에 사용될 때 네트워크 탭

![image](https://github.com/10000-Bagger/free-topic-study/assets/80238096/5bc572be-97bc-4f70-98a4-8e6353a26ca5)


-  `fetch()`는 “High” 우선 순위를 받는 반면,
-  비콘은(위에서 “ping” 유형으로 표시됨)은 “Lowest” 우선 순위를 가진다.

> [Beacon 스펙](https://www.w3.org/TR/beacon/) 내용
>
> 이 스펙은 다음 인터페이스를 정의합니다 […] 시간적으로 중요한 다른 작업과 리소스 경합을 최소화하면서 요청이 계속 처리되고 대상으로 전달되도록 보장합니다.
다른 말로하면, `sendBeacon()` 은 그 요청이 애플리케이션에 중요한 것들과 사용자 경험에 관여하지 않도록 합니다.

## `ping` 속성에 대한 훌륭한 언급

- 점점 더 많은 브라우저들이 [ping 속성](https://css-tricks.com/the-ping-attribute-on-anchor-links/)을 지원

```html
<a href="http://localhost:3000/other" ping="http://localhost:3000/log">
  Go to Other Page
</a>
```
이 요청 헤더에는 링크가 클릭된 페이지(`ping-from`)와 해당 링크의 `href` 값(`ping-to`)이 포함됩니다: 

```js
headers: {
  'ping-from': 'http://localhost:3000/',
  'ping-to': 'http://localhost:3000/other'
  'content-type': 'text/ping'
  // ...다른 헤더들
},
```

이는 비콘 전송과 기술적으로 유사하지만 제한 있음

1. **링크에서만 사용할 수 있도록 엄격하게 제한**
   - 버튼클릭이나 양식 제출과 같은 다른 상호작용과 관련된 데이터를 추적해야 하는 경우 사용할 수 없습니다.

2. **브라우저 지원이 나쁘지는 않지만, [아주 좋지는 않습니다](https://caniuse.com/ping)**.
   - Firefox 미지원

3. **요청과 함께 커스텀 데이터를 보낼수 없음** 

- 모든 것을 고려해 볼 때, `ping` 은 간단한 요청으로 충분하고 커스텀 JavaScript 를 작성하지 않으려는 경우 좋은 방법
- 하지만 더 중요한 것을 보내야한다면, 가장 좋은 방법은 아닐 수 있음

## 그래서 어떤것을 사용해야 할까요?

- `keepalive`와 함께 `fetch`를 사용하거나 `sendBeacon()`을 사용하여 마지막 요청을 전송하는 것에는 분명한 트레이드오프가 있음

### 아래와 같은 경우에는 `fetch()` + `keepalive` 를 사용하는 것이 좋습니다.

- 요청과 함께 커스텀 헤더를 쉽게 전달
- `POST` 가 아닌 `GET` 요청
- 예전 브라우저(IE 같은)를 지원하고 있으며 이미 `fetch` 폴리필이 로드된 경우

### 하지만 아래의 경우에는 `sendBeacon()`이 더 좋은 선택일 수 있습니다.

- 커스텀이 많이 필요하지 않은 간단한 서비스 요청
- 깔끔하고 우아한 API 를 선호
- 요청이 애플리케이션에서 발송되는 다른 높은 우선순위의 요청과 경쟁하지 않도록 보장

- 참고자료
  - [Reliably Send an HTTP Request as a User Leaves a Page](https://css-tricks.com/send-an-http-request-on-page-exit/)
