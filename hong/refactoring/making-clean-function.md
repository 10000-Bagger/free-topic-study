# 잘 읽히고, 깔끔한 함수 만들기

`Clean Code`의 함수 챕터를 읽으면서, 지난번에 리팩토링한 컴포넌트는 아직 개선할 부분이 많다는 것을 알 수 있었다. 그래서 다시 한번 리팩토링을 해보기로 했다. 리팩토링은 아래의 원칙을 따라 진행하였다.

1. 함수는 최대한 작게 만들어라
2. 함수는 한 가지 일만 하라
3. 함수끼리의 추상화 수준을 일치시켜라
4. 서술적인 이름을 사용하라
5. 함수의 인수는 최소한으로 만들어라
6. 부수 효과를 일으키지 마라
7. 반복하지 마라

## 문제 분석

변경 전 `RHFTextField` 컴포넌트:

```typescript
export interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  name: string;
  label?: string;
  helperText?: string;
}

export const RHFTextField = ({
  name,
  label,
  type,
  helperText,
  maxLength,
}: TextFieldProps) => {
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

위 코드는 지난번에 리팩토링한 컴포넌트의 일부이다. 코드를 다시 보니 기존에 생각하지 못했던 문제점들이 보이기 시작한다.

1. 함수가 길다.
2. number 타입을 지원하기 위해 if 문이 반복적으로 사용되고 있다. 이는 한 함수에서 두 가지 일을 한다고 볼 수 있다.
3. RHFTextField가 multiline을 지원하지 않기 때문에 별도로 RHFMultilineTextField를 만들어줘야 하며, 코드는 input, textarea tag만 다르고 나머지는 모두 동일하다. 중복이 발생한다.
4. 함수의 인수가 많다.

## 문제 해결

### 1. 함수 분리하기

함수를 최대한 작게 만들어야 한다. 작을수록 좋다. 그래서 함수를 분리하기로 했다. 분리 포인트는 `한 가지 일을 독립적으로 할 수 있는가`이다. 그래서 `RHFTextField`에서 독립적으로 출력될 수 있는 `label`과 `helperText` 섹션을 별도의 함수로 분리했다.

변경 후:

```typescript
const Label = ({
  label,
  value,
  maxLength,
}: {
  label: string;
  value: string | number;
  maxLength?: number;
}) => (
  <div className='flex justify-between items-center'>
    <Typography type='title3' className='text-gray-50'>
      {label}
    </Typography>
    {maxLength && (
      <div className='flex'>
        <Typography type='title5' className='text-gray-40'>
          {String(value).length}
        </Typography>
        <Typography
          type='title5'
          className='text-gray-30'
        >{`/${maxLength}`}</Typography>
      </div>
    )}
  </div>
);

const HelperText = ({ text }: { text: string }) => (
  <div className='px-5xs'>
    <Typography type='body3' className='text-gray-40'>
      {text}
    </Typography>
  </div>
);
```

새롭게 태어난 컴포넌트들에게는 이름대로 살아가길 바라는 마음을 담아 `Label`과 `HelperText`라는 이름을 지어주었다. 보통 함수는 동사형으로 이름을 짓지만, 리엑트 컴포넌트는 함수 형태를 띄더라도 역할은 클래스와 더 가깝기 때문에 명사형으로 이름을 짓는 것이 더 적합하다고 생각했다.

### 2. 한 가지 일만 하기

함수는 한 가지 일만 해야 한다. `RHFTextField`에서 `number` 타입을 지원하면서 지속해서 `if`문을 사용하고 있다. 고민한 결과, `number` 타입을 지원하는 컴포넌트는 별도로 만들어주기로 했다. `number` 타입을 완벽히 지원하기 위해서는 다양한 예외 처리가 필요하지만, `text` 타입은 많은 예외 처리가 필요하지 않다. 현재 반디부디 서비스에서 사용되는 number 타입의 input은 생년월일 등의 특수한 경우가 많기 때문에 (우선) 반디부디의 TextField는 이름대로 `text` 타입만 지원하기로 했다. 하지만 코드는 요구사항들의 변경 등으로 계속 변화하기 때문에, 타입에 따라 별도의 함수로 분리해서 처리하는 방식으로 컴포넌트를 만들어주는 것도 나쁘지 않다고 생각한다.

변경 전:

```typescript
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
```

변경 후:

```typescript
<Input {...field} maxLength={maxLength} />
```

`number` 타입 지원이 빠짐에 따라 input의 기본 설정들을 그대로 사용할 수 있게 되었고, 그 결과 코드가 훨씬 깔끔해질 수 있었다.

### 3. 반복하지 않기

기존 `RHFTextField`는 multiline 입력 필드를 지원하지 못한다. 내부에서 사용하는 input tag가 multiline을 지원하지 못하기 때문이다. multiline을 지원하기 위해서는 textarea tag를 사용해야 한다. 하지만 이 외의 모든 기능은 같다. 그래서 tag 이외의 모든 코드가 중복된다. 고민한 결과, `MUI`의 `TextField` component를 참고하여 rows 필드를 받는 방식으로 `TextField` 출력 로직을 분리해주었다.

변경 후:

```typescript
  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <div className="flex flex-col gap-5xs">
          {label && <Label label={label} value={field.value} maxLength={maxLength} />}
          {isTextarea ? (
            <Textarea {...field} maxLength={maxLength} rows={props.rows} />
          ) : (
            <Input {...field} maxLength={maxLength} />
          )}
          {helperText && <HelperText text={helperText} />}
        </div>
      )}
    />
