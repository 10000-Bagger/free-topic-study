# Spring Batch Scailing

1. Multi-threaded Step (Single process)
2. Remote Chunking (Multi process, Remote)
3. Spring Batch Partitioning
4. 비동기 Tasklet - AsyncItemProcessor, AsyncItemWriter
5. 분산 배치 서버 스케줄링


# 1. Multi-threaded Step (Single process)
일반적으로 Spring Batch는 단일 쓰레드에서 실행된다. 각 스텝은 순차적으로 실행된다. Chunk-oriented 방식으로 Chunk 단위로 나눠서 수행해도

1. Reader와 Processor는 한건식 작업을 수행한다.
2. 데이터가 너무 많이서 Chunk 단위로 나눠도 오래 걸릴 수 있다.

**이런 경우 Step을 Chunk 단위로 멀티 스레드에서 실행되게 하는 것을 고려할 수 있다.** <br>

선택해야 할 것은 아래와 같다.
1. Reader, Writer 구현체 선택
2. TaskExecutor 선택


## 1.1 Tasklet 구현체 선택
병렬 스레드로 step을 실행하도록 결정했다면, Reader, Writer 구현체를 선택하는 것이 중요하다. **구현체에 따라 Thread Safe한 것이 있고, 아닌 것이 있어서 Thread Safe하지 않은 Tasklet을 쓰려면 SynchronizedItemStreamReader와 같은 구현체로 래핑해서 사용해야 한다.** <br>  

알아내는 방법은 간단하다 클래스별로 javadoc 내용을 확인해본다. 예를 들어 JpaPagingItemReader의 javadoc 설명엔 "the implementation is thread-safe"라는 문구가 적혀 있다. <br> 

### 1.1.1 Thread Safe 하지 않은 구현체
Spring Batch 4.0부터 추가된 SynchronizedItemStreamReader로 Wrapping한다면 `CursorItemReader`와 같은 스레드 세이프 하지 않는 Reader도 간단하게 Thread Safe 하게 바꿀 수 있다. <br>
**단, Wrapping한 경우 Reader는 멀티스레드로 작동하지 않는다.** 대신 Processor와 Writer는 멀티 스레드로 동작한다. 일반적으로 배치 작업은 Write 에서 많은 시간을 사용하기 때문에 좋은 방법에 해당한다. <br>



## 1.2 TaskExecutor 선택
다양한 TaskExecutor를 활용해 쓰레드 풀의 스레드 갯수나 동작을 선택할 수 있다.
// TODO : [내가 쓴 글에서 옮기기](https://github.com/10000-Bagger/free-topic-study/blob/main/jin/%5BJava%5D%20ThreadPoolExecutor%EC%9D%98%20%EC%8A%A4%EB%A0%88%EB%93%9C%20%EA%B0%AF%EC%88%98%EB%8A%94%20%EC%96%B4%EB%96%BB%EA%B2%8C%20%EA%B4%80%EB%A6%AC%EB%90%98%EB%8A%94%EA%B0%80.md) 

<br>

## 1.3 주의
### 1. **실패 지점 재시작이 불가능하다.** 
원래의 Batch 작업은 순차적으로 실행되기 때문에, 단순히 몇번째 까지가 성공했는지만 저장해둔다면, 그 지점 부터 다시 시작하면 된다. **왜냐하면 Step이 순차적으로 실행되기 때문에, 알아서 앞의 시행들은 모두 성공했고, 현재 Chunk와 그 뒤의 Chunk 단위 수행들은 모두 다시 수행되야 함이 당연하기 때문이다.** <br>
하지만 멀티 스레드로 진행되는 경우 어디까지 성공했고, 어디까지 실패했는지 정확하게 파악하기가 어렵다. **따라서, 아예 처음 부터 시작되는 것이 좋은데,** 아예 처음 부터 시작할 수 있게 하기 위해 state를 저장하지 않는다. `.saveState(false)` 이 옵션을 false로 두어야 처음 부터 다시 시작할 수 있다. 

### 2. 모든 Batch 작업을 멀티 스레드로 해결하는 것이 답은 아니다.
서버 리소스 사용량을 확인하자. 단일 쓰레드인 상태에서도 리소스가 거의 남지 않았더라면, 멀티 스레드로 전환해도 마찬가지다. 그리고 당연히 리소스 자원을 많이 잡아먹기 때문에 다른 Job들에게 영향을 줄 수 밖에 없다.

