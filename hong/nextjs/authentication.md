## Authentication, Authorization, Session Management Using Next.js Features

Next.js의 기능을 사용해서 일반적인 인증, 인가, 세션 관리 기능을 구현하는 방법을 소개한다.

## Authentication

> **Authentication** verifies if the user is who they say they are. It requires the user to prove their identity with something they have, such as a username and password.

사용자가 username, password 또는 다른 인증 수단을 써서 자신의 신원을 증명하는 것을 말한다. 사용자의 정보를 보호하고 권한이 없는 접근이나 악의적인 활동을 막는 등의 목적으로 사용된다.

### 인증 전략

- OAuth/OpenID Connect (OIDC): third-party 인증을 사용하여 사용자의 credentials를 직접 공유받지 않고 인증하는 방법. 예: Social Media Login 또는 Single Sign-On (SSO).

- Credentials-based login (Email + Password): 웹 애플리케이션ㅇ에서 가장 일반적으로 사용되는 인증 방법. 쉽게 개발이 가능하지만, 피싱과 같은 위협에 대한 강력한 보안 조치가 필요.

- Passwordless/Token-based authentication: email magic link나 SMS one-time code를 사용하여 비밀번호 없이 안전하게 인증하는 방법. 편리하고 안전하지만, 사용자가 이메일이나 휴대폰을 사용할 수 있어야 한다는 제약이 있음.

- Passkeys/WebAuthn: 디바이스의 내장된 인증 수단을 사용하여 내부에 저장된 개인키를 통해 사용자의 신원을 확인하는 방법. 안전하지만 새로운 기술이기 때문에 구현에 어려움이 있을 수 있음. 예: Fingerprint, Face ID, Security Key.

### Implementing Authentication

간단한 email-password 방식의 인증을 구현하는 방법을 예시로 next.js의 Authentication 기능을 사용하는 방법을 소개한다.

인증 과정은 다음과 같다.

1. 사용자는 폼에 이메일과 비밀번호를 입력한 후 제출한다.
2. 폼의 정보를 서버로 전송한다.
3. 성공적으로 정보가 확인되었다면 사용자는 성공적으로 인증되었다는 메시지를 받는다.
4. 확인에 실패했다면 에러 메시지를 받는다.

#### 로그인 페이지 예제 코드:

```typescript
// app/login/page.tsx

import { authenticate } from '@/app/lib/actions';

export default function Page() {
  return (
    <form onSubmit={authenticate}>
      <input type='email' name='email' />
      <input type='password' name='password' />
      <button type='submit'>Login</button>
    </form>
  );
}
```

#### `Authenticate` Server Action 예제 코드:

```typescript
// app/lib/actions.ts

'use server';

import { signIn } from '@/auth';

export async function authenticate(_currentState: unknown, formData: FormData) {
  try {
    await signIn('credentials', formData);
  } catch (error) {
    if (error) {
      switch (error.type) {
        case 'CredentialsSignin':
          return 'Invalid credentials';
        default:
          return 'Something went wrong';
      }
    }
    throw error;
  }
}
```


## Authorization

> **Authorization** decides what parts of the application the user is allowed to access.

사용자가 인증된 후, 인증된 사용자가 어떤 리소스에 접근할 수 있는지 여부를 결정하는 것을 말한다.

### Protecting Routes with Middleware

Next.js에서는 `Middleware`를 사용하여 특정 route에 대한 접근을 제어할 수 있다. 미들웨어는 라우트에 접근하기 전에 실행되는 함수로, 라우트에 대한 접근을 제어할 수 있다. Next.js는 Middleware를 모든 routes에 적용하고 공개 route 접근은 따로 제외하는 방식을 추천한다.

### Implementing Middleware in Next.js

Setting Up Middleware:

- Create a `middleware.ts` file in your project's root directory.
- Include logic to authorize user access, such as checking for authentication tokens.

Defining Protected Routes:

- Not all routes require authorization. Use the `matcher` option in your Middleware to specify any routes that do not require authorization checks.

Middleware Logic

- Write logic to verify if a user is authenticated. Check user roles or permissions for route authorization.

Handling Unauthorized Access:

- Redirect unauthorized users to a login or error page as appropriate.

예제 코드:

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import typoe { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
    const currentUser = request.cookies.get('currentUser')?.value;

    if (currentUser) {
        return NextResponse.redirect(new URL('/dashboard', request.url));
    };
    return NextResponse.redirect(new URL('/login', request.url));
};

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|.*\\.png$).*)'],
};

```

specific redirection이 필요한 경우, redirect 함수는 Server Components, Route Handlers, Server Actions 등에서 사용될 수 있다.

성공적으로 인증된 후에는 사용자의 역할에 따라 페이지를 관리하는 것이 중요하다. 예를 들어, 관리자는 모든 페이지에 접근할 수 있지만, 일반 사용자는 특정 페이지에만 접근할 수 있어야 한다.

이때 보안 이슈가 생길 수 있는데 Next.js에서는 상황에 따라 3가지 방법으로 데이터를 핸들링하는 것을 추천한다. ([링크 참조](https://nextjs.org/blog/security-nextjs-server-components-actions))

위 방법 중 Data Access Layer(DAL)를 사용하는 방식은 Next.js에서 신규 프로젝트를 생성할 때 추천하는 방식인데, 이는 일관된 데이터 접근과 인가 버그 최소화, 유지보수 단순화 등의 이점이 있기 때문이다.

Next.js에서 보안을 보장하기 위한 3개의 key areas:

1. **Server Actions**: Implement security checks in server-side processes, especially for sensitive operations.
2. **Route Handlers**: Manage incoming requests with security measures to ensure access is limited to authorized users.
3. **Data Access Layer**: Directly interacts with the database and is crucial for validating and authorizing data transactions. it's vital to perform critical checks within the DAL to secure data at its most crucial interaction point - access or modification.

### Protecting Server Actions

Server Actions는 서버에서 실행되는 비동기 함수로, public-facing API endpoints와 같은 보안 요구사항을 충족해야 한다.

Server Action에서 사용자의 role 체크 예제:

```typescript
// app/lib/actions.ts

