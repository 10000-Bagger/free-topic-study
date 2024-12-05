## React Strict DOM

> 리액트를 사용하여 모든 플랫폼에서 리액트 개발 프로세스를 통합하는 것을 목표로 하는 실험 기능인 RSD에 대해 소개합니다.

### React DOM의 문제점
- React DOM은 웹 어플리케이션 최상위에서 사용할 수 있는 DOM 메서드를 제공하기 때문에 리액트 컨텍스트에서 DOM을 효율적으로 관리할 수 있음
- 하지만 React DOM은 모바일 환경에 적합하지 않음
- 대부분 React Native를 이용해서 별도의 앱을 만듦
   - 이 경우에 두가지 시스템(React DOM, RN)을 학습하고 관리해야하는 문제점이 있음
   - 또한 사용자에게 일관된 경험을 제공하기 위해 동일한 작업을 반복해야함

![image](https://github.com/10000-Bagger/free-topic-study/assets/80238096/651040bb-0a1f-4e10-85a8-30439d0a71bb)


### React Strict DOM이란?
- 리액트를 사용한 크로스 플랫폼 개발에서 개발을 가능하게 해줌
- 웹과 네이티브 모두에서 원활하게 작동하도록 설계된 API, 컴포넌트를 제공
- 즉, 개발자는 코드를 한 번만 작성하면 웹 브라우저, iOS, Android 등 모든 곳에서 실행시킬 수 있음

![image](https://github.com/10000-Bagger/free-topic-study/assets/80238096/b15bde82-57d4-43cd-b08c-16e6edeeb30c)

- RSD는 컴포넌트와 API의 동작을 표준화하면서 어플리케이션이 어디에서 실행되든 예측 가능하게 동작하도록 보장
- React DOM과 RN의 차이로 인해 크로스 플랫폼 어플리케이션에서 발생하는 버그를 개선
- RSD는 StyleX(메타에서 발표한 스타일 라이브러리)와 같이 사용하여 통합 스타일링 솔루션을 제공

``` js
import { css, html } from 'react-strict-dom';
import { LogBox } from 'react-native';
LogBox.ignoreLogs(['Failed prop type'])

const styles = css.create({
  container: {
    display: 'flex',
    flex: 1,
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    borderTopWidth: 1
  },
  h1: { padding: 10 },
  button: {
    borderRadius: 20,
    backgroundColor: '#700fad',
    padding: 10,
    paddingLeft: 50,
    paddingRight: 50
  },
  buttonText: { 
    color: 'white',
    position: 'relative',
    fontWeight: 'bold'
  }
});

export default function App() {
  return (
    <html.div style={styles.container}>
      <html.h1 style={styles.h1}>Hello World</html.h1>
      <html.button
        style={styles.button}
        onClick={() => alert('Hello World')}
      >
        <html.p
          style={styles.buttonText}
        >
          Click me
        </html.p>
      </html.button>
    </html.div>
  );
}
```

- 모든 플랫폼에서 리액트 개발 프로세스를 통합하는 것을 목표로 하는 실험 기능
