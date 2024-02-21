# 재사용성이 높은 컴포넌트 만들기

### 공부하게 된 배경

`Clean Code`라는 책을 읽으면서 내가 과연 장인 정신을 가지고 반디부디를 개발했을까 고민하게 되었습니다. 이후 목표 수정 기능을 개발하려고 했는데, 입맛이 뚝 떨어지는 코드를 보게 되어 잠시 고민해 본 결과... 지금이라도 장인 정신을 발휘하여 조금씩 리팩토링을 해보자고 판단했습니다.

반디부디에 여러 기능이 추가되면서 아래와 같은 문제가 발생했습니다.

1. atom component에 재사용성이 떨어지는 코드가 덕지덕지 붙어 있는 문제
2. 한 feature에서만 사용하려고 만든 컴포넌트를 사방팔방에서 사용하고 있는 문제

위 문제로 인해서 작은 변경 사항 하나를 적용할 때마다 side effect 발생 위험이 커지고, 재사용성이 떨어져서 새로운 기능에 사용될 수 없는 상황…

이왕 리팩토링하는 김에 `재사용성이 높은 컴포넌트 만들기`에 대해 찾아보았습니다.

## 재사용성이 높은 컴포넌트

**Advantages of using highly reusable components:**

- reduce code duplication
- improve consistency
- speed up the development process

재사용성이 높은 컴포넌트는 중복된 코드를 줄여주고, 일관성 있는 뷰를 만들어주고, 생산성을 극대화해 주는 데 큰 도움이 된다.

그러나, 이런 컴포넌트를 만들기 위해선 많은 고민이 필요하다. 왜냐하면 컴포넌트가 재사용성이 높아질수록 더 다양한 상황에서 사용될 수 있기 때문이다. 따라서 재사용성이 높은 컴포넌트를 만들 때는 여러 사용성에 유연하게 대처할 수 있게 개발되어야 하며, 그 방법의 하나로 컴포넌트를 “추상적으로” 만드는 방법이 있다.

### 추상성이 높은 컴포넌트의 특징

- 하나의 역할만 담당 (단일 책임 원칙)
- 같은 props가 들어오면 항상 같은 결과를 렌더링 (변경에 따른 Side Effect가 없거나 적어야 함)
- 네이밍에 여러 문맥이 포함되지 않음 (예: BankAccountDropdownList (x), DropdownList (o) )

## 재사용성이 높은 컴포넌트 만들기: 문제 분석

반디부디 앱에 있는 안 좋은 예시:

```Typescript
// src/features/goal/components/new/TextInput.tsx
import type { ChangeEvent, ChangeEventHandler } from 'react';

import { Input, Typography } from '@/components';
import { Textarea } from '@/components/atoms/textarea';

type lineType = 'single' | 'multi';

interface TextInputProps {
  labelName?: string;
  value?: string;
  type?: lineType;
  height?: string;
  maxLength: number;
  placeholder: string;
  onChange?: (value: string) => void;
}

export const TextInput = ({
  labelName = '',
  value = '',
  type = 'single',
  height = '140px',
  maxLength,
  placeholder,
  onChange,
}: TextInputProps) => {
  const handleChangeInput = (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (event.target.value.length > maxLength) {
      event.target.value = event.target.value.slice(0, maxLength);
    }
    onChange && onChange(event.target.value);
  };

  return (
    <div className="flex flex-col gap-5xs">
      <div className="flex justify-between items-center">
        <Typography type="title3" className="text-gray-50">
          {labelName}
        </Typography>
        <div className="flex">
          <Typography type="title5" className="text-gray-40">
            {value.length}
          </Typography>
          <Typography type="title5" className="text-gray-30">{`/${maxLength}`}</Typography>
        </div>
      </div>
      {type === 'single' ? (
        <Input type="text" value={value} placeholder={placeholder} onChange={handleChangeInput} />
      ) : (
        <Textarea
          style={{ height }}
          placeholder={placeholder}
          onChange={handleChangeInput as ChangeEventHandler<HTMLTextAreaElement>}
        />
      )}
    </div>
  );
};
```

위 코드는 여러 문제점을 가지고 있다.

- 파일이 `/features/goal/components/new/` 경로에 위치해 있는데, 이 컴포넌트는 생성, 수정 시 모두 사용되고 있다.
- type에 따라 출력되는 컴포넌트가 달라지기 때문에 단일 책임 원칙을 위반한다.
- Wrapping 컴포넌트의 props를 확장하지 않아 attribute의 이름, 타입 등 통일된 컨벤션을 지키지 않고 있다.
- onChange 함수를 내부에서 변환하고 있어 재사용성이 떨어진다.

이런 문제점을 하나씩 해결해 가면서 재사용성이 높은 컴포넌트를 만들어보자.

## 재사용성이 높은 컴포넌트 만들기: 문제 해결

### 정리, 정돈

우선 Clean Code에서 배운 정리, 정돈 원칙을 적용해 보았다.

