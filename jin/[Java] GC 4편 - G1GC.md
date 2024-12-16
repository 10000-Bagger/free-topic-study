# Garbage First GC

# 1. Grabage First Grabage Collector란
GC는 STW 시간과 발생 횟수를 줄이는 것을 목적으로 진화해왔다. 처리량이나과 같은 요소도 매우 중요하지만, 결국 STW가 얼마나 자주 발생하고, 얼마나 오랜 시간 발생하느냐는 앱에게 어마어마한 영향을 미치는 요소이기 때문이다. <br> 
CMS GC는 Root에서 바로 참조 가능한 객체만을 1차적으로 Mark한다. 단지 이 때만 STW가 일어난다. 이렇게 마크한 객체들과 이어진 객체들을 확인하는 과정은 STW 없이 진행될 수 있다. 따라서 짧은 STW가 장점이었다. <br> <br>

그러나, Collection 과정 중 Compaction을 제공하지 않는다는 단점이 있었는데, 결국 단편화 문제를 피하려면 언젠가 Compaction 하긴 해야 할 것이다. **결국 나중에 몰아서 Comapction을 하는 Full GC 과정이 있고, 이때 STW가 매우 길게 일어난다.** (경우에 따라 기존 GC에서 발생하던 STW보다 길 수도 있다) <br> 
따라서, Compaction이 일어나는 주기와 시간을 확인하고 사용해야 한다. <br> <br>

