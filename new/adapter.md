# Adapter 패턴

> TL;DR
> 
> 서버 응답과 클라이언트 컴포넌트 데이터 구조의 불일치를 해결하기 위해 어댑터 패턴을 사용하는 방법에 대해 설명합니다.
> 
> 어댑터를 사용하여 서버 응답을 UI에 맞게 가공하는 방법을 보여주고 있다.
> 
> 또한, react-query에 어댑터 패턴을 적용하는 방법에 대해서도 소개하고 있다.


### 서버 응답과 클라이언트 컴포넌트 데이터 구조의 불일치

- UI를 표현하기 위해 서버에서 보내주는 응답을 '있는 그대로' 사용할 수 없는 경우가 있다.
- UI에 보여줘야 하는 데이터는 서버의 응답을 가공해서 보여줘야 할 수도 있다.

``` json
{
	name: 'John',
	age: 20,
	phone_number: '010-1234-5678',
	biz_number: '123-45-67890',
}
```

- 예를 들어, 전화번호의 형식이나 나이 기준으로 성인 여부를 판단해야 하는 경우가 있다.
- 이러한 경우 클라이언트 컴포넌트 내부에서 데이터를 가공하여 필요한 형식으로 변환하는 함수를 추가할 수 있다.

```jsx
import { useMemo } from 'react';

export const User = () => {
  const { data } = await fetch('/user');

  // 성인 여부 판단
  const isAdult = useMemo(() => {
    return data.age >= 20;
  }, [data.age]);

  // 전화번호 형식 변환
  const formattedPhoneNumber = useMemo(() => {
    return data.phone_number.replace(/-/g, '');
  }, [data.phone_number]);

  // 사업자 등록번호 유효성 검사
  const isValidBizNumber = useMemo(() => {
    return data.biz_number.length === 12;
  }, [data.biz_number]);

  return (
    <>
      <p>Name: {data.name}</p>
      <p>Age: {data.age}</p>
      <p>Phone Number: {formattedPhoneNumber}</p>
      <p>Business Number Valid: {isValidBizNumber ? 'Valid' : 'Invalid'}</p>
      {isAdult ? <p>Status: Adult</p> : <p>Status: Not Adult</p>}
    </>
  );
```

### 어댑터 패턴 적용하기

- 어댑터 패턴은 특정 객체를 다른 객체의 구조에 맞게 "조정"할 수 있는 디자인 패턴
    - 어댑터는 변환의 복잡성을 숨기기 위해 객체를 래핑한다.
    - 래핑된 객체는 어댑터를 인식하지 못한다.
        - 예를 들어 미터 및 킬로미터 단위로 작동하는 객체를 모든 데이터를 피트 및 마일과 같은 영국식 단위로 변환하는 어댑터로 래핑할 수 있습니다.

```jsx
export class UserAdapter {
  private user: User;

  constructor(user: User) {
    this.user = user;
  }

  get isAdult() {
    return this.user.age >= 20;
  }

  get formattedPhoneNumber() {
    return this.user.phoneNumber.replace(/-/g, '');
  }

  get isValidBizNumber() {
    return this.user.bizNumber.length === 12;
  }
}
```

- UserAdapter는 UI에 맞게 백엔드 API 응답을 "조정"한다.
- UserAdapter는 UI로 나타나는 객체와 서버 API 응답 객체에 대한 래퍼 역할을 한다.

```jsx
import { useMemo } from 'react';

export const User = () => {
  const { data } = await fetch('/user');
  
  const user = new UserAdapter(data);

  return (
    <>
      <p>Name: {data.name}</p>
      <p>Age: {data.age}</p>
      <p>Phone Number: {formattedPhoneNumber}</p>
      <p>Business Number Valid: {isValidBizNumber ? 'Valid' : 'Invalid'}</p>
      {isAdult ? <p>Status: Adult</p> : <p>Status: Not Adult</p>}
    </>
  );
```

- UserAdapter는 서버 API 응답 객체를 캐치하고 UI에 보여줘야 하는 데이터로 형식과 인터페이스를 변환한다.

### react query에 어댑터 패턴 적용하기

react query에 적용하면 select 옵션에 어댑터를 적용할 수 있다.

```jsx
export const useGetUser = () => {
	return useQuery({
		queryKey: ['user'],
		queryFn: fetchUser,
    select: (data) => new UserAdapter(data),
	})
}
```

`react-query`의 `select` 메서드를 사용하여 원본 데이터를 이 화면에 필요한 데이터로 "조정"할 수 있다.

컴포넌트 수준에서 깔끔하게 매핑을 처리할 수 있다.

---

- 어댑터 디자인 패턴은 항상 존재하고 구현 방식만 다를 뿐이다.
- 클래스가 아닌 단순한 함수인 소위 "매퍼 함수"로 구현했을 수도 있다.
- 이를 구현하는 데는 여러 가지 방법이 있다.
- 디자인 패턴은 반복되는 문제를 해결하기 위해 디자인하는 방법에 대한 아이디어를 제공할 뿐 구현을 어떻게 설계할지에 대한 제한을 두지 않는다.
