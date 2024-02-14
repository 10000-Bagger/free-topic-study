# FSM and XState

### keywords:

Finite State Machine, XState

### 요약:

특정한 상태들에 따라 동작을 달리해야 하는 경우, 상태의 개수에 따라 복잡도가 아주 많이 증가하게 된다. FSM를 사용하면 제한된 구조와 몇 가지 제약으로 복잡하게 얽힌 코드를 직관적으로 정리할 수 있다. XState는 이러한 FSM을 더 쉽게 사용할 수 있도록 도와주는 JavaScript와 TypeScript 기반 라이브러리이다.

## Finite State Machine (유한 상태 기계):

> A finite state machine is a mathematical model of computation that describes the behavior of a system that can be in only one state at any given time.

컴퓨터의 수학적 모델의 일종. 컴퓨터 내에 `유한한 상태`를 가지는 기계가 있다고 가정하고, 컴퓨터는 오로지 `하나의 상태만`으로 있을 수 있으며, 상태별 동작과 상태끼리의 `전이에 대한 내용`을 설계하는 방식. (순서도와 비슷한 개념)

### 종류:

- Moore FSM: 상태(state)와 입력에 따라 순서가 결정됨. 시스템이 복잡해질수록 적합.
- Mealy FSM: Only 상태에 따라 순서가 결정됨. 상태가 간단한 경우 접합.

### 예시:

![한 종류(VALID / INVALID)의 상태에 대한 FSM](/hong/img/two-states-FMS.png) <br/>
_한 종류(VALID / INVALID)의 상태에 대한 FSM_

![세 종류(VALID / INVALID, ENABLED / DISABLED, CHANGED / UNCHANGED) 상태에 대한 FSM](/hong/img/eight-states-FMS.png) <br/>
_세 종류(VALID / INVALID, ENABLED / DISABLED, CHANGED / UNCHANGED) 상태에 대한 FSM_

위 사진에서 보다시피 상태의 종류가 추가됨에 따라 관리해야 하는 상태의 총수가 2배씩 증가하게 된다.

예를 들어, 조이스틱으로 움직이는 게임을 만든다고 생각해 보자. 조이스틱의 버튼에 따라 캐릭터의 동작이 달라져야 하며, 조이스틱의 버튼은 A, B가 있다고 가정하자. 이때, `A 버튼`을 누르면 캐릭터가 `점프`를 하고, `B 버튼`을 누르면 캐릭터가 `공격`을 한다고 할 때, 이를 if 문을 사용해서 코드로 구현한다면 아래와 같은 코드가 될 것이다.

```javascript
const isJumping = false;

function handleInput(button) {
  if (button === 'AButton') {
    jump();
  } else if (button === 'BButton') {
    attck();
  }
}
```

그런데, 만약에 캐릭터가 점프(A 버튼)를 하는 중에 B 버튼을 누르면 어떻게 될까? 이 경우, 캐릭터는 `날아 차기`를 해야 하고 날아 차기를 하는 중에는 `다시 점프나, 공격이 안된다`고 정의한다면, 아래와 같이 추가적인 상태에 대한 처리 로직이 들어가게 된다.

```javascript
const isJumping = false;
const isJumpAttack = false;

function handleInput(button) {
  if (button === 'AButton') {
    if (!isJumpAttack) {
      isJumping = true;
      jump();
    }
  } else if (button === 'BButton' && !isJumpAttack) {
    if (isJumping) {
      isJumping = false;
      isJumpAttack = true;
      jumpAttack();
    } else {
      attck();
    }
  }
}
```

이렇게 상태가 두 가지만 되어도 코드가 복잡해지고, 상태가 추가될수록 코드의 복잡도는 기하급수적으로 증가하게 된다. 이 상태를 FMS 방식으로 정의하면 아래와 같이 직관적으로 정의할 수 있다.

```javascript
const State = {
  STANDING: 0,
  JUMP: 1,
  JUMP_ATTCK: 2,
};

let currentState = State.STANDING;

function handleInput(button) {
  switch (currentState) {
    // 서있는 상태에서 가능한 동작 정의
    case State.STANDING:
      if (input === 'AButton') {
        currentState = State.JUMPING;
        jump();
      } else if (input === 'BButton') {
        attck();
      }
      break;
    // 점프 중인 상태에서 가능한 동작 정의
    case State.JUMPING:
      if (input === 'BButton') {
        currentState = State.JUMP_ATTACK;
        jumpAttack();
      }
      break;
  }
}
```

이렇게 FSM를 사용하면 제한된 구조와 몇 가지 제약으로 복잡하게 얽힌 코드를 직관적으로 정리할 수 있다.

FSM을 사용할 때는 아래의 5가지 요소를 고려해야 한다.

1. **A finite number of states**: 상태의 개수가 유한해야 한다.
2. **A finite number of events**: 이벤트의 개수가 유한해야 한다.
3. **An initial state**: 초기 상태가 정의되어 있어야 한다.
4. **A transition function that determines the next state given the current state and event**: 현재 상태와 이벤트에 따라 다음 상태로 전이되는 함수가 있어야 한다.
5. **A (possibly empty) set of final states**: 최종 상태가 정의되어 있어야 한다.

XState는 이러한 고려 사항을 충족시켜 줄 뿐만 아니라 복잡한 상태의 정의와 관리를 도와주는 라이브러리이다.

## XState

> XState is a state management and orchestration solution for JavaScript and TypeScript apps. It has zero dependencies, and is useful for frontend and backend application logic.

**너무 양이 방대하여.. 여기서 한번 끊을게요.. 흑.. TO BE CONTINUED...**

## references:

**What Is a Finite State Machine (FSM)? Meaning, Working, and Examples:** https://www.spiceworks.com/tech/tech-general/articles/what-is-fsm/

**Finite State Machines**: https://xstate.js.org/docs/about/concepts.html#finite-state-machines

**State Machine: State Explosion**: https://statecharts.dev/state-machine-state-explosion.html

**자바스크립트로 만든 유한 상태 기계 XState:** https://fe-developers.kakaoent.com/2022/220922-make-cart-with-xstate/