```

### 4. 함수의 인수를 최소한으로 만들기

이번 리팩토링에서 가장 어려웠던 부분이다. `Clean Code`에서는 함수의 인수는 최소한으로 만들어야 한다고 한다. 하지만 컴포넌트는 클래스 개념이라 인수를 최소한으로 만들기가 쉽지 않다. 출력에 필요한 값을 모두 전달해줘야 하기 때문이다. 컴포넌트를 내부에서 함수로 처리하는 방법도 고려했지만, 이는 컴포넌트의 재사용성을 떨어뜨릴 수 있고 `내려 읽기` 방식이 아닌 역순으로 함수를 정의해야 하기 때문에 코드의 가독성을 떨어뜨린다고 생각했다. 결국은 어느 정도의 균형을 찾아야 했다. 그래서 인수가 과도하게 많이 전달되기 때문에 별도 컴포넌트로 분리하지 못했던 input, textarea 출력 로직을 내부 함수로 분리하는 방식으로 최대한 인수를 줄이기 위해 노력했다.

변경 후:

```typescript
  const renderField = (field: ControllerRenderProps) => {
    if (isTextarea) {
      return <Textarea {...field} maxLength={maxLength} rows={props.rows} />;
    } else {
      return <Input {...field} maxLength={maxLength} />;
    }
  };

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <div className="flex flex-col gap-5xs">
          {label && <Label label={label} value={field.value} maxLength={maxLength} />}
          {renderField(field)}
          {helperText && <HelperText text={helperText} />}
        </div>
      )}
    />
```

## 정리

위와 같은 과정을 통해서 더 잘 읽히고, 조금 더 깔끔한 컴포넌트로 리팩토링할 수 있었다. 리팩토링을 하면서 만족스러운 결과를 만들기 참 어렵다는 것을 다시 한번 경험할 수 있었다. `Clean Code`에서 코드는 끝없는 재작업이 필요하며 개발자가 포기할 때에만 그 작업이 끝난다는 말이 더욱 와닿게 되었다.

#### 최종 리팩토링된 `RHFTextField` 컴포넌트:

```typescript
export interface TextFieldProps {
  label?: string;
  helperText?: string;
}
export interface InputTextFieldProps
  extends InputHTMLAttributes<HTMLInputElement>,
    TextFieldProps {
  name: string;
}

export interface TextareaTextFieldProps
  extends TextareaHTMLAttributes<HTMLTextAreaElement>,
    TextFieldProps {
  name: string;
}

export const RHFTextField = (
  props: InputTextFieldProps | TextareaTextFieldProps
) => {
  const { name, label, helperText, maxLength } = props;
  const { control } = useFormContext();
  const isTextarea = 'rows' in props;

  const renderField = (field: ControllerRenderProps) => {
    if (isTextarea) {
      return <Textarea {...field} maxLength={maxLength} rows={props.rows} />;
    } else {
      return <Input {...field} maxLength={maxLength} />;
    }
  };

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <div className='flex flex-col gap-5xs'>
          {label && (
            <Label label={label} value={field.value} maxLength={maxLength} />
          )}
          {renderField(field)}
          {helperText && <HelperText text={helperText} />}
        </div>
      )}
    />
  );
};
RHFTextField.displayName = 'RHFTextField';

const Label = ({
  label,
  value,
  maxLength,
}: {
  label: string;
  value: string | number;
  maxLength?: number;
}) => (
  <div className='flex justify-between items-center'>
    <Typography type='title3' className='text-gray-50'>
      {label}
    </Typography>
    {maxLength && (
      <div className='flex'>
        <Typography type='title5' className='text-gray-40'>
          {String(value).length}
        </Typography>
        <Typography
          type='title5'
          className='text-gray-30'
        >{`/${maxLength}`}</Typography>
      </div>
    )}
  </div>
);

const HelperText = ({ text }: { text: string }) => (
  <div className='px-5xs'>
    <Typography type='body3' className='text-gray-40'>
      {text}
    </Typography>
  </div>
);
```
