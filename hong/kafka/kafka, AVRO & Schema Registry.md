# Kafka, AVRO & Schema Registry

## Kafka

> 모든 시스템으로 데이터를 전송할 수 있고, 실시간 처리도 가능하며, 급속도로 성장하는 서비스를 위해 확장이 용이한 시스템을 만들자
> 
- kafka는 파이프라인, 스트리밍 분석, 데이터 통합 및 미션 크리티컬 애플리켜이션을 위해 설계된 고선등 분산 이벤트 스트리밍 플랫폼.
- Pub-Sub 모델의 메시지 큐 형태로 동작
- 분산 환경에서의 사용이 특화되어 있음.
- LinkedIn에서 개발
- 아래의 기존 데이터 시스템의 문제점을 해결하기 위해 개발됨.
    - 각 애플리케이션과 DB가 end-to-end로 연결되어 있고(각 파이프라인이 파편화되어 있음), 요구사항이 늘어남에 따라
    - 데이터 시스템 복잡도 증가.
        - 통합된 전송 영역이 없어 데이터 흐음 파악 어려움.
        - 특정 부분에서 장애 발생 시 조치 시간 증가(연결되어 있는 애플리케이션들을 모두 확인해야하기 때문에)
        - HW 교체 / SW 업그레이드 시 관리포인트가 늘어남(연결된 애플리케이션에 side effect가 없는지 확인해야 함.)
    - 데이터 파이프라인 관리의 어려움.
        - 각 애플리 케이션과 데이터 시스템 간의 별도의 파이프라인이 존재하고, 파이프라인 마다 데이터 포맷과 처리 방식이 다름.
        - 새로운 파이프라인 확장이 어려워지면서, 확장성 및 유연성이 떨어짐.
        - 데이터 불일치 가능성이 있어 신뢰도 감소.
- 모든 이벤트/데이터의 흐름을 중앙에서 관리하는 카프카를 개발.

### Kafka 동작 방식

- Message Queue (MQ)
    - MQ는 메시지 지향 미들웨어(MOM: Message Oriented Middleware)를 구현한 시스템으로 프로그램(프로세스) 간의 데이터를 교환할 때 사용하는 기술
    - producer: 정보를 제공
    - consumer: 정보를 제공받아서 사용
    - Queue: producer의 데이터를 임시 저장 및 consumer에 제공
- MQ 장점
    - 비동기: queue라는 임시 저장소가 있기 때문에 나중에 처리 가능
    - 낮은 결합도: 에플리케이션과 분리
    - 확장성: producer or consumer 서비스를 원하는대로 확장할 수 있음.
    - 탄력성: consumer 서비스가 다운되더라도 애플리케이션이 중단되는 것은 아니며 메시지는 지속하여 MQ에 남아있음.
    - 보장성: MQ에 들어간다면 결국 모든 메시지가 consumer 서비스에게 전달된다는 것을 보장.
- Message Broker / Event Broker
    - 메시지 브로커
        - publisher가 생성한 메시지를 MQ에 저장하고, 저장된 데이터를 consumer가 가져갈 수 있도록 중간 다리 역할을 해주는 broker.
        - 보통 서로 다른 시스템(소프트웨어) 사이에서 데이터를 비동기 형태로 처리하기 위해 사용됨 (대규모 엔터프라이즈 환경의 미들웨어로서의 기능)
        - 이러한 구조를 보통 pub/sub 구조라고 하며 대표적으로는 Redis, RabbitMQ 소프트웨어가 있고, GCP의 pubsub, AWS의 SQS 같은 서비스가 있음.
        - 이와 같은 메시지 브로커들은 consumer가 큐에서 데이터를 가져가게 되면 즉시 혹은 짧은 시간 내에 큐에서 데이터가 삭제되는 특징이 있음.
    - 이벤트 브로커
        - 이벤트 브로커 또한 기본적으로 메시지 브로커의 큐 기능들을 가지고 있어 메시지 브로커의 역할도 할 수 있음.
        - 메시지 브로커와의 가장 큰 차이점은, 이벤트 브로커는 publisher가 생성한 이벤트를 이벤트 처리 후 바로 삭제하지 않고 저장하여, 이벤트 시점이 저장되어 있어서 consumer가 특정 시점부터 이벤트를 다시 consume 할 수 있는 장점을 가지고 있음.
        - 또한 대용량 처리에 있어서는 메시지 브로커보다는 더 많은 양의 데이터를 처리할 수 있는 성능을 보여줌.
        - 이벤트 브로커에는 Kafka, AWS의 kinesis 같은 서비스가 있음.
- Event:
    - kafka에서 producer와 consumer가 데이터를 주고 받는 단위, 메시지
- Topic:
    - 이벤트가 모이는 곳. producer는 topic에 이벤트를 게시하고, consumer는 topic을 구독해야 이로부터 이벤트를 가져와 처리.
- Partition: topic은 여러 bocker에 분산되어 저장되며, 이렇게 분산된 topic을 partition이라고 함.
- Zookeeper: 분산 메시지의 큐의 정보를 관리

### 동작 원리

1. publisher는 전달하고자 하는 메시지를 topic을 통해 카테코리화함.
2. subscriber는 원하는 topic을 구독함으로써 메시지를 읽어옴.
3. publisher와 subscriber는 오로지 topic 정보만 알 뿐, 서로에 대해 알지 못함.
4. kafka는 broker들이 하나의 클러스터로 구성되어 동작하도록 설계.
5. 클러스터 내, broker에 대한 분산 처리는 zookeeper가 담당.

## AKHQ

