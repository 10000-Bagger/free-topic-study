<!-- 얼마 전 친구와 면접 준비를 하다가 ThreadPoolExecutor의 동작을 완전히 잘못 알고 있다는 사실을 깨달았다. <Br> -->
<!-- 간단하게 공부한 적은 있었지만, 자세한 동작에 대해 오해하고 있었다. 정확한 동작을 알고 보니 너무나도 잘 만들어진 클래스였고, 미리 알았더라면 여기저기 적용 했을 것이다. <br> -->

<!-- 하고 싶은 말들 -->
<!-- 1. ThreadPoolExecutor의 재미있는 스레드 갯수 관리 방식 알고 사용해보자. -> corePoolSize와 maximumPoolSize가 어떻게 쓰이는지? -->
<!-- 3. `Executors`의 정적 팩터리 메서드에 의해 생성될 때, 내부적으로 어떤 Blocking Queue가 쓰이고, Queue마다 어떻게 동작이 다른지 알아보자 -> 재미있는 애들 많다. -->

## ThreadPoolExecutor란?
ThreadPoolExecutor란 ExecutorService의 구현체 중 하나로, 제출된 작업들을 수행하기 위해 미리 ThreadPool을 만들어 두고, 거기에서 스레드를 가져다 위임한다. <br>
다양한 파라미터를 통해 편하게 설정할 수 있는데,
1. 기본 스레드 갯수와 최대 스레드 수
2. 스레드 Factory 
3. 작업들이 대기하는 Blocking Queue
4. Idle 상태인 스레드를 지우는 시간 
5. Reject된 작업들에 대한 핸들러  


<br>

위처럼 다양한 요소를 직접 설정할 수 있다. <br>
<!-- 그리고 매우 매우 아름다운 방법으로 스레드의 갯수를 조절하는데, 한번 알아보자. (ExecutorService 자체에 대한 설명은 생략) <br> -->

# 1. Thread 갯수는 어떻게 관리되는가?
가장 아름다운 부분 먼저 알아보자. <br>
스레드 갯수는 아래 2개의 파라미터에 의해 결정된다. 
1. `corePoolSize`
2. `maximumPoolSize`

<br>

(이 값들은 생성시 파라미터로 넣어 줄 수도 있고, set method가 제공되어서 동적으로 조절 가능하다.) <br>

`MaximumPoolSize`라는 파라미터가 있으면, 나머지 하나가 Minimum Pool Size일거 같은데 왜 "Core" Pool Size일까? <br>
Core라고 부르는데엔 이유가 있다. **ThreadPoolExectorService는 생성시 `corePoolSize` 갯수만큼 스레드를 만들어 내지 않는다.** (이름을 보면 뭔가 기본적으로 갖고 있을 것만 같다.) <br> 

**새로운 작업이 제출 되었을 때, 만약 실행중인 스레드의 갯수가 `corePoolSize` 미만이라면, 그때 `corePoolSize`가 될 때까지 스레드를 만들어 내서 작업을 할당한다!** <br>  
굳이 객체가 만들어질 때 미리 core 갯수만큼 스레드를 만들지 않고, 필요할 때 만들어 낸다! 반대로 객체가 만들어질 때 미리 corePoolSize 갯수만큼 준비했으면 좋을 것 같은 상황도 있을 것인데, `prestartCoreThread()`, `prestartAllCoreThread()`메서드를 통해 미리 스레드를 준비할 수도 있다. <br> <br>

CorePoolSize에 작업이 모두 할당된 다음 추가 요청이 들어오면, MaxSize까지 스레드를 만들어 낼 것만 같지만, 또 그렇지 않다. <br> 
**`CorePoolSize`를 초과하는 경우 일단 Blocking Queue에 작업을 추가하고, 이 Queue가 가득차게 되는 경우에만 새로운 스레드를 생성해낸다! 그 상한 값이 maximumPoolSize가 되는 것이다.** <br>
그러니까, 일단은 Core Size로 계속해서 버티면서, Blocking Queue에 작업을 밀어 넣다가, Queue까지 가득차게 되면 그때 스레드를 만들어 내는 것이다! **스레드를 미리 생성하지 않고 최대한 미루고 미룬다!** 아주 스마트 하다. <br> 
그리고 스레드가 maximumPoolSize 이상 실행중이고, 작업도 모두 할당되고, 큐도 꽉찼다면, 이후 요청은 거절된다! (이때 Reject Handler로 거절시 동작을 결정할 수 있다.) <Br> <br>

