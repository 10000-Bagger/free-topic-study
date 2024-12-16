# JVM 성능 분석 및 모니터링 도구: jstat, jmap, jstack

## jstat

### 설명

- JVM 상태를 모니터링하는 도구.
- jstack, jmap과는 다르게 서비스에 영향을 주지 않기 때문에 서비스 중인 프로세스에도 사용할 수 있다.
- 프로세스가 실행 후 MinorGC, FullGC가 각각 몇번 발생했는지, heap, metaspace 공간에 대한 정보 등을 확인할 수 있다.
- `jstat -options` 명령어는 어떤 통계를 볼지 선택할 수 있는 인자 list를 볼 수 있다.

## jstack

### 설명

- 스레드 덤프 분석 도구.
- 스레드 전체 덤프를 출력한다.
- 애플리케이션이 느리게 동작한다거나, 데드락이 의심될 때 스레드 상태를 분석할 때 사용된다.
- JVM 내부에서 각 Thread 객체마다 `Thread.getAllStackTraces`, `Thread.dumpStack()`을 호출한 것과 동일하다.
- 시스템에 따라 Hang이 발생할 수 있다.
- `kill -3 PID` 명령어를 주면 어플리케이션의 스레드 덤프가 표준 출력에 출력된다. (`-l` 옵션을 주면 잠금 세부 사항도 확인할 수 있다.)

### Thread dump 생성 방법

- `jstack [PID]`
- 반드시 생성 시 3~5회 연속 생성하여 문제 상황에 대한 변화 과정을 확인.

### Thread dump 정보

- 스레드 이름, 우선순위, 스레드 아이디, 스레드 상태, 스레드 콜스택

### tid (Java-Level Thread ID)를 이용하여 정보 얻기

- ThreadMXBean을 이용하여 ThreadInfo 정보 획득 가능
- JMX 또는 REST API 등록으로 정보 획득을 가능하게 할 경우 문제 분석 용이
- tid와 threadId가 다른 경우도 존재하기 때문에 name으로 찾는 것이 좋음
- nid (Native Thread ID)를 이용하여 정보 얻기
    - Linux : ps -mo, ps - Elf 이용

### 트러블 슈팅

- CPU 사용 및 Load가 점차적으로 증가
    - 재시작 후 Thread dump를 주기적으로 생성 (thread leak)
- 요청이 증가하는 경우 장애가 발행하지는 않지만 응답시간이 느려지는 현상
    - Thread Dump 생성 후 TDA로 분석
    - 스레드 덤프 생성 후 BLOCKED 상태이거나 WAIT 상태가 많은 스레드가 있는지 확인.
    - Stack Trace 확인 (lock을 잡고 있는 것을 확인)
- 요청이 증가한 매우 간헐적으로 CPU가 100%로 폭증이후 요청량이 줄어들어도 CPU 사용량은 줄어들지 않고 재시작후 정상으로 돌아오는 현상.
    - CPU를 많이 사용하는 Thread 확인 -ps -mo 명령어를 통하여 CPU를 사용하는 lwp (Light Weight Process) 확인.
    - 16진수로 변경된 Thread Id를 이용하여 Thread Dump 검색.

** jstack 관련 내용은 추후 더 조사 필요.

## jmap

### 설명

- 현재 실행중인 프로세스의 JVM 메모리 맵을 보여주는 분석 도구.
- 힙 덤프를 발생시켜서 어떤 객체가 어떤 값을 가지고 있는지 저장한다.
- stop-the-world를 발생시키므로 서비스 중인 프로세스에는 반드시 필요한 상황에만 사용해야 한다.
- jmap 커맨드로 생성한 힙 덤프 파일은 이후 설명할 MAT에서 업로드해 분석할 수 있다.

```python
jmap -dump:format=b,file=heap.hprof 50690
```

- 콘솔에서 heap dump의 결과를 바로 출력하고자 한다면 아래 2가지 명령어를 사용할 수 있다.
    - jmap -histo 50690
        - FullGC가 일어나지 않음. GC가 일어나지 않기 때문에 GC 대상이 되는 객체들도 결과에 포함됨.
    - jmap -histo:live 50690
        - FullGC가 일어남. 서비스 중인 프로세스에는 신중하게 사용해야 함.
- 이때 클래스 이름 중에서 일반적이지 않은 이름들이 출력되는데 뜻은 아래와 같다.

```python
[C = char[]
[S = short[]
[I = int[]
[B = byte[]
[[I = int[][]
```

## jconsole, VisualVM

- java 모니터링 도구로서 기본적으로 제공해주는 툴: jconsole, VisualVM.
- VisualVM은 jconsole 보다 좀 더 많은 프로파일링 정보를 제공한다.

## Heap Memory 분석 도구: Eclipse Memory Analyzer (MAT)

- 오픈소스 메모리 분석 도구.
- Memory Leak 리포트나 생성된 객체, 차지하는 메모리들을 잘 보여주고 있어서 heap memory, memory leak 분석에 유용한 툴.
- Memory Leak이 의심되어서 프로세스를 검사해보고 싶다면, jmap 명령어로 Heap dump 파일을 추출하고 MAT 프로그램으로 분석한다.
- VisualVM으로 프로세스를 모니터링하면서 일정 시간동안 메모리가 어떻게 변하는지 보는 것도 좋지만 과거 데이터까지 보면서 각종 메트릭들의 변화 추이를 보고 싶다면 별도의 모니터링 시스템 구축 필요 (예: Prometheus)
- Heap Dump 파일 오픈 시에 파일이 너무 크면 MAT 프로그램이 out-of-memory을 발생할 수 있다. `Java heap space`
- 아래와 같이 프로그램 실행 시에 메모리를 좀 늘려서 실행해주면 해결된다.

```python
./MemoryAnalyzer -vmargs -Xmx5g -XX:-UseGCOverheadLimit
```