### 3. 어떤 스레드가 어떤 데이터를 처리할지 세밀한 조정이 불가능하다.
추적을 하지 않기 때문.

### 4. 도입하기까지 고려 사항이 많다 // TODO : 더 알아보기
Reader와 Writer 구현체가 스레드 세이프를 제공하는가?

### 5. JobScope로 객체 사용시 하위 Worker 스레드에 데이터가 전달되지 않을 수도 있다. 
JobScope Bean을 JobParameter를 빈으로사용할 수도 있다. 그런데 JobScope로 객체 사용시 하위 Worker 스레드에 데이터가 전달되지 않을 수도 있다. **JobContext가 스레드 로컬에 저장되기 때문이다.** 그래서
1. JobScope Bean 대신 `@Value`를 직접 사용해 해결한다.
2. TaskExectuor에서 JobExecution을 하위 Worker 스레드에게 전달한다. 블로그에서 본 방법인데 이런 방법을 써도 되는게 맞나?


# 2. Remote Chunking (Multi process, Remote)
Step 처리를 여러 **프로세스로** 분할해 수행할 수 있음. 예를 들어 A 서버에서 Reader를 맡고, B 서버에서 Writer를 맡을 수도 있음. 어느 서버에서 어떤 구현체를 맡고 있는지 관리하지 않아 유실에 취약


# 3. Spring Batch Partitioning
**Spring batch Partition은 데이터를 더 작은 Chunk로 나눈 다음 파티션에 할당한다. 이렇게 나눈 각 파티션을 여러 슬레이브 Worker들이 독립적으로 작업을 수행한다.** <br>

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/27cc8759-095b-42d3-bd27-cc9848e134e2)


Master Step이 있고, 이 마스터 스텝이 다른 워커 스텝들을 관리한다. (로컬과 원격 모두 지원)


**각각의 파티션 - Worker Step은 독립적인 Step을 구성한다. 각자 ItemReader, ItemProcessor, ItemWriter를 가지고 동작하는 완벽한 하나의 스텝이다!** 그리고 별도의 StepExecution을 관리한다. <br> 
따라서 병렬스레드 처리를 적용할 때와는 달리 Reader나 Writer의 구현체가 Thread Safe를 지원하는지 중요하지 않다. 

## 3.1 선택해야 할 것들 
### 3.1.1 Partitioner 인터페이스
Partitioner 인터페이스를 구현해 파티셔닝 된 각 Worker Step을 위한 Step Executions를 생성해준다. 

### 3.1.2 PartionHandler 인터페이스
PartionHandler 인터페이스느 마스터 Step이 다른 Worker Step들을 어떻게 Handling  할지 정의합니다. 

1. 어느 Step을 Worker Step으로 쓸 것인가. (어떤 Step을 병렬로 수행하게 할 것인가)
2. 쓰레드 풀 관리는 어떻게 할 것인가
3. gridSize (TODO : 이게 뭐지??)

## 3.1.3 TaskExecutor
여기서도 TaskExecutor가 중요하다. 왜냐하면 구현체에 따라 스레드를 무한하게 생성해 사용할 수 있기 때문에, 대용량 데이터를 다루는 배치 작업에서는 스레드 갯수를 조절하는 적절한 ThreadExecutor를 사용하는 것이 중요하다. <br>

## 3.2 페이징 처리
파티션으로 나눈 하나의 Step은 완전한 Step이기 때문에 내부적인 pageSize를 설정할 수 있다.

## 3.3 RedisStreams
스프링 배치에서 기본적으로 제공해 주는 테이블 isolation level은 SERIALIZABLE이다. <br>
TODO : 보충

# 4. 비동기 Tasklet - AsyncItemProcessor, AsyncItemWriter
별개의 쓰레드를 통해 비동기적으로 처리한다. 구현체인 AsyncItemProcessor, AsyncItemWriter를 함께 사용해야 한다. 왜냐하면 AsyncItemProcessor는 Futrue를 반환하는데, 함께 사용하지 않으면 이 Future 객체를 직접 다뤄야 한다. 


# 5. 분산 배치 서버 스케줄링
