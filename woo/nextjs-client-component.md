# Rendering - Client Components
- 요청 시점에 Client에서 렌더링이 되는 interactive UI를 제공한다.
- Next.js에서 Client Rendering은 선택 사항이다.
- 때문에 Client Component를 사용을 위해서는 명시적으로 지정을 해줘야 한다.

## Client Rendering의 장점
- interactivity: state, effects, event listeners를 활용해 즉각적으로 변화를 UI에 반영할 수 있다.
- browser APIs: browser APIs를 이용할 수 있다.

## 사용법
```
'use client'
 
import { useState } from 'react'
 
export default function Counter() {
  const [count, setCount] = useState(0)
 
  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>Click me</button>
    </div>
  )
}
```
- 파일 상단에 'use client' 지시어를 추가하면 된다.
- child component를 포함하여 해당 파일에 import된 모든 모듈들은 client bundle의 일부로 인식된다.


### Client Component의 Rerendering 방식
- client component는 요청이 full page load(초기 방문 혹은 새로고침에 의한 reload)인지 subsequent navigation인지에 따라 렌더링 방식이 다르다
### Full page load
-  React API's를 사용하여 client/server component 모두를 서버에서 static HTML preview를 렌더링한다.
- 이러한 방식 덕분에 초기 방문 시에 client가 client component의 JS 번들을 download, parse, execute하며 대기할 필요가 없어진다.
- Server의 작업 순서
    1. server component를 RSC Payload 데이터 형식으로 렌더링한다.
    2. RSC Payload와 client component JS 명령어를 활용해 HTML을 렌더링한다.
- 이후 Client 작업 순서
    1. HTML은 즉각적인 preview를 제공한다(non-interactive)
    2. RSC Payload를 활용해 client / server Component tree를 재구성하고 DOM을 업데이트 한다.
    3. JS 명령어를 활용해 client component들을 hydrate하고 client component들을 interactive하게 만든다.

### Subsequent Navigations
- server 렌더링 없이 client에서 렌더링 된다.