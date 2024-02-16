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

![한 종류(VALID / INVALID)의 상태에 대한 FSM](/hong/img/xstate/two-states-FMS.png) <br/>
_한 종류(VALID / INVALID)의 상태에 대한 FSM_

![세 종류(VALID / INVALID, ENABLED / DISABLED, CHANGED / UNCHANGED) 상태에 대한 FSM](/hong/img/xstate/eight-states-FMS.png) <br/>
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
  JUMPING: 1,
  ATTACKING: 2,
  JUMP_ATTCKING: 3,
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

Xstate는 JavaScript와 TypeScript 앱을 위한 상태 관리 및 조정 솔루션이다. XState는 상태를 시각화하여 관리할 수 있도록 도와주며, dependency가 없어 기존 프로젝트에 바로 적용이 가능하며, statechart를 코드로 변환해 주는 기능도 제공한다.

검색을 해보면, redux와 xstate를 비교하는 글을 확인할 수 있다.

> state + event = nextState
> 위 관점에서 redux와 xstate는 비슷하다고 볼 수 있다. 하지만, redux는 상태를 관리하는 데에 그치지만, xstate는 FSM의 요소를 고려하여 상태를 관리할 수 있을 뿐만 아니라 상태를 시각화하여 관리할 수 있도록 도와주기 때문에 활용성에 큰 차이가 있다.

### XState의 특징

- 라이브러리에서 FSM의 프레임을 잡아주고, 상태 관리 및 조정 기능을 제공한다.
- 복잡한 로직을 VISUALIZER를 통해 시각화하여 생성 및 관리할 수 있다.
- 위에서 생성한 statechart를 코드로 변환해 준다.
- 미쳤다.

## XState 사용

XState 공식 웹 페이지: https://xstate.js.org/

처음 XState 공식 페이지를 들어가면 머릿속에 물음표`?`가 떠오를 수 있다. (그냥 내가 당황했다..) 왜냐하면..

![xstate-welcome-page](/hong/img/xstate/xstate-welcome-page.png)

Welcome page가 날 환영해 주지 않는다. 그냥 바로 시작하자는 듯한 느낌이다. 그래서.. 그냥 시작해 보자.

### 설치

```bash
yarn add xstate
```

끝이다. 이제 바로 사용하면 된다. 사용 방법은 코드를 직접 구현해도 되지만, VISUALIZER를 사용하면 더 쉽고, 재밌게 상태를 관리하고 코드를 생성할 수 있으니까 VISUALIZER를 사용해 보자. (직접 구현하는 방법을 알고 싶으면 공식 문서의 [quick start 페이지](https://stately.ai/docs/quick-start)를 참고하자.)

### 사용

VISUALIZER를 사용하려면, [XState VISUALIZER](https://xstate.js.org/viz/) 페이지에 들어가면 된다.

![starting-stately-visualizer](/hong/img/xstate/starting-stately-visualizer.png)

이미 작성한 코드가 있다면, `import code`를 통해 statechart를 생성할 수 있다. template도 잘 만들어져 있어서, 사용해 보면 좋을 듯하다. 하지만, 나는 `Generate with AI`를 통해서 위에서 정의한 AB 버튼 게임을 위한 statechart를 생성해 보았다.

![ai-template-state-creation](/hong/img/xstate/xstate-ai-template-creation.png)
_위에서 정의한 AB 버튼 게임을 위한 description 작성. 과연 결과는..?_

![generated-with-ai](/hong/img/xstate/xstate-ai-tamplate-state-chart.png)
_두둥.. 모든 조건은 완벽히 커버했다._

생성된 statechart를 보면, 게임에서 정의한 상태와 이벤트에 따라 다음 상태로 전이되는 것을 시각적으로 확인할 수 있다. 이제 이 statechart를 코드로 변환해 보자.

```typescript
import { createMachine } from 'xstate';

export const machine = createMachine({
  context: {},
  id: 'gameControl',
  initial: 'Standing',
  states: {
    Standing: {
      on: {
        aButton: {
          target: 'Jumping',
          actions: {
            type: 'setJumpingTimeout',
          },
        },
        bButton: {
          target: 'Attacking',
        },
      },
      description:
        'The character is standing. This is the initial and final state.',
    },
    Jumping: {
      on: {
        bButton: {
          target: 'JumpAttacking',
        },
      },
      after: {
        '5000': {
          target: 'Standing',
        },
      },
      description: 'The character has jumped and is in the air.',
    },
    Attacking: {
      after: {
        '5000': {
          target: 'Standing',
        },
      },
      description: 'The character is performing an attack.',
    },
    JumpAttacking: {
      after: {
        '5000': {
          target: 'Standing',
        },
      },
      description: 'The character is performing an attack while jumping.',
    },
  },
}).withConfig({
  actions: {
    setJumpingTimeout: function (context, event) {
      // Add your action code here
      // ...
    },
  },
});
```

로직이 완벽하게 구현되진 않았지만(내가 생성 시 설명하지 않은 부분이긴 하다.) Boilerplate 코드로 사용되기에 충분하다. 이제 이 코드를 사용하여 게임 로직을 구현하면 된다.

### 후기

Welcome page에서부터 뭔가 자신감이 느껴진다. 한번 맛보면 헤어 나올 수 없다는 걸 아는 것 같다. 핵심 기능(무제한 AI generation, Github repo 연동, live testing & deployment 등)들을 사용하기 위해서는 부담스러운 가격(매달 33달러.. yearly 결제..)의 professional 라이센스가 필요하지만, 위의 기본적인 기능은 무료로 사용할 수 있으니, 한번 사용해 보는 것도 좋을 것 같다.

## references:

**What Is a Finite State Machine (FSM)? Meaning, Working, and Examples:** https://www.spiceworks.com/tech/tech-general/articles/what-is-fsm/

**Finite State Machines**: https://xstate.js.org/docs/about/concepts.html#finite-state-machines

**State Machine: State Explosion**: https://statecharts.dev/state-machine-state-explosion.html

**자바스크립트로 만든 유한 상태 기계 XState:** https://fe-developers.kakaoent.com/2022/220922-make-cart-with-xstate/