정리. 파일 이름은 "첫 아이의 이름 짓듯이" 장인 정신을 발휘해서 짓는다. 이 컴포넌트는 `TextInput`이라는 이름으로 불렸지만, feature에 소속되어 react-hook-form과 함께 사용된다. 또한 컴포넌트에 input만 있는 것이 아닌 해당 필드를 구성하는 컴포넌트들을 포함하고 있다. <br />
따라서 한 필드를 구성하기 위한 컴포넌트를 담아내고 react-hook-form과 평생 함께하라는 마음을 담아, React-Hook-Form Text Field. `RHFTextField.tsx`로 변경하였다.

정돈. "모든 악을 퇴치할 치료약" 장인 정신을 발휘해서 코드를 정돈한다. 물건마다 모두 제 자리가 있지만, 이 컴포넌트는 본인이 있어야 할 자리가 아닌 곳에서 사용되고 있었다. 따라서 아래와 같이 react-hook-form의 TextField 역할에 맞는 자리를 마련해 드렸다.

변경 후:

```typescript
// src/components/molecules/reactHookForm/RHFTextField.tsx
```

### Wrapping 컴포넌트의 props 확장

이 컴포넌트는 html의 input tag를 사용하기 위한 컴포넌트이다. 하지만 불필요하게 속성값들을 props로 하나씩 전달하고 있고 일반적인 naming convention을 지키고 있지 않아 재사용성이 떨어진다. 따라서 아래와 같이 `InputHTMLAttributes<HTMLInputElement>`를 확장하여 컴포넌트의 추상성과 재사용성을 높였다.

변경 후:

```typescript
export interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  name: string;
  label?: string;
  helperText?: string;
}
```

> **참고**: HTMLAttributes<T>

- HTMLAttributes<T> 는 Element 타입을 받을 수 있는 generic 인자를 받으며, 해당 Element 가 가질 수 있는 속성들을 반환한다. 아래와 같은 타입들의 조합으로 만들어진다.
  - Element 들이 공통적으로 가지는 속성들
  - 접근성을 위한 ARIA 속성들
  - generic 인자로 받은 Element 자신의 속성들

### 단일 책임 원칙 및 추상적인 이벤트 핸들러 적용

이 컴포넌트는 단일 책임 원칙을 위반하고 있다. 또한, onChange 함수를 내부에서 변환하고 있어 재사용성이 떨어진다. 따라서 Input과 Textarea를 분리하여 단일 책임 원칙을 지키고, react-hook-form에서 생성해 주는 attribute와 이벤트 핸들러를 그대로 사용하는 방식으로 변경하였다.

변경 후:

```typescript
export const RHFTextField = ({
  name,
  label,
  type,
  helperText,
  maxLength,
}: TextFieldProps) => {
  /**
   * react-hook-form에서 제공하는 컴포넌트를 사용하여 form 값을 따로 전달 받아 처리하는 로직을 제거함.
   * 이로 인해 이 컴포넌트에서 rhf에 필요한 모든 기능을 수행할 수 있게 되었다.
   */
  const { control } = useFormContext();

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <div className='flex flex-col gap-5xs'>
          {label && (
            <div className='flex justify-between items-center'>
              <Typography type='title3' className='text-gray-50'>
                {label}
              </Typography>
              {maxLength && (
                <div className='flex'>
                  <Typography type='title5' className='text-gray-40'>
                    {field.value?.length}
                  </Typography>
                  <Typography
                    type='title5'
                    className='text-gray-30'
                  >{`/${maxLength}`}</Typography>
                </div>
              )}
            </div>
          )}

          {/* 단일 책임 원칙에 따라 이 molecule에서는 Input 역할만 수행하도록 변경 */}
          <Input
            {...field}
            type={type}
            value={type === 'number' && field.value === 0 ? '' : field.value}
            onChange={(event) => {
              if (type === 'number') {
                field.onChange(Number(event.target.value));
              } else {
                field.onChange(event.target.value);
              }
            }}
          />

          {helperText && (
            <div className='px-5xs'>
              <Typography type='body3' className='text-gray-40'>
                {helperText}
              </Typography>
            </div>
          )}
        </div>
      )}
    />
  );
};
```

## 정리

위와 같은 과정을 통해서 컴포넌트의 재사용성을 높이는 과정을 수행해 보았다. 문제점을 하나씩 수정해 나가면서 컴포넌트가 다양한 상황을 컨트롤할 수 있게 되었고, 변경에 따른 Side Effect 발생 가능성을 줄일 수 있었다.

코드는 영원히 미완성이라 끝없는 재작업이 필요하며 포기할 때에만 끝난다고 한다. 위 방법이 최선이라고는 할 수 없겠지만, 장인 정신을 발휘하여 지속적해서 재사용성이 높은 컴포넌트를 만들어 나가는 노력을 해야겠다.

## References

**How to Build Reusable Components Using React**: https://buttercms.com/blog/building-reusable-components-using-react/

**제목은... 재사용성이 높은 컴포넌트 만들기라고 하겠습니다. 근데 이제 타입스크립트를 곁들인**: https://www.pumpkiinbell.com/blog/react/reusable-components