## 1.1 Blocking Queue의 사이즈는 어떻게 조절하는가?
우리는 "요청이 적은 평소 상황"과 "요청이 몰리는 상황"에 쓰일 스레드 갯수 `corePoolSize`와 `maximumPoolSize`로 지정할 수 있었다. <br>
그렇다면, 결국 Max Pool Size 갯수만큼의 스레드가 가동되는 것은 Queue가 꽉찬 이후이므로, Application이 "현재 상황이 요청이 몰리는 중인가 그냥 평소 상황인가"를 판단할 때, Queue Capacity가 기준이 될 것이다. <br>
문제는, ThreadPoolExecutor를 생성할 때 명시적인 Queue Capacity 지정이 없는데, Queue를 생성할 때 지정되기 때문이다. <br>
**문제는 Queue 구현체마다 Capacity를 설정할 수 있는 것도 있고, 없는 것도 있어서 이 사실을 모르고 막 사용한다면 영원히 corePoolSize 갯수의 스레드만 사용되거나 반대로 걸핏하면 maximumPoolSize 갯수만큼 스레드가 생성될 수 있다.** <br>
**왜냐하면 `Executors`가 static factory method로 제공해주는 ThreadPoolExecutor의 구현체들이 사용하는 Queue 중에는 Capacity가 0인 것도 있고, 무한인 것도 있기 때문이다!** <br> <br>

간단하게 Blocking Queue의 종류와 구현체들을 알아보자. 그리고 해당 구현체들을 사용하는 `Exectors`의 메서드를 알아보자.
### 1.1.1 LinkedBlockingQueue
LinkedBlockingQueue는 **무제한의 Capacity를 가진 Blocking Queue이다.**  <br>
**크기 제한이 무제한이기 때문에, 이 큐를 사용하는 ThreadPoolExecutor의 스레드는 갯수는 항상 `corePoolSize` 만큼만 생성된다! `maximumPoolSize` 설정은 사실상 무의미한 것이다!** <br> 
왜냐하면 Queue가 꽉차기 전까지는 스레드 갯수를 `corePoolSize`만큼만 유지하고, 꽉찬 이후에 maximumPoolSize까지 스레드가 만들어지는 방식이라고 설명했었는데, 이 큐가 꽉찰 일이 없기 때문이다. <br>
**그래서 해당 큐를 사용할 때는 항상 `corePoolSize` 갯수가 스레드의 최대 갯수임을 인지하고 있어야 한다.** <br> 
또한 **대기열 무한정 증가에 주의해야 한다!** 만약 작업을 처리하는 쪽에 문제가 생겨 큐에서 작업을 Consume하지 못하는 상황이 발생한다면 Queuee에 작업이 무한히 쌓여 크기가 무한히 커질 수 있다. <br> <br>

정적 메서드 `Executors.newFixedThreadPool()`과, `Executors.newSingleThreadExecutor()`를 통해 생성되는 ThreadPoolExecutor가 LinkedBlockingQueue를 사용한다! <br>  

![image](https://github.com/depromeet/amazing3-be/assets/71186266/993349bf-bb47-4914-a001-a95ace24275d)

<br>

`Executors.newSingleThreadExecutor()`인데, 이름값 대로 하나의 스레드만을 사용하기 위해 coreSize 값을 1로 두고 있다. Queue의 크기는 무한하므로 계속 1개의 스레드만 유지될 것이다. maximum이 적혀있으나 무의미하다. <br>

![image](https://github.com/depromeet/amazing3-be/assets/71186266/143d9197-7171-489e-b857-002f227c12ac)


<br>

`Executors.newFixedThreadPool(int nThread)`는 입력 받은 nThread 값을 corePoolSize와 maximumPoolSize 값으로 설정한다. <br> <br>

큐의 조작은 우리가 잘 아는 기본적인 Queue 인터페이스가 제공해주는 메서드들로 조작할 수 있다. `add`, `offer`, `remove`, `poll`은 기존 Queue에서와 똑같이 동작한다. 다만 차이라면 이 4 메서드는 Block되지 않고, Block되는 메서드들도 있다. **`put`과 `take` 메서드는 호출시 블록되어 대기한다. 이 메서드들을 작업을 동기적으로 조절하는 데에 사용할 수 있다.** 물론 무한 대기 상황에서는 제한해야 한다. (타임아웃 제공은 X)

### 1.1.2 SynchronousQueue 
**SynchronousQueue는 크키가 0인 큐로, 크기가 0이기 때문에 작업이 제출될 때마다 매번 maximumPoolSize 까지 스레드가 생성된다!** <br>
아니.. 큐의 사이즈가 0이면 그게 "자료 구조"인가? 했는데, 용도가 다 있다. <br>
SynchronousQueue는 작업 제출시 다른 스레드가 해당 작업을 소비할 때까지 제출한 스레드가 Blocking된다. 혹은 작업을 제출한 스레드가 없는데, 어떤 스레드가 소비하려 한다면, 해당 스레드는 Blocking된다. <Br> 
이렇게 Blocking되어 반대쪽에 다른 스레드가 나타나기를 기다리는 스레드들은 여러개일 수 있고, "공정성(fair)"이라는 개념에 의해 SynchronousQueue 내부의 자료구조인 Transfer Stack이나 Transfer Queue에 의해 대기된다. 공정성에 대해 간단하게만 설명하자면, 공정성 - fair가 true인 경우 Transfer Queue에 의해 작업들이 대기된다. 먼저 줄 선 사람이 먼저 작업할 수 있으니, 공정하지 않은가? 반대로 fair 값이 false인 경우엔 TransferStack에 의해 관리되는데, 늦게 들어온 스레드가 더 짧은 대기 시간을 가지니 불공평하지 않은가? <br> 
이러한 자료구조들에 의해 작업을 제출한 Thread와 소비하려는 Thread는 대기하고 하나씩 수행하게 된다. SynchronousQueue는 중재자 역활만을 할 뿐이다. (fair 값은 기본적으로 false이다.) <Br> <br>

이러한 대기로 인해 작업은 자연스럽게 작업이 "동기적으로" 수행되도록 만든다. 순서를 지켜가면서 하나씩 수행될 수 밖에 없기 떄문이다. 이래서 이름이 "SynchronousQueue"이다. <br>
정적 팩터리 메서드 `Executors.newCachedThreadPool()`를 통해 ThreadPoolExecutor를 생성하면, 내부적으로 이 큐를 사용한다. <br>
이름만 보면 단순히 동기적으로 동작하겠네~ 싶지만, 사이즈가 0인 것을 인지하고 maximumPoolSize 설정에 신경 써야 한다.

![image](https://github.com/depromeet/amazing3-be/assets/71186266/22d6d6df-a5b8-48cb-a00d-4b68c32e2356)

<br>

**보면 알겠지만 애초에 core 갯수가 0개이고, max가 Integer MAX_VALUE이다! 대놓고 요청이 들어오는 만큼 계속해서 스레드를 찍어 내겠다는 뜻이다!** <br>
newCachedThreadPool라는 메서드 이름만 보면 이런 동작이 예상가지 않을 수 있기 때문에 주의해야 한다. <br>
그럼 왜 메서드 이름이 newCachedThreadPool인가? 작업 갯수만큼 스레드는 만들어지고, 작업을 마치고 나면 KeepAliveTime 시간동안 살아있게 된다. 결국 corePoolSize가 0이므로 언젠간 사라지겠지만, 살아 있는 동안은 이들을 다시 활용할 수 있으므로 "Cached"인것 같다.

### 1.1.3 ArrayBlockingQueue 
ArrayBlockingQueue는 내부적으로 고정 크기의 배열을 사용한다! 드디어 사이즈 조절이 가능한 큐가 등장했다. <br>
큐 사이즈를 의도적으로 조절하고 싶을 때 쓸 수 있겠다! <br>
Queue 사이즈는 어떻게 설정하면 좋을까? <br>
**예상되는 "요청이 몰릴 때"와 "평소"를 통해 PoolSize를 조절했을 것이다. 이제, 처리량과 CPU 사용률, 그리고 거부되는 작업이 있어도 되는지, 절대 없어야 하는지 등을 고려하며 Queue 사이즈와 Pool의 사이즈를 조절하면 된다.**
- 작은 Queue Capacity, 큰 Pool Size -> CPU 사용률이 높아지지만, **Queue가 작아 거부되는 작업이 있을 수도 있으므로, 처리량이 감소할 수 있다.** <br> 어느 정도 작업이 실패해도 상관 없고, CPU 사용률이 더 중요하다면 큐 사이즈를 작게 설정
- 큰 Queue Capacity, 작은 Pool Size -> CPU, OS 리소스 사용량 Down, ContextSwitching 오버해드 Down, **그러나 낮은 처리량을 유발할 것이다.** <br> 최대한 core 갯수만큼의 스레드만 사용해 처리할 의도가 있다면 큐 사이즈를 풀 사이즈 보다 크게 설정

### 1.1.4 BlockingQueue들 주의점 정리

결국 정적 팩터리 메서드로 만들어내는 Executor들이 어떤 Blocking Queue를 가지고 있고, 큐에 따라 스레드 갯수가 다르게 관리될 수 있다는 점을 알아야 한다.

1. `LinkedBlockingQueue`
   - Queue 사이즈가 무한이다.
   - 따라서, 항상 corePoolSize 갯수의 스레드만 운용된다. (maximumPoolSize 값이 무의미)
   - Queue가 무한하기 때문에 작업이 무한히 쌓일 수 있다. (소비하는 쪽에서 문제가 생기는 경우)
   - `Executors.newFixedThreadPool()`와, `Executors.newSingleThreadExecutor()`에 의해 생성될 수 있음.
2. `SynchronousQueue`
   - 큐 Capacity가 0이기 때문에, 스레드가 무한정 만들어질 수 있음에 주의한다.
   - `Executors.newCachedThreadPool()`에 의해 생성될 수 있음.
3. `ArrayBlockingQueue`
   - 크기를 직접 조절할 수 있는 큐이다. Pool Size와 Queue Capacity간의 관계를 이해하고, 상황에 맞게 적절한 값을 사용해야 한다.


## 1.2 요청이 몰리는 순간이 끝나면, 그 많던 스레드들은 어떻게 될까?
만약 max pool size 갯수만큼 스레드가 만들어진 상태에서, 요청이 몰리는 시간대가 끝나고 다시 서비스가 한산해지면 어떻게 될까? 이제 그렇게 많은 스레드는 필요 없는데, 스레드를 잔뜩 만들어 두었다면 낭비일 수 밖에 없다. <br>
이때 KeepAliveTime이 쓰인다. `keepAliveTime` 옵션을 통해 간단하게 유휴 상태 스레드를 관리할 수 있다! <br>
ThreadPoolExecutor는 똑똑하게 **스레드 갯수가 `corePoolSize`값 보다 많을 때, `keepAliveTime` 보다 오랜 시간동안 동안 유휴 상태인 스레드가 있다면, 해당 스레드를 종료 시킨다.** **단, `corePoolSize` 갯수 만큼은 남겨두고 제거한다.** <br> <br>

만약 어떤 서비스가 특정 날짜나 시간대에만 요청이 몰리고 평소엔, 별로 많지 않다고 생각해보자. 그때 이 옵션들을 잘 활용할 수 있을 것이다. 
- 평소에는 몇 개의 스레드를 해당 기능을 위해 준비 할건지 -> `corePoolSize` 
- 요청이 몰릴 때는 최대 몇 개의 스레드가 처리할 것인지 -> `maximumPoolSize`
- 물론 큐에 따라 

스레드 갯수가 Core Size 갯수와 같아도 오랜 시간 유휴 상태인 스레드를 종료 시키고 싶은 경우 `allowCoreThreadTimeOut()`을 호출하라. 그러면 coreThread에도 Timeout이 적용된다. <br>
옵션 중 Executor의 정적 팩터리 메서드 `newCachedThreadPool()`를 통해 생성한다면, keepAliveTime이 60초로 설정되고, 다른 정적 메서드로 생성되는 경우 보통 제한 시간이 없으므로 신경 쓰자. (0으로 설정 되어 있는데, 이것이 제한 시간이 없는 것)

## 1.2.1 keepAliveTime의 기본 설정 값은 어떻게 되는가?
keepAliveTime의 기본 설정 값은 없다. 생성시 꼭 값을 대입해 줘야 한다. <br>
다만, Executors의 정적 팩터리 메서드를 통해 생성하는 경우 자동으로 값이 할당될 수 있으므로 주의해야 한다. <br> 
중 `newCachedThreadPool`, `newSingleThreadExecutor`를 통해 생성하는 경우엔 자동으로 값이 설정된다. <br>
`newCachedThreadPool`를 사용하는 경우, corePoolSize가 0, maximum Size가 Integer.MAX_VALUE로 설정되는데, 사실상 제한 없이 스레드를 계속 만들겠다는 것. <br>

`newSingleThreadExecutor`의 경우 core, maximum이 이름 그대로 1개이다.

<!-- # 3. BlockingQueue
작업들이 스레드에 할당되기 전에 저장되는 Queue이다. <br>
기본적으로 첫 작업 제출 때 Queue에 작업을 추가하지 않고 바로 corePoolSize 갯수만큼 스레드를 만들어 할당하므로, core 갯수가 꽉찼을 때나 처음 Queue에 작업이 쌓이게 된다. <br>
이러한 BlockingQueue는 구현체에 따라 동작이 다르다. 몇개 확인해보자.

## 3.1 구현체의 종류
1. **LinkedBlockingQueue**
   - 무제한 크기의 큐이다. 크기 제한이 무제한이기 때문에, 스레드는 `corePoolSize` 만큼만 생성되고, `maximumPoolSize` 설정은 무의미하다.
   - 대기열 무한정 증가에 주의해야 한다.
   - 기본적인 Queue가 제공해주는 메서드들로 조작할 수 있다. `add`, `offer`, `remove`, `poll`은 기존 Queue에서와 똑같이 동작하고, Block되지 않는다. **하지만, `put`과 `take` 메서드는 호출시 블록되어 대기하기 떄문에 작업을 동기적으로 조절하는 데에 사용할 수 있다.** 물론 무한 대기에는 제한해야 한다. (타임아웃 제공은 X) 
2. SynchronousQueue 
   - "동기적인 큐" 크키가 0인 큐로, 크기가 0이기 때문에 작업 추가시 새로운 스레드가 생성된다. 만약 작업 요청이 빠르다면 스레드가 무한으로 증가할 수 있다.
   - 요소 추가시 다른 스레드가 해당 작업을 꺼낼 때까지 현재 스레드는 Blocking된다. 이로써 동기적으로 수행하게 만드는 듯 하다. 
3. ArrayBlockingQueue 
   - 고정 크기의 배열을 사용한다.
   - Queue 크기와 Pool 크기 관계
     - 작은 Queue와 큰 Pool -> CPU 사용률이 높아지지만, Queue가 작아 거부되는 작업이 있어 **처리량이 감소할 수 있다.**
     - 큰 Queue와 작은 Pool -> CPU, OS 리소스 사용량 Down, ContextSwitching 오버해드 Down, **그러나 낮은 처리량 유발** 

## 3.2 Executor 정적 팩터리 메서드에 의한 설정
역시 기본 값은 없다. 꼭 지정해 줘야 한다. Executor 정적 팩터리 메서드에 의해서는 자동 설정 된다.
- newFixedThreadPool, newSingleThreadExecutor : `LinkedBlockingQueue`
- newCachedThreadPool : SynchronousQueue -->


# 2. 거절당한 작업들은 어떻게 처리될까? 
큐까지 꽉차게 되면 새로운 요청을 처리하기 위해 최대 스레드 갯수만큼의 스레드가 만들어질 수 있다. <br>
**최대 갯수만큼의 스레드가 만들어 졌고, 모두 작업이 할당됐으며, 큐까지 꽉차게 된다면 이후 요청은 거절된다!** 이때, 거절된 작업들은 어떻게 처리될까? <br>

![image](https://github.com/depromeet/amazing3-be/assets/71186266/c0314a5c-9dc6-42ce-8cbc-cea31e483547)

위 메서드는 ThreadPoolExecutor에 작업을 제출하는 execute 메서드이다. <Br>
corePoolSize만큼 스레드가 이미 있을 워커 스레드를 더는 늘릴 수 없는 경우 reject가 호출된다. <Br>
![image](https://github.com/depromeet/amazing3-be/assets/71186266/3e64d2af-49e6-4af4-9afc-acaea2e2ce67)

**reject는 RejectedExecutionHandler의 `rejectedExecution()`를 호출한다.** <br>
이는 RejectedExecutionHandler 인터페이스가 제공하는 메서드로, 정책마다 다른 구현을 가진다. <br>
제공되는 구현으로는 4가지 정책이 있다. 동작을 살펴보자.

1. AbortPolicy
2. CallerRunsPolicy
3. DiscardPolicy
4. DiscardOlestPolicy

### 2.1 AbortPolicy 정책
ThreadPoolExecutor.AbortPolicy 정책은 기본 정책이며, **더 이상 작업을 받을 수 없는 경우 예외를 발생시킨다.**

![image](https://github.com/depromeet/amazing3-be/assets/71186266/fbd9a927-fb4c-402b-8846-e9ad5efcc8f5)

위 그림의 빨간 네모칸을 보면, 간단한 실행 정보와 함께 예외를 발생시키는 것을 확인할 수 있다.


### 2.2 CallerRunsPolicy 정책
ThreadPoolExecutor.CallerRunsPolicy는 이름 그대로 Caller가 Run하는 정책이다. **즉, Executor가 종료 되지 않았더라면, execute를 호출한 스레드가 직접 요청을 수행한다!**

![image](https://github.com/depromeet/amazing3-be/assets/71186266/16792199-82f1-43d9-9ec6-aa2101aa15c2)

executor의 상태를 확인한 다음, run을 호출해서 직접 작업을 수행하는 모습을 확인할 수 있다.

### 2.3 DiscardPolicy 정책

![image](https://github.com/depromeet/amazing3-be/assets/71186266/013f00ee-ff5b-4198-822d-418b5231aa1c)

깔끔하고 귀엽다. ThreadPoolExecutor.DiscardPolicy는 작업을 버리는 정책이다. 메서드 블럭에 코드가 단 한 글자도 없다. 구현이 깔끔하고 클린 코드 그자체이다. <br>

### 2.4 DiscardOldestPolicy 정책
잔인한 정책이다. ThreadPoolExecutor.DiscardOldestPolicy는 작업 하나를 Queue에서 poll한다. **즉, 가장 오래 대기한 작업을 꺼내어 없애고, execute를 다시 호출한다.** (Executor가 종료되지 않은 경우) <Br>

![image](https://github.com/depromeet/amazing3-be/assets/71186266/10b30c58-4adf-4c2f-9582-4cae10bf259e)

너무 잔인하다. 오랜 시간을 고되게 기다려온 작업은 수행되지 못하고 poll당하고 새로운 작업을 위해 execute를 수행한다. 그래서 DiscardOldest이다. 가장 오래된 작업이 버려진다. <br>

<!-- # 3. Thread Pool Hook 메서드
ThreadPoolExecutor는 

# 4. 생명주기 -->


<!-- 

결국 여기로 귀결

protected void doExecute(Runnable task) {
    Thread thread = this.threadFactory != null ? this.threadFactory.newThread(task) : this.createThread(task);
    thread.start();
}

 -->
