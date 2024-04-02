# 2. Concurrent Mark & Sweep GC

이제 CMS CG에 대해 알아보자. <br>
앞서 간단하게 언급했던 바와 같이 CMS는 STW 시간을 최소화 시켰다. 그를 위해 Application이 실행중일 때도 가급적 많은 업무를 수행하는데, 문제는 마킹에 삼색 마킹을 사용한다는 점이다. <br> <br>

앞서 언급했던 것처럼 삼색 마킹은 마킹 중 새로운 객체가 만들어지는 경우 문제가 생길 수 있는데, "살아있는 객체는 절대 수집하지 않는다."는 GC의 중요한 원칙을 지키기 위해 복잡한 수행 단계를 갖는다. <br> <br>

## 2.1 CMS GC 수행 단계

1. **Inital Mark (STW 발생)**
2. Concurrent Mark (동시 마킹)
3. Concurrent Preclean (동시 사전 정리)
4. **Remark (STW 발생)**
5. Concurrent Sweep
6. Concurrent Reset

<br>

위에 표시한 것처럼 1, 4번 과정에서만 STW가 발생한다! 원래 긴 한번의 STW를 '일반적으로' 매우 짧은 두 번의 STW로 대체한 샘이라고 생각하면 된다. <br> 

### 1. Inital Mark (STW)
'초기 마킹' 단계의 목적은 해당 영역 내부에 위치한 `GC 출발점`을 얻어내는 것이다. 이는 앞서 언급됐던 GC 루트와 동등한 개념이다. **덕분에 Inital Marking 단계에서는 다른 메모리 영역을 신경 쓸 필요가 없이 GC 풀에만 집중할 수 있어서 유리하다!** 어차피 DFS 안 할거고 어차피 하위 노드 안 탈거니까 신경 안 써도 된다는 이야기인 것 같다. 

<br>

### 2. Concrruent Mark
동시 마킹 단계에선 앞서 언급된 "삼색 마킹" 알고리즘을 힙에 적용한다. GC 출발점들에서 출발해 객체들을 마킹한다. 그리고 단점 부분에서 언급한 것처럼 나중에 조정이(조정한 아님 ㅋ) 필요할 수도 있는 변경 사항들을 이때 추적한다. 

<br>

### 3. Concurrent Preclean
이 단계의 목표는 다음 단계인 Remark 단계에서의 STW를 줄이는 것이다! Remark 단계는 카드 테이블 (뭔지 까먹음)을 이용해 `Concrruent Mark` 단계 도중 발견한 '조정'사항들을 조정한다. (조정한 아님 ㅋ)



### 4. Remark (STW)
이전 단계들에서 새로 추가되거나 참조가 끊긴 객체를 확인합니다.


### 5. Concurrent Sweep
드디어 Sweep이다. 이전 단계들에서 잘 체크했으니, 접근 불가능한 객체들을 치워버린다.

### 6. Concurrent Reset

이제 Mark & Sweep은 끝났고, 다음 CMS를 위한 정리 작업을 수행한다.

ompaction을 기본적으로 제공하고 있지 않아 단편화 현상이 발생할 수 있습니다.

## 4. CMS의 장단점
원리를 설명하기에 앞서, 간단하게 장단점을 살펴보자.

### 장점
1. **Application Thread가 멈추는 시간이 짧다** -> 결국 이것 때문에 쓰는거다.

<br>

장점 벌써 끝! <br>
이제 단점을 알아보자. 

### 단점
1. **CMS는 Heap Compaction을 하지 않는다!** <br> **Old 영역은 Fragmentation이 발생할 수 있다.** 이로 인해 Full GC를 유발하는 ParallelOld GC를 사용해야 한다.
2. 단일 Full GC Cycle 시간이 더 길다.
3. CMG GC Cycle 동안 Application 처리율 감소
4. GC가 객체들을 추적해야 하기 때문에, 메모리를 더 사용함
5. GC 수행 시간에 훨씬 더 많은 CPU 시간이 필요하다.