![G1GC](https://github.com/binary-ho/TIL-public/assets/71186266/663122f2-f7e5-4a7d-b2b4-aabfe0a45727)


이러한 문제를 해결하기 위해 도입된 G1 GC는 Garbage Fist GC로, 위 바둑판 모양의 영역들 중 쓰레기로 가득찬 영역을 집중적으로 수집한다고 해서 Garbage First GC이다. (Java 9 ~ 12 Default GC) 대용량 메모리가 있는 멀티 프로세서 시스템을 위해 제작되었다고 하고, **CMS와 같이 Old Generation에서의 GC를 병렬로 작업한다!** Application Thread가 돌아가면서 GC 수행이 가능하다. (Can operate concurrently with applications threads like the CMS collector.)

<Br> 

**영억을 동일한 크기의 region으로 관리하면서 일종의 "조각 모음"을 한다. 이로써, CMS의 Compaction 부재로 인한 단편화 없어 긴 Full GC를 갖는다는 단점을 해결했다..** <br> <br>

### 간단한 특징
1. 큰 메모리를 가진 멀티 프로세서 시스템을 타겟으로 한다. (targeted for multi-processor machines with large memories)
2. STW를 최소화 한다. 아주 없애지는 못해서 실시간은 아니다.
3. 사용중인/사용중이지 않는 Region을 `Available/Unused`로 구분한다.
4. GC로 인해 멈추는 시간을 더욱 예측하기 쉽다고 한다. (Need more predictable GC pause durations.)
<!-- G1GC는 아래와 같은 상황에서 좋다.
1. Java Heap의 50% 이상이 생존 객체로 채워진 경우
2. 시간이 흐르며 객체 할당 비율과 프로모션 비율이 크게 달라지는 경우??
3. GC가 너무 오래 걸리는 경우 -->

# 2. G1GC의 영역 - Region


![G1GC](https://github.com/binary-ho/TIL-public/assets/71186266/663122f2-f7e5-4a7d-b2b4-aabfe0a45727)


기존 GC의 Young Generationd이 Eden, Serviver 1, 2로 나뉜 구조와 달리, G1GC는 **바둑판과 같은 동일한 크기의 칸들이 있고 이 칸들은 상황에 따라 Young Generation, Old Generation 등을 담당하게 된다.** <br> 

**즉, Heap의 영역을 물리적으로 구분하는 것이 아니라 논리적으로 구분한다.** 이 구분된 영역들을 region 이라고 부른다. <br>
(이 region들을 관리하기 위한 전체 heap의 5% 미만 크기의 `remember set`을 만들어서 사용한다.) <br> <br>

region을 나누는 방식만 다르고 region들 자체의 사용은 기존 GC와 비슷하다. **새로 만들어진 객체는 비어있는 영역에 할당되고, 그 영역이 Eden 영역이 된다.** <br> 
이후 꽉찬 region을 청소하는데, **살아있는 객체들을 다른 비어있는 영역으로 옮기고 꽉 찬 영역은 깨끗히 비운다.**  <br>
**일반 GC와 똑같이 Eden에서 살아남은 객체들이 옮겨진 영역을 Survivor Region으로, Servivor Region에서 살아 남은 객체들이 옮겨지는 곳을 Old Region으로 부른다!** 옮겨진 새로운 칸이 상황에 따라 Survivor, Old 영역 등이 된다. **이 과정을 "Evacuation" - "대피"라고 부르고, 이 과정에서 STW가 발생한다!!** <Br>

결론적으로 5 종류의 region이 있다.
1. Empty Region
2. Eden Region
3. Survivor Region
4. Old Region
5. Humongous Region

<br>

이러한 region의 크기와 Application에서 실제로 할당되는 객체들의 크기가 애매하게 안 맞는 경우 경우 GC가 잦아 효율이 좋지 않을 수 있다. <br> 
구체적으로는 region 크기에 비해 너무 작은 객체가 많거나, region size 반 이상 넘어가는 Humongous Object가 많으면 비효율적이다.



## 2.1 Humongous Region
그림을 잘 보면 두개의 region을 차지하는 Humongous 영역이 있는데, **하나의 region의 50% 이상의 크기를 갖는 거대한 객체가 저장되는 영역이다.** `-XX:G1HeapRegionSize`에 의한 영역 설정의 영향을 받는다. G1HeapRegionSize의 기본값은 최대 heap 사이즈의 `1/2048`이다. 즉, 2^(-11) 이다. <br>
이들은 연속된 영역을 순서대로 차지하도록 할당된다. 크기가 애매하게 남으면? -> 그냥 사용하지 않는다. <br> <br>

Humongous Object는 Full GC 중에도 옮겨지지 않는다. 그래서 region 크기의 반을 넘는 개체를 만드는 것은 위험하다. 공간이 충분한데도 애매하게 남은 "잉여 공간"들이 있어 메모리 부족 상태가 발생할 수도 있다. <br> <Br>

그렇다고 Humongous Object에 대해 아무런 처리도 하지 안흔 것은 아니다. 일단 Humongous Object가 할당되면 G1GC는 IHOP을 확인한다. 만약 IHOP이 초과된 상태인 경우 강제적으로 `young collection`을 시작한다. <br> <br>

IHOP은 로, 마킹 발동의 기준이 되는 Old Generation 크기에 대한 백분률이다 <br> 이 값은 Adaptive IHOP을 통해 G1의 통계를 계산하며 최적의 IHOP 값을 찾아내 설정된다. <br>

Adaptive IHOP 기능이 켜져 있는 경우 `-XX:InitiatingHeapOccupancyPercent`을 통해 초기 IHOP값을 지정할 수 있고, 기본값 45%이다. (아직 통계가 덜 쌓였을 때) <br>
물론 끌 수도 있다. Adaptive IHOP 옵션을 끄게 되는 경우 `XX:InitiatingHeapOccupancyPercent로 `지정한 IHOP 값을 사용한다. <Br> <br>s


# 3. G1GC Cycle
### 이 파트에 대해..
이 파트는 오라클에서 제공하는 문서 위주로 봐도 조금 헷갈리는 부분이 있다. 버전의 문제인지 내 이해력의 문제인지 정확한 정보임을 확신하기 어렵다. <br>
이 점을 감안해주길 바란다.. 

## G1GC Cycle
G1GC의 작업은 2가지 Phase로 나누어 볼 수 있다. 그리고, 두 페이즈가 번갈아가며 GC 작업을 수행한다.

![image](https://github.com/binary-ho/TIL-public/assets/71186266/6c94d6f1-90cc-4cc2-98fc-eb2f003af8e9)

<br>

1. Young Only Phase : old 객체들을 다른 공간으로 옮기는 페이즈이다.
   - `파란색` : Minor GC, Young GC (Evacuation Phase) <br> STW를 수반한다. Live Objects들은 Survivor Region으로 옮겨진다. 혹은 Old Region으로 Promotion 된다. <br> **Young GC는 여러 스레드를 사용하여 병렬로 수행되며, 크기에 따라 Region 크기를 조절하기 위해 Region이 연속되어 할당되지 않는다.** <br>
   - `주황색` : Major GC (Old GC, Concurrent Cycle) <br> **CMS GC와 같이 G1는 짧은 Old GC STW 시간을 갖는다.** 
2. Space Reclamation phase : 부여한 공간들을 회수하는 페이즈
   - `분홍색` : Mixed GC

<br>

표시된 동그라미들은 모두 STW가 수반되는 과정이고, 그 크기가 소요 시간을 의미한다.

## 3.1 Young Only Phase
### 3.1.1 Young GC (Minor GC)


![image](https://github.com/binary-ho/TIL-public/assets/71186266/dc25579d-b0f6-44bb-810f-c07a0ba07019)

일단 살아있는 Young 객체들을 하나 이상의 Survivor 영역으로 이동한다. **Aging Thrashold가 넘어서면 Old 영역으로 Promotion** <br> 
그러면 아래와 같이 진한 초록색 영역으로 이동한다. <br> 

![image](https://github.com/binary-ho/TIL-public/assets/71186266/bcde4519-40b1-4e5f-8f40-dbcf6cacfebc)


#### 이때, 모든 Application Thread 까지 멈추는 STW이 진행된다!! (중요)
#### Young GC는 병렬로 수행된다!!


`Space Reclamtaion Phase`에서 Old Generation의 점유율이 일정 threshold 값을 넘어서면 `Young Only Phase`로 전환된다. <br>
Young GC가 수행시 가장 먼저 Marking Phase가 진행된다. 그리고 도달할 수 있는 객체들에 Concurrent Mark를 진행한다. <br>


### 3.1.2 Old GC (Major GC)

**Concurrent 라고 적힌 부분은, Application Thread와 함께 병렬로 수행된다고 생각하면 된다.** <br>

![image](https://github.com/binary-ho/TIL-public/assets/71186266/e14fe0a6-8432-4ffb-9f3d-54ecf5eff93d) <br> <br>


1. `Initial-mark (STW)` : Old Generation에 참조를 가질 수 있는 Survivor 영역이나, Root를 Mark한다. **Young GC중 수행된다고 한다**
2. `Concurrent Root Region Scan` : initial-mark에서 찾아낸 Survivor Region들을 스캔해, Old Generation에 대한 래퍼런스 찾아 Mark한다. (Young GC 발생 전에 완료 되어야 한다.)
3. Concurrent Mark : 전체 Heap 영역에 있는 모든 Live 객체를 찾는다. 빈 영역도 체크한다. (Young GC에 의해 중단될 수 있다.)
4. `Remark (STW)` : Live 객체 Marking을 마무리 하는 단계이다. 비어있는 리전을 제거하거나 회수한다. 그리고 모든 Region들의 liveness를 계산한다. liveness는 살아있는 객체가 많을 수록 높다. <br> 이때, SATB라는 빠른 알고리즘을 사용한다. 이후 SATB 버퍼를 비우고, Reference Processing 동작
5. `Cleanup/Copying (STW)` : Young/Old 가리지 않고 살아있는 객체들을 "대피"시킨다. 즉, 다른 칸으로 옮기게 된다. (Evacuation)
   1. 살아있는 객체와 Free Region에 대한 계산을 수행한다. (STW) 
   2. Remember Set을 한번 갱신한다. (STW)
   3. 이후 Empty Region들을 Reset 하고, Free List에 추가한다. (Concurrent) **Spae Reclamation Phase로 들어갈지 말지 판단한다.**
   - `Copying (STW)` : 중간 중간 Live 객체들을 옮기는 과정에서 STW가 발생한다. Young GC나 Mixed GC에서 발생할 수 있다.

Cleanup/Copying 전/후는 아래와 같다.
![beforeremarkcopying](https://github.com/binary-ho/TIL-public/assets/71186266/0cacd2b0-64da-4df0-9a7c-c78cc79a1d3b)
![aftermarkcopying](https://github.com/binary-ho/TIL-public/assets/71186266/27713b7d-4dcc-4e8c-8f08-eca40ba8e95e)

## 3.2 Space Reclamtaion Phase (Mixed GC)
Young/Old Generation 전부 수집된다. Old Generation은 liveness가 가장 낮은 지역을 찾아 GC 수행된다.
만약 작업 효율이 떨어지게 되면 이 페이즈는 끝나고, 다시 `Young Only Phase`로 전환된다.

## 4. SATB란?
G1GC는 Snapshot-At-The-Beginning (SATB) 알고리즘을 사용해 Concurrent Marking 작업을 한다. <br>

SATB는 이름 그대로 **Marking을 시작한 시점의 스냅샷을 찍는다.** <br> 
이 Old Generation에 대한 스냅샷만 보고 작업하기 때문에, 
1. **이후 할당된 객체들은 암묵적으로 Live 객체로 간주해 회수 대상에서 제외한다.**
2. **스냅샷을 찍고 마킹하는 과정에서 죽은 객체도 Live하다고 체크한다.**

이러한 특성 때문에 **"보수적인" 알고리즘이라고** 부르는 것이다. <br>
**덕분에 Live 여부를 분석해야 할 객체의 양이 고정되어, 처리할 데이터 양이 변하지 않는다. 이는 Marking이 빠른 이유가 된다.** <br> 
G1은 빠른 마킹이 마킹 실행중 죽은 객체를 빠르게 회수하는 것보다도 중요하게 여기기 때문에 이렇게 구현 되었다.


## 5. G1GC로의 전환은 언제 수행하면 좋을까?
G1을 사용하지 않는 상태에서 Java 버전 업이나, 문제가 있을 때 G1으로 GC를 바꾸는 것을 고려할 수 있다! <br> 
CMS나 병렬 GC를 사용중인 상황에서 STW가 그리 길지 않으면 GC를 유지하는 것이 좋다고 한다. 꼭 최신 JDK로 바꾼다고 해서 GC도 바꿀 필요는 없다고 한다. <br>
CMS GC 또는 병렬 GC로 실행중인 Application은 아래와 같은 문제들 중 하나 이상이 발생하면 G1으로 변경하는 것이 좋다고 한다. 

1. Full GC가 너무 길거나, 빈번한 상황
2. 객체 할당 비율이나 promotion 비율이 크게 다르다?
3. 예상하지 못한 GC나 Compaction을 위한 Pauses 시간이 0.5 ~ 1초 이상인 경우

<br>

 
## Reference
- [Getting Started with the G1 Garbage Collector](https://www.oracle.com/webfolder/technetwork/tutorials/obe/java/G1GettingStarted/index.html)
- [일반적인 GC와 G1GC](https://thinkground.studio/2020/11/07/%EC%9D%BC%EB%B0%98%EC%A0%81%EC%9D%B8-gc-%EB%82%B4%EC%9A%A9%EA%B3%BC-g1gc-garbage-first-garbage-collector-%EB%82%B4%EC%9A%A9/)
- [기계인간 G1GC](https://johngrib.github.io/wiki/java/gc/g1gc/#gc-cycle)