export async function serverAction() {
  const session = await getSession();
  const userRole = session?.user?.role;

  // Check if user is authorized to perform the action
  if (userRole !== 'admin') {
    throw new Error('Unauthorized access');
  }

  // Proceed with the action for authorized users
  // ... implementation of the action
}
```

### Protecting Route Handlers

incoming requests를 처리하는 데 사용되며, Server Actions와 같이 특정 인증된 사용자만 사용할 수 있도록 설정할 수 있다.

Route Handler에서 사용자의 role 체크 예제:

```typescript
// app/api/route.ts

export async function GET() {
    // User authentication and role verification
    const session = await getSession();

    // Check if the user is authenticated
    if (!session) {
        return nnew Response(null, { status: 401}); // User is not authenticated
    }

    // Check if the user has the 'admin' role
    if (session.user.role !== 'admin') {
        return new Response(null, { status: 403 }); // User is authenticated but does not have the right permissions
    }

    // Data fetching for authorized users
}

```

### Authorization Using Server Components

Server Components는 back-end 리소스에 직접 접근할 수 있으며, data-heavy 작업을 최적화하고, 보안을 강화하는 데 사용할 수 있다.

가장 흔하게 사용되는 방식은 UI elements를 사용자의 역할에 따라 조건적으로 출력하는 것이다.

예제 코드:

```typescript
// app/dashboard/page.tsx

export default function Dashboard() {
  const session = await getSession();
  const userRole = session?.user?.role;

  if (userRole === 'admin') {
    return <AdminDashboard />;
  } else if (userRole === 'user') {
    return <UserDashboard />;
  } else {
    return <AccessDenied />;
  }
}
```

## Session Management

> **Session Management**: tracks the user's state (e.g. logged in) across multiple requests.

사용자의 상태를 추적하고, 사용자가 로그인한 상태인지 여부를 확인하는 것을 말한다. 사용자가 불필요한 로그인을 반복하는 것을 방지하고, 보안과 사용자 경험을 향상시킬 수 있다. Session management를 위한 가장 일반적인 방법은 `cookie-based Sessions`와 `database sessions`가 있다.

### Cookie-based Sessions ([영상 강의 링크](https://www.youtube.com/watch?v=DJvM2lSPn6w))

> Cookie-based sessions manage user data by storing encrypted session information directly in browser cookies.

사용자의 로그인이 성공적으로 수행되면 암호화된 데이터를 cookie에 저장한다. 이후의 서버 요청에는 이 cookie가 함께 전달되어 불필요하게 서버에 추가적인 요청을 보내지 않아도 된다.

(**주의 사항**) 이 방식은 사용자의 민감한 정보를 주의 깊게 암호화하지 않으면 보안 위험이 발생할 수 있음! 핵심은 cookie가 도난당하더라도 cookie 안의 정보는 읽을 수 없도록 암호화하는 것이다.

#### Cookie 적용 예제 코드:

```typescript
// app/actions.ts

import { cookies } from 'next/headers';

export async function handleLogin(sessionData) {
  const encryptedSessionData = encrypt(sessionData);
  cookies().set('session', encryptedSessionData, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: 60 * 60 * 24 * 7, // 1 week
    path: '/',
  });

  // Redirect or handle the response after setting the cookie
}
```

#### Cookie 접근 예제 코드:

```typescript
// app/page.tsx

import { cookies } from 'next/headers';

export async function getSessionData(req) {
  const encruptedSessionData = cookies(req).get('session')?.value;
  return encryptedSessionData
    ? JSON.parse(decrypt(encryptedSessionData))
    : null;
}
```

### Database Sessions

> Database session management involves storing session data on the server, with the user's browser only receiving a session ID. This ID references the session data stored server-side, without containing the data itself.

사용자의 세션 정보를 서버에 저장하고, 사용자의 브라우저는 세션 ID만을 받는다. 이 ID는 서버에 저장된 세션 데이터를 참조하며, 데이터 자체를 포함하지 않는다. 이 방식은 client-side 공격에 노출될 리스크를 줄일 수 있고, 저장할 수 있는 데이터의 크기가 더 크다는 장점이 있다. 하지만, database lookup이 많아짐에 따른 performance overhead가 발생할 수 있기 때문에 session data를 적절하게 caching 하는 것이 중요하다.

#### Database Session 적용 예제 코드:

```typescript
import db from './lib/db';

export async function createSession(user) {
  const sessionId = generateSessionId(); // Generate a unique session ID
  await db.insertSession({ sessionId, userId: user.id, createdAt: new Date() });
  return sessionId;
}
```

#### Database Session 접근 예제 코드:

```typescript
import { cookies } from 'next/headers';
import db from './lib/db';

export async function getSession() {
  const sessionId = cookies().get('sessionId')?.value;
  return sessionId ? await db.findSession(sessionId) : null;
}
```

## References

App Router > Building Your Application > Authentication: https://nextjs.org/docs/app/building-your-application/authentication

How to Think About Security in Next.js: https://nextjs.org/blog/security-nextjs-server-components-actions

Next.js App Router Authentication (Sessions, Cookies, JWTs): https://www.youtube.com/watch?v=DJvM2lSPn6w