<br> <br>

어째 단점이 더 "많다" 그럼에도 사용했던 이유는 장점이 더 "컸기" 때문이다. 결국 다 트레이드 오프고 개발자는 장단점의 많고 적음이 아니라 크고 작음을 따지면 되겠다. <br> 

그런데 단점 부분을 읽어보니 좀 이상하다. STW를 줄이려고 사용하는게 CMS인데, 오히려 시간이 더 걸릴 수도 있다니.. 대체 그 이유는 뭘까? <br> <br>


## 5. CMS 작동 원리
CMS는 강력하다. G1 GC 때문에 무시 받지만, **CMS는 대부분 Application Thread와 동시에 작동한다.** 가용스레드들은 절반으로 나뉘어 아래 역할을 수행한다. <br>

**기본적으로 가용 스레드의 절반을 동원해 GC Concurrent 단계들을 수행한다. (앞서 설명한 수행 단계에서 Concurrent가 붙은 단계들) <br> <br> 그리고 나머지 절반의 스레드들은 기존 Application 스레드의 역할인 "Java 코드의 실행"을 수행한다.** <br> <br>

아름답고 평화로운 날들이 지속되는데..

### 그런데 이때!
Java 코드를 실행하던 스레드들이 새로운 객체를 할당한다? <br>
**그래서 CMS 실행 도중 에덴 공간이 꽉 차버리게 된다??** <br> <br>

## 5.1 Concurrent Mode Failure(CMF) 문제
CMS 실행 도중 에덴 공간이 꽉 차게 되면서.. 평화는 깨지게 되고.. 에덴 공간이 꽉 찼으므로, 메모리 할당이 어려워 Application Thread는 실행이 중단된다. 그리고 **CMS 도중에 STW를 동반한 Young GC가 발생할 것이다.** <br> 문제는 이 Yong GC는 코어의 절반 밖에 사용하지 못한다는 점이다. 왜냐하면 나머지 절반은 이미 CMS가 사용중이잖아?? <br> 결국 이 Young GC는 CMS 이전에 사용하던 병렬 수집기의 Yong GC 보다도 더 오래 걸리게 된다! <br> <br>

### 여기서 끝이 아니다?
이러한 상황에서 **객체 할당률이 급증하면 어떤 일이 발생할까?** <br>

**Yong GC시 `Premature Promotion (조기 승격)`이 일어날 수 있고, Young GC 이후 승격된 객체가 너무 많아 Old 영역 공간이 부족한 사태가 벌어질 수도 있다.**

<br>


**이러한 현상을 Concurrent Mode Failure (CMF)라고 부른다.** 그리고, CMF가 발생하면 JVM은 어쩔 수 없이 ParallelOld GC를 사용해 Old 영역을 청소하는데, 이는 Full GC를 유발한다. <br> <br>

(참고 : 여기서 "Premature Promotion"이란 급격한 객체 할당으로 인해, Eden 영역에서 살아남은 객체들의 용량이 Survivor 영역보다도 커서 바로 Old 영역으로 보내지는 현상이다.) <br> 

CMF를 막으려면, Old 영역이 꽉차기 전에 CMS가 수집 사이클을 개시하는게 좋다. 디폴트로는 75%로 설정 되어 있다. <br>

### 여기서 끝이 아니다?2
**CMS의 큰 단점 중 하나는 Memory Compaction을 지원하지 않는다는 점인데,** Compaction이 없으므로 결국 Old 영역에 Fragmentation이 발생할 수 있다. 이 단편화도 CMF를 유발한다! 결국 해결책은 Compaction을 수행하는 ParallelOld GC를 사용하는 것이다. 이는 Full GC를 유발한다.. <Br> <Br>

결국 CMS 사용시 할당률이 높아지는 경우 FUll GC가 발생한다. STW를 줄이려고 사용한게 CMS인데 오히려 더 긴 시간동안 GC가 발생할 수도 있다.. <Br>
이래서 G1 G1하는거다 이제 G1 GC를 알아보자 

