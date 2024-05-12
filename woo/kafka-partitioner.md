# Kafka Clients 제공 Partitioner (kafka-clients 3.6.1v)
- kafka topic에는 partition이란 개념이 있다.
- producer는 각 message를 어떤 partition에 저장할지를 결정해야 하는데 이 책임을 가지고 있는 것이 Partitioner이다.

## Interface
```java
public interface Partitioner extends Configurable, Closeable {
    int partition(String topic, Object key, byte[] keyBytes, Object value, byte[] valueBytes, Cluster cluster)

    void close();

    /** @deprecated */
    @Deprecated
    default void onNewBatch(String topic, Cluster cluster, int prevPartition) {
    }
}
```
- kafka-clients 3.6.1 version 기준 Partitioner 인터페이스이다.
- partition(): topic, key 등의 정보를 바탕으로 해당 Message가 저장될 partition을 반환한는 메서드
- close(): 더이상 필요하지 않을 때 자원을 해제하기 위해 사용됨
- onNewbatch(): DefaultPartitioner and UniformStickyPartitioner에서 사용되었지만 현재는 Deprecated 상태이다. Partitioner에게 새로운 Batch가 생성 예정임을 알려 고정 파티션을 변경하는 기능이다.

## Implementations
- kafka-clients 3.6.1 기준으로 UniformStickyPartitioner, DefaultPartitioner는 @Deprecated된 상태이고 RoundRobinPartitioner만 유지될 예정이다.

### 1. RoundRobinPartitioner
```java
public class RoundRobinPartitioner implements Partitioner {
    private final ConcurrentMap<String, AtomicInteger> topicCounterMap = new ConcurrentHashMap();

    public RoundRobinPartitioner() {
    }

    public void configure(Map<String, ?> configs) {
    }

    public int partition(String topic, Object key, byte[] keyBytes, Object value, byte[] valueBytes, Cluster cluster) {
        List<PartitionInfo> partitions = cluster.partitionsForTopic(topic);
        int numPartitions = partitions.size();
        int nextValue = this.nextValue(topic);
        List<PartitionInfo> availablePartitions = cluster.availablePartitionsForTopic(topic);
        if (!availablePartitions.isEmpty()) {
            int part = Utils.toPositive(nextValue) % availablePartitions.size();
            return ((PartitionInfo)availablePartitions.get(part)).partition();
        } else {
            return Utils.toPositive(nextValue) % numPartitions;
        }
    }

    private int nextValue(String topic) {
        AtomicInteger counter = (AtomicInteger)this.topicCounterMap.computeIfAbsent(topic, (k) -> {
            return new AtomicInteger(0);
        });
        return counter.getAndIncrement();
    }

    public void close() {
    }
}
```
- 이름에서부터 동작 방식을 파악할 수 있듯이 RoundRobin방식으로 Message를 produce한다.
- 로직을 보면 topic별로 AtomicInteger를 하나씩 관리하고, 이 값을 기반으로 파티션을 정하게 된다.

### 2. BuiltInPartitioner
- 앞서 kafka-clients 3.6.1 version에서는 UniformStickyPartitioner, DefaultPartitioner가 @Deprecated된 것을 확인했다.
- 그렇다면 Partitioner를 지정하지 않았을 때는 어떤 Partitioner를 사용하게 될까?

#### Kafka Producer의 partition(...) 메서드
```java
private int partition(ProducerRecord<K, V> record, byte[] serializedKey, byte[] serializedValue, Cluster cluster) {
    if (record.partition() != null) {
        return record.partition();
    } else if (this.partitioner != null) {
        int customPartition = this.partitioner.partition(record.topic(), record.key(), serializedKey, record.value(), serializedValue, cluster);
        if (customPartition < 0) {
            throw new IllegalArgumentException(String.format("The partitioner generated an invalid partition number: %d. Partition number should always be non-negative.", customPartition));
        } else {
            return customPartition;
        }
    } else {
        return serializedKey != null && !this.partitionerIgnoreKeys ? BuiltInPartitioner.partitionForKey(serializedKey, cluster.partitionsForTopic(record.topic()).size()) : -1;
    }
}
```
- kafka producer는 위 메서드를 사용해서 message의 partition을 결정한다.
- 이때 record에 partition값이 이미 지정된 경우 혹은 partitioner가 지정된 경우가 아니라면 마지막 else 구문에 의해 반환값이 정해진다.
- 코드를 보면 key값이 없거나 key값을 무시하는 설정이 되어있다면 -1
- 그게 아니라면 BuiltInPartitioner의 partitionForKey(...)를 사용한다.

#### partition(...) 반환값이 -1이라면?
```java
if (partition == -1) {
    partitionInfo = topicInfo.builtInPartitioner.peekCurrentPartitionInfo(cluster);
    effectivePartition = partitionInfo.partition();
} else {
    partitionInfo = null;
    effectivePartition = partition;
}
```
- 위 로직은 KafkaProducer가 Message를 발행하는 로직. 정확히는 RecordAccumulator 클래스의 append(...) 메서드이다.
- partition()메서드의 반환값이 -1이면 첫번째 if문을 타게 된다.
- RecordAccumulator 내에는 topic에 대한 정보를 가진 TopicInfo들이 저장되어 있다.
- 각 TopicInfo는 내부에 BuiltInPartitioner를 가지고 있는데 BuiltInPartitioner가 target partition값인 StickyPartitionInfo를 가지고 있고 이 객체를 기반으로 partition을 할당 받는다.
- 전체적인 동작 방식을 보면 RoundRobin 방식과 유사하지만 Message 1개당 Partition을 순차적으로 바꾸지 않는다.
- 기본적으로 batch 1회 기준으로 RoundRobin이 적용되면 target partition으로 특정 양(내부 변수 stickyBatchSize)이상을 produce하기 전까지는 partition을 변경하지 않는다.

### BuiltInPartitioner.partitionForKey(...)
```java
public static int partitionForKey(byte[] serializedKey, int numPartitions) {
    return Utils.toPositive(Utils.murmur2(serializedKey)) % numPartitions;
}
```
- Key값이 있는 Message의 경우 BuiltInPartitioner.partitionForKey(...)를 사용해 partition을 정한다.
- 위 코드를 보면 알 수 있듯이 key 기반의 해싱값으로 partition을 할당한다.
- 즉, 동일 key를 가지는 Message는 동일 partition이 보장되는 것이다. 