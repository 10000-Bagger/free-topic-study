> 리액트 19 베타 릴리즈 기념

## 주요 변경사항
### Action

#### AS-IS
- `useState`를 이용해서 데이터 패칭 -> 응답을 상태로 저장
- 예를 들어, api 호출 후 응답을 처리하기 때문에
- 로딩 상태, 오류 상태, 낙관적 업데이트, 순차적 요청을 수동으로 처리해야함


``` js
function UpdateName({}) {
  const [name, setName] = useState("");
  const [error, setError] = useState(null);
  const [isPending, setIsPending] = useState(false);

  const handleSubmit = async () => {
    setIsPending(true);
    const error = await updateName(name);
    setIsPending(false);
    if (error) {
      setError(error);
      return;
    } 
    redirect("/path");
  };

  return (
    <div>
      <input value={name} onChange={(event) => setName(event.target.value)} />
      <button onClick={handleSubmit} disabled={isPending}>
        Update
      </button>
      {error && <p>{error}</p>}
    </div>
  );
}
```

#### TO-BE
- 리액트 19에서는 트랜지션에서 비동기 함수를 사용하여 보류 상태, 오류, 양식 및 낙관적 업데이트를 자동으로 처리하는 기능이 추가됨
- `useTransition`을 사용해서 로딩 상태를 관리할 수 있음

``` js
function UpdateName({}) {
  const [name, setName] = useState("");
  const [error, setError] = useState(null);
  const [isPending, startTransition] = useTransition();

  const handleSubmit = () => {
    /* 트랜지션을 사용해서 로딩 상태 관리 */
    startTransition(async () => {
      const error = await updateName(name);
      if (error) {
        setError(error);
        return;
      } 
      redirect("/path");
    })
  };

  return (
    <div>
      <input value={name} onChange={(event) => setName(event.target.value)} />
      <button onClick={handleSubmit} disabled={isPending}>
        Update
      </button>
      {error && <p>{error}</p>}
    </div>
  );
}
```
- 비동기 전환은 즉시 isPending 상태를 true로 설정하고 비동기 요청을 수행하며 전환 후 isPending을 false로 전환
- 이렇게 하면 데이터가 변경되는 동안 현재 ui를 유지할 수 있음

#### 비동기 전환을 사용하는 함수를 Action이라고 한다
> 액션은 자동으로 데이터 제출을 관리한다

- 로딩 상태: 요청이 시작될 때 시작되어 최종 상태가 업데이트되면 자동으로 재설정됨
- 낙관적 업데이트: 요청이 제출되는 동안 사용자에게 즉각적인 피드백을 표시할 수 있도록 새로운 `useOptimistic` 훅을 지원
- 에러 핸들링: 요청이 실패하면 에러 바운더리를 보여주며 낙관적 업데이트를 자동으로 원래 값으로 돌림

- 폼: `<form>` 요소는 `action`과 `formAction` 속성에 함수 전달을 지원
  - `action` 속성에 함수를 전달하면 기본적으로 액션이 사용되며 제출 후 폼이 자동으로 재설정

 
``` js
function ChangeName({ name, setName }) {
  const [error, submitAction, isPending] = useActionState(
    async (previousState, formData) => {
      const error = await updateName(formData.get("name"));
      if (error) {
        return error;
      }
      redirect("/path");
      return null;
    },
    null,
  );

  return (
    <form action={submitAction}>
      <input type="text" name="name" />
      <button type="submit" disabled={isPending}>Update</button>
      {error && <p>{error}</p>}
    </form>
  );
}
```
