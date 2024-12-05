# React Internal
## breakpoint을 사용하여 React 내부를 디버깅하는 방법
### 1. breakpoint 설정하기
디버깅할 코드는 아래와 같습니다.
<img width="804" alt="image" src="https://github.com/minkyung00/react-internals-depp-dive/assets/80238096/22277259-fa65-48cf-bf8a-a7515184d3d0">

React는 UI 라이브러리이기 때문에, 가장 중요한 단계 중 하나는 DOM이 조작된 코드를 찾은 다음 콜스택을 읽어 무슨 일이 일어나고 있는지 파악하는 것입니다. 
여기서는 아래와 같이 DOM 컨테이너에 DOM breakpoint를 만들면 됩니다.
![image](https://github.com/minkyung00/react-internals-depp-dive/assets/80238096/f9c09917-6e6f-4f86-8db1-5459c62ef126)

### 2.1 컴포넌트 렌더링 시, 첫번째 일시 정지
![image](https://github.com/minkyung00/react-internals-depp-dive/assets/80238096/9a5de8c2-a3da-42c9-b42f-ba470c015876)
다음은 콜스택에서 호출 순서대로 나열된 중요한 함수들입니다.
1. `ReactDOMRoot.render()` -> 우리가 작성하는 사용자 측 코드로, 먼저 `createRoot()`를 호출한 다음 `render()`를 호출합니다.
2. `scheduleUpdateOnFiber()` -> React에게 렌더링할 위치를 알려주는데, 초기 마운트에는 이전 버전이 없으므로 루트에서 호출됩니다.
3. `ensureRootIsScheduled()` -> 이 중요한 호출은 `performConcurrnetWorkOnRoot()`가 스케줄 되도록 "보장"합니다.
4. `scheduledCallback()` -> 스크린샷을 보면 React 스케줄러의 일부인 actual scheduling이 `postMessage()`에 의해 비동기화되는 것을 알 수 있습니다.
5. `workLoop()` -> 어떻게 React 스케줄러가 태스크를 처리하는 방식입니다.
6. `performConcurrentWorkOnRoot()` -> 이제 스케줄된 태스크들이 작동하고, 컴포넌트들이 실제로 렌더링됩니다.

이를 통해 React가 실제로 렌더링을 수행하는 방식에 대한 몇 가지 단서를 얻을 수 있습니다.

### 2.2 DOM 조작 시, 두번째 일시 정지
![image](https://github.com/minkyung00/react-internals-depp-dive/assets/80238096/1df86c45-f4d6-4ec9-a3b9-3bfb1faf12d3)
UI 라이브러리로서 목표는 DOM 업데이트를 관리하는 것입니다. 실제로 위의 "렌더링 단계" 다음에 "커밋 단계"가 있습니다.
1. `commitRoot()` -> 이전 렌더링 단계에서 파생된 필수 DOM 업데이트를 커밋하고, 물론 이펙트 처리와 같은 더 많은 작업을 수행합니다.
2. `commitMutationEffect()` -> 호스트 DOM의 실제 수정
3. 

### 2.3 이펙트 실행 시, 세번째 일시 정지
![image](https://github.com/minkyung00/react-internals-depp-dive/assets/80238096/1fc2d5a6-6f00-44d4-98b2-ca437af4f4ac)
이제 우리는 `useEffect()` 호출에서 일시 정지되는 것을 볼 수 있습니다.
1. `flushPassiveEffects()` -> `useEffect()`에 의해 생성된 모든 패시브 효과를 실행시킵니다.

또한 `postMessage()`에 의해 비동기화되어 즉시 실행되지 않고 스케줄링되어 있다는 것을 알 수 있습니다. `flushPassiveEffects()`에 중단점을 추가하면 이 중단점이 `commitRoot()` 내부에 있다는 것을 쉽게 알 수 있습니다.

### 2.4 컴포넌트를 렌더링할 때 다시 일시 정지
![image](https://github.com/minkyung00/react-internals-depp-dive/assets/80238096/b53b4c2d-45ff-4e2e-83b6-39a03122dc03)
`useEffect()`에서 `setState()`를 호출하여 리렌더링을 발생시키는데, 호출 스택을 보면 전체 리렌더링이 첫번째 중단점 일시 정지와 매우 유사하다는 것을 알 수 있습니다. 다만, `performConcurrnetWorkOnRoot()` 내부에서 `mountIndeterminateComponent()`가 아닌 `updateFunctionComponent()`를 호출한다는 점만 다릅니다.

<br />

React 소스 코드에서, `mount()`는 첫번째 렌더링을 의미하는데, 초기 렌더링에는 차이점을 비교할 이전 버전이 없기 때문입니다.

### 3. React 내부 개요
실제로 위의 스크린샷들은 이미 React 내부의 기본을 다루고 있습니다. 개괄적으로 너무 자세한 내용은 다루지 않겠지만, 이미 세부적인 내용을 파악했기 때문에 아래와 같이 React 내부를 4단계로 나누어 살펴보겠습니다.
![image](https://github.com/minkyung00/react-internals-depp-dive/assets/80238096/3298616f-0608-4ef6-88f5-67de5c68e7fa)

#### 3.1 Trigger
모든 작업이 여기서 시작되기 때문에 "Trigger"라는 이름을 붙여습니다. 초기 마운트든 상태 훅으로 인한 재렌더링이든, 이 단계에서는 앱의 어떤 부분을 렌더링(`scheduleUpdateOnFiber()`)해야 하는지, 어떻게 렌더링해야 하는지를 React 런타임에 알려줍니다.

<br />

이 단계는 "태스크 생성"이라고 생각할 수 있으며, `ensureRootIsScheduled()`는 이러한 태스크를 생성하는 마지막 단계이고, 이후 `scheduleCallback()`에 의해 태스크가 스케줄러로 전송됩니다.

<br />

관련 주제로, 아래를 참조할 수 있습니다:
1. [React에서 useState()는 내부적으로 어떻게 작동하나요?](https://jser.dev/2023-06-19-how-does-usestate-work/)

#### 3.2 Schedule

React 스케줄러이고, 기본적으로 우선 순위에 의해 태스크를 수행하는 우선순위 큐입니다. <br />
`scheduleCallback()`은 렌더링이나 이펙트 실행과 같은 작업을 스케줄링하기 위해 런타임에 노출됩니다. <br />
스케줄러 내부의 `workLoop()`은 태스크가 실제로 실행되는 방식입니다. <br />

스케줄러에 대해 더 자세히 알고 싶다면, 아래를 참조할 수 있습니다:
1. [React 스케줄러는 어떻게 동작하나요?](https://jser.dev/react/2022/03/16/how-react-scheduler-works/)

#### 3.3 Render

Render는 스케줄링된 태스크(`performConcurrentWorkOnRoot()`)이고, 새로운 Fiber 트리를 계산하고 호스트 DOM에 적용하기 위해 어떤 업데이트가 필요한지 파악하는 것을 의미합니다. 

<br />

Fiber 트리는 기본적으로 앱의 현재 상태를 나타내는 내부 트리와 같은 구조이기 때문에 여기서 자세히 알 필요는 없습니다. 이전에는 가상 DOM이라고 불렀지만, 지금은 DOM에만 사용되는 것이 아니며 React 자체도 더 이상 가상 DOM이라고 부르지 않습니다.

<br />

그래서 `performConcurrentWorkOnRoot()`는 트리거 단계에서 생성되고, 스케줄러에서 우선순위를 지정한 다음, 실제로 여기서 실행됩니다. Fiber 트리를 돌아다니며 재렌더링이 필요한지 확인하고 호스트 DOM에 필요한 업데이트를 알아내는 작은 사람이 있다고 생각하면 됩니다.

<br />

concurrent 모드로 인해 "렌더링" 단계가 중단되었다가 다시 시작될 수 있으므로 복잡한 단계가 될 수 있습니다.

더 자세한 내용은 다음 에피소드를 참고하세요:
1. [React는 어떻게 Fiber 트리를 내부적으로 순회하나요?](https://jser.dev/react/2022/01/16/fiber-traversal-in-react/)
2. [React bailout은 reconciliation에서 어떻게 작동하나요?](https://jser.dev/react/2022/01/07/how-does-bailout-work/)
3. ["key"는 내부적으로 어떻게 동작하나요? React의 리스트 차이](https://jser.dev/react/2022/02/08/the-diffing-algorithm-for-array-in-react/)
4. [React 소스 코드에서 Lanes란 무엇인가요?](https://jser.dev/react/2022/03/26/lanes-in-react/)

#### 3.4 Commit
새로운 Fiber 트리가 생성된 후, 업데이트는 host DOM에 "commit" 됩니다. 물론 DOM을 조작하는 것(`commitMutationEffects()`) 외에도 여러가지가 있습니다. 예를 들어, 모든 종류의 이펙트도 여기서 처리됩니다(`flushPassiveEffects()`, `commitLayoutEffects()`)

<br />
관련 에피소드:
1. [`useLayoutEffect()`는 내부적으로 어떻게 동작할까?](https://jser.dev/react/2021/12/04/how-does-useLayoutEffect-work/)
2. [`useEffect()`는 내부적으로 어떻게 동작할까?](https://jser.dev/2023-07-08-how-does-useeffect-work/)
3. [`useTransition()`은 내부적으로 어떻게 동작할까?](https://jser.dev/2023-05-19-how-does-usetransition-work/)
4. [React에서 이펙트 훅의 라이프사이클](https://jser.dev/react/2022/01/19/lifecycle-of-effect-hook/)
