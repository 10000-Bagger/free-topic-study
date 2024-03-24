# ConcurrentKafkaListenerContainerFactory.setConcurrency

## Kafka와 처리 순서 보장
- 기본적으로 Kafka Consumer는 메시지 처리의 순서를 보장할 수 없다.
- 만약 메시지 처리 순서를 보장하고 싶다면 파티션을 1개만 두어야 한다.
- Partition을 늘릴 경우 개별 Partition 내의 메시지 처리 순서는 보장할 수 있지만, 토픽 전체의 처리 순서는 보장할 수 없다.
- 즉, Kafka를 쓴다는 건 메시지의 처리 순서를 보장하지 않아도 되는 상황이라는 의미이다.

## Kafka와 동시 처리
- 순서가 보장되지 않아도 된다는 것은 동시 처리를 통해 성능상의 이점을 가질 수 있다는 의미이다.
- Kafka에서 Message 처리 성능을 높이기 위한 방식 중 대표적인 건 브로커의 Partition 수를 추가하고, 이에 맞게 Consumer 수를 늘리는 일이다.
- 위와 같이 설정하고 나면 개별 Partition에 쌓이는 Message양은 줄어들게 된다.
- 이와 동시에 Partition과 Consumer 수를 1:1로 맞추게 된다면 Consumer가 처리해야하는 Message 수는 줄어들게 된다.

## Consumer 수를 늘리는 방식
- 가장 간단하게는 Consumer Application이 동작하는 서버를 Scale Out하면 된다.
- 하지만 서버의 자원이 많이 남는다면 서버 수를 늘리기 이전에 ConcurrentKafkaListenerContainerFactory와 setConcurrency()메서드를 통해 서버를 늘리지 않고 Message 처리량을 늘릴 수 있다.

## AbstractKafkaListenerContainerFactory
- Spring은 AbstractKafkaListenerContainerFactory의 구현체로 KafkaMessageListenerContainer, ConcurrentKafkaListenerContainerFactory 2가지를 제공한다.
- ConcurrentKafkaListenerContainerFactory의 경우 setConcurrency() 메서드를 통해 Consumer를 처리하는 Thread 개수를 설정할 수 있다.

## ConcurrentKafkaListenerContainerFactory의 setConcurrency()의 역할 코드 타고 들어가보기
### 1. concurrency값은 무엇인가?
```java
public class ConcurrentKafkaListenerContainerFactory<K, V> extends AbstractKafkaListenerContainerFactory<ConcurrentMessageListenerContainer<K, V>, K, V> {
    private Integer concurrency;

    public ConcurrentKafkaListenerContainerFactory() {
    }

    public void setConcurrency(Integer concurrency) {
        this.concurrency = concurrency;
    }
    ...
}
```
- ConcurrentKafkaListenerContainerFactory는 기본적으로 @KafkaListener가 동록된 메서드 기반의 ConcurrentMessageListenerContainer를 생성하는 역할을 한다.
- 또한 내부적으로 concurrency 값을 가지고 있고 setConcurrency() 메서드를 사용해 concurrency값을 설정한다.
### 2. ConcurrentMessageListenerContainer 초기화
```java
protected void initializeContainer(ConcurrentMessageListenerContainer<K, V> instance, KafkaListenerEndpoint endpoint) {
    super.initializeContainer(instance, endpoint);
    Integer conc = endpoint.getConcurrency();
    if (conc != null) {
        instance.setConcurrency(conc);
    } else if (this.concurrency != null) {
        instance.setConcurrency(this.concurrency);
    }
}
```
- ConcurrentKafkaListenerContainerFactory의 initializeContainer 메서드를 통해 ConcurrentMessageListenerContainer의 초기값을 설정한다.
- 이때 기본 설정 로직은 부모 객체인 ConcurrentMessageListenerContainer의 initializeContainer()를 따라가지만 추가적으로 ConcurrentMessageListenerContainer에 concurrency값을 설정한다.
```java
public class ConcurrentMessageListenerContainer<K, V> extends AbstractMessageListenerContainer<K, V> {
    private final List<KafkaMessageListenerContainer<K, V>> containers = new ArrayList();
    private final List<AsyncTaskExecutor> executors = new ArrayList();
    private final AtomicInteger stoppedContainers = new AtomicInteger();
    private int concurrency = 1;
    private boolean alwaysClientIdSuffix = true;
    private volatile ConsumerStoppedEvent.Reason reason;
    ...
}
```
- ConcurrentMessageListenerContainer 내부에도 concurrency값이 존재하며 default는 1이고 ConcurrentKafkaListenerContainerFactory의 concurrency값에 맞춰서 초기화 된다.
- ConcurrentMessageListenerContainer는 이 값으로 무슨 일을 하는 걸까?

```java
protected void doStart() {
    if (!this.isRunning()) {
        this.checkTopics();
        ContainerProperties containerProperties = this.getContainerProperties();
        TopicPartitionOffset[] topicPartitions = containerProperties.getTopicPartitions();
        if (topicPartitions != null && this.concurrency > topicPartitions.length) {
            this.logger.warn(() -> {
                return "When specific partitions are provided, the concurrency must be less than or equal to the number of partitions; reduced from " + this.concurrency + " to " + topicPartitions.length;
            });
            this.concurrency = topicPartitions.length;
        }
    
        this.setRunning(true);
    
        for(int i = 0; i < this.concurrency; ++i) {
            KafkaMessageListenerContainer<K, V> container = this.constructContainer(containerProperties, topicPartitions, i);
            this.configureChildContainer(i, container);
            if (this.isPaused()) {
                container.pause();
            }
    
            container.start();
            this.containers.add(container);
        }
    }
}
```
- ConcurrentMessageListenerContainer의 doStart() 메서드이다.
- 로직을 살펴보면 ConcurrentMessageListenerContainer가 할당 받은 Partition을 조회하고 concurrency값이 Partition보다 클 경우 Partition 개수를 concurrency로 update한다.
- 다른 글을 통해 알게된 내용이지만 concurrency는 동시에 처리 가능한 Partition 개수를 뜻한다고 한다.
- 즉, concurrency가 3이면 3개의 Thread가 생성되어 3개의 Partition을 처리한다.
- 만약 Thread가 Partition 수보다 크다면 낭비되는 Thread가 생성되는 것이라 생각하면 이 로직이 이해가 된다.
- 이후 작업을 보면 concurrency 개수만큼의 KafkaMessageListenerContainer를 생성하고
- configureChildContainer 메서드 내에서 KafkaMessageListenerContainer에 개별 SimpleAsyncTaskExecutor를 등록한다.
- `즉, concurrency 수만큼의 KafkaMessageListenerContainer가 생기고 각 Container는 개별 Thread로 동작한다.`
- `서버 리소스를 확인해보고 여유가 있다면 concurrency 수를 늘리는 게 비용 측면에서 더 효율적이지 않을까 싶다`