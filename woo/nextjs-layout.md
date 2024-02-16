# Layouts
```
export default function DashboardLayout({
  children, // will be a page or nested layout
}: {
  children: React.ReactNode
}) {
  return (
    <section>
      {/* Include shared UI here e.g. a header or sidebar */}
      <nav></nav>
 
      {children}
    </section>
  )
}
```
- 여러 경로의 페이지들이 공유하는 UI를 정의하는 곳이다.
- layout은 State를 보존하고 Interactive을 유지시키고, re-render를 방지한다.
- 또한 중첩 적용이 가능하다.
- layout.js(jsx, tsx) 파일을 생성하고 React Component를 export하는 방식으로 정의한다.
- 또한 React Component는 children porps(child layout 또는 page)를 받을 수 있도록 정의되어야 한다.


## Root Layout (필수)
```
// app/layout.tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {/* Layout UI */}
        <main>{children}</main>
      </body>
    </html>
  )
}
```
- app 폴더 내 최상위 위치에 존재하는 layout을 뜻한다.
- 모든 route에 적용된다.
- root layout은 필수이고 서버에서 반환된 최초의 HTML을 수정할 수 있도록 html, body 태그를 필수로 가지고 있어야 한다.

## 알아두면 좋은 것들
- root layout만 html, body 태그를 포함할 수 있다.
- 같은 폴더에 내에 layout.tsx, page.tsx가 존재해도 page에 layout이 적용된다.
- default는 Server Component / Client Component는 옵션
- `원하는 데이터를 fetch 할 수 있다.` -> Context를 활용해 모든 route에서 공유할 데이터 State로 전달에 적합할듯 (Token Payload 등)
- child 쪽에 직접적으로 데이터를 전달할 수는 없다.
- 같은 경로에서 동일한 데이터를 여러 번 fetch할 수 있으며, React는 요청의 중복을 제거한다. -> 중복될 수도 있고 중복이 제거될 수도 있다는 말인가..?
- [Route Group](https://nextjs.org/docs/app/building-your-application/routing/route-groups)을 활용해 URL Path에 영향 없이 layout을 적용할 수도 있다.