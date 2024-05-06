# Meida Query

> CSS의 일부로, **미디어 유형이나 특정 장치의 특성**에 따라 스타일을 **조건부**로 적용하는 기능

- 따라서 반응형 디자인에 매우 유용하며 다양한 디바이스에서 일관된 사용자 경험을 제공하는데 도움을 준다.

## 기본 사용법

- `@media`를 앞에 붙이고, 중괄호 안에 해당 쿼리가 참일 때 적용할 CSS를 정의하여 사용한다.

```css
@media media-type and (media-feature-rule) {
  /* CSS rules go here */
}
```

### media-type

> 브라우저에게 어떤 미디어에 대한 처리인지 알려주는 타입

- `print` : 인쇄 기기와 인쇄 미리 보기와 같은 인쇄된 디스플레이를 재현하기 위한 장치
- `screen` : `print` 유형의 기기를 제외한 모든 것들
- `all` : `print` + `screen`

### media-feature-rule

> 어떤 조건일때, 대응할지를 표기하는 규칙 혹은 조건문 형태의 표현식

- `and`와 `or`을 사용하여 여러 조건을 설정할 수 있다. (논리곱)
- `not`을 이용하여 `!`처럼 해당 조건의 부정을 설정할 수 있다. (부정 논리)
- `,`를 이용하여 여러 조건을 설정하고 이들 중 하나라도 참일 경우 적용할 CSS를 정의할 수 있다. (논리합)

```css
@media screen and (max-width: 1024px) {
  width: 24px;
  height: 24px;
}

@media screen and (min-width: 600px), screen and (orientation: landscape) {
  body {
    color: blue;
  }
}
```

## orientation

- 현재 장치가 가로 모드인지, 세로 모드인지 검사할 수 있다.
- `orientation: mode`로 사용
  - `landscape` : 가로 모드
  - `portrait` : 세로 모드

```css
@media (orientation: portrait) {
  /* 세로 모드일 때 CSS를 적용할 수 있다. */
}
```

## 포인팅 장치

### hover

- level4에서 hover 기능이 도입
- 사용자가 커서를 올릴 수 있는 능력이 있는지를 검사한다.
  - `hover` : hover를 사용할 수 있는 환경
  - `none` : hover를 사용할 수 없는 환경
  - 즉, 모바일 환경에서 hover를 사용했을 경우, 아주 잠시 동안 PC 환경에서 보이던 hover 효과가 잠시 보였다 사라지는 현상이 생기고, 이는 모바일 사용자에게 부정적인 경험을 줄 수 있다고 한다.

```css
@media (hover: hover) {
  /* hover를 사용할 수 있는 환경에서의 CSS를 적용할 수 있다. */
}
```

### pointer

- 사용자가 포인팅 장치(마우스 등)를 가지고 있는지 여부와 주요 포인팅 장치의 정확도를 확인한다.
  - `none` : 포인팅 장치가 없는 경우
  - `coarse` : 터치 스크린에서 손가락처럼 주요 포인팅 장치의 정확도가 제한되어 부정확한 포인팅 장치를 지원하는 경우
  - `fine` : 마우스, 트랙 패드처럼 정확한 주요 포인팅 장치를 지원하는 경우

```css
@media (pointer: fine) {
  /* 마우스를 사용하는 환경에서의 CSS를 적용할 수 있다. */
}
@media (pointer: coarse) {
  /* 모바일 환경과 같이 터치 스크린을 사용하는 환경에서의 CSS를 적용할 수 있다. */
}
```

## @import

- 다른 CSS 파일을 불러와 사용하기 위해 사용한다.
- 해당 쿼리가 참일 때 불러온 css 파일이 적용된다.

```css
@import url(example.css) screen and (max-width: 768px);
```