- Apache Kafka HQ
- 카프카는 저장하는 데이터 리소스에 대한 blindness가 높아 운영 모니터링 툴이 필요.
- AKHQ는 카프카 운영 모니터링 툴.
- AKHQ는 오픈소스, micronaut 프레임워크를 기반으로 구성된 자바 웹 애플리케이션.

### AKHQ의 주요 기능

- 브로커 데이터 리소스에 대한 모니터링 및 운영
    - 브로커 노드 별 토픽 파티션 현황 조회
    - 토픽 리스트 조회
    - 토픽 생성 및 삭제
    - 토픽 파티션 리터 및 현황 및 디스크 사이즈 조회
    - 토픽 설정 조회 및 변경
    - 실시간 토픽 메시지 조회 및 검색
    - 웹 UI를 통한 토픽 메시지 발행
    - 토픽 별 ACL 조회
    - 컨슈머 그룹 목록 조회
    - 컨슈머 그룹 별 LAG 조회
- 카프카 플랫폼 연동
    - schema registry 연동
        - 스키마 조회 및 생성, 삭제, 수정
    - 하나 이상의 커넥터 클러스터 연동
        - 커넥터 목록 조회
        - 커넥터 생성, 수정, 삭제
        - 커넥터 일시 중지 및 재시작
    - 웹 UI 보안
        - Read Only mode
        - 사용자 그룹 정의
        - 정규식을 이용한 사용자 그룹 별 토픽 필터링
        - LDAP와 연동한 인증


## Redis

### Redis의 동작 방식 및 특징

- Redis는 데이터베이스, 캐시, 메시지 브로커 및 스트리밍 엔진으로 사용되는 인메모리 데이터 구조 저장소.
- 구성 요소:
    - publisher: 메시지를 게시(pub)
    - channel: 메시지를 쌓아두는 queue
    - subscriber: 메시지를 구독(sub)
- 동작:
    - publisher가 channel에 메시지 게시 → 해당 체널을 구독하고 있는 subscriber가 메시지를 sub해서 처리함.
- 특징:
    - channel은 이벤트를 저장하지 않음.
    - channel에 이벤트가 도착했을 때 해당 채널의 subscriber가 존재하지 않는다면 이벤트가 사라짐.
    - subscriber는 동시에 여러 channel을 구독할 수 있으며, 특정한 channel을 지정하지 않고 패턴을 설정하여 해당 패턴에 맞는 채널을 구독할 수 있음.
- 장점:
    - 처리 속도가 쁘름
    - 캐시의 역할도 가능
    - 명시적으로 데이터 삭제 가능
- 단점
    - 메모리 기반이므로 서버가 다운되면 Redis 내의 모든 데이터가 사라짐
    - 이벤트 도착 보장을 못함

## Arvo

- Apache에서 만든 프레임워크로 데이터 직렬화 기능을 제공.
- JSON과 비슷한 형식이지만, 스키마가 존재함.
- Arvo = schema + binary(json value)

장점

- 스키마를 통해 데이터 구조 및 타입을 알 수 있음
- 데이터 압축
- 스키마 변경에 유연하게 대응 가능
- json 대비 데이터 사이즈가 컴팩트함.
- 프로그래밍 언어에 상관없이 serialize/deserialize 가능 (java에서 serialize된 후 python에서 deserialize 가능)
- 다양한 데이터 타입을 지원.
- 스키마 변경을 유연하게 처리할 수 있음.

단점

- binary로 serialize되어서, 디버깅 등 상황에서 데이터 확인에 어려움이 있음.
- 스키마에 대한 관리가 필요 (관리 포인트 증가)

## Schema Registry

- kafka topic에 발행되는 schema 형식을 관리할 수 있도록 해주는 툴
- schema 버전별로도 등록하고 조회할 수 있음.

## Spring에서 사용

### publisher

- arvo schema 정의
- 정의된 arvo achema를 schema registry에 등록 (gradle script plugin을 사용하여 github action으로 CI에 넣을 수 있음)
- arvo schema로 java class 생성, message 발생 (serializer에 avro serializer 등록)
- avro만 별도 git repo에서 관리하기도 함.

### Consumer

- schema registry에서 avro schema를 다운로드 (gradle script plugin을 사용하여 빌드 시 다운로드 가능)
- avro schema로 java class 생성, message parsing
- [`com.github.imflog.kafka-schema-registry-gradle-plugin`](https://github.com/ImFlog/schema-registry-plugin)
    - schema registry에 avsc 파일을 등록/다운로드 가능하도록 만들어주는 gradle plugin ([링크](https://plugins.gradle.org/plugin/com.github.imflog.kafka-schema-registry-gradle-plugin))
    
    ```kotlin
    plugins {
      id("com.github.imflog.kafka-schema-registry-gradle-plugin") version "2.1.1"
    }
    ```
    
- application.yml에 schema registry url 정보 입력
    
    ```yaml
    spring:
      kafka:
        bootstrap-servers: localhost:9092
        consumer:
          group-id: spring-kafka
          auto-offset-reset: earliest
          keyDeserializer: org.apache.kafka.common.serialization.StringDeserializer
          valueDeserializer: io.confluent.kafka.serializers.KafkaAvroDeserializer
          properties:
            schema.registry.url: 'https://schema-registry.dev.yeah'
            auto.register.schemas: true
    ```
    
- KafkaListener를 사용해서 schema 타입 사용
    
    ```java
    public class ShipmentProcessor {
        @KafkaListener(topics = "shipment")
        public void process(ConsumerRecord<String, Shipment> record) {
            log.info("received a message. {}", record);
        }
    }
    ```
    

## References

- https://medium.com/@gaemi/kafka-와-confluent-schema-registry-를-사용한-스키마-관리-3-96b0f070d0f1
- https://geonyeongkim-development.tistory.com/74
