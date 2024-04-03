# kafka streams

## 스트림 프로세싱
- 이벤트 스트림에 데이터가 도착할 때마다 처리를 이어가는 Application
- kafka에서는 consumer를 떠올릴 수 있다.

## Stateless / Stateful
- Stateless: 이벤트 레코드가 도착했을 때 그 레코드만으로 처리가 완료되는 것
    - 이벤트를 받아 filtering 후 RDB에 적재와 같은 작업
- Stateful: 도착한 이벤트 레코드나 이를 기반으로 생성한 데이터를 저장해두고 조합하여 결과를 생성하는 것
    - 이벤트 기반 통계치와 같은 작업

## Stateful 애플리케이션의 State Store
- Stateful한 작업을 진행하기 위해서 현재까지 받아온 데이터를 저장하는 것은 필수적이다.
- 이벤트 발행 속도와 동시에 지속적인 처리를 위해서는 낮은 대기 시간이 중요하다.
- kafka streams나 flink는 RocksDB라는 localdb를 사용한다.
- 하지만 localdb에는 문제점이 있는데 kafka로 예를 들면 리밸런싱이 발생했을 때 기존 StateStore를 이용할 수 없기 때문이다.
- 때문에 리밸런싱과 같은 상황에서는 노드의 전환에 맞게 StateStore 재배치 메커니즘 또한 필수적이다.

## Kafka Streams
- 아파치 카프카에서 공식적으로 제공하는 스트림 프로세싱 프레임워크 with java
- stateful / stateless 작업 모두 이미 구현된 기능들을 통해 코드를 간략화 할 수 있다.
- [kafka streams 기본 개념](https://docs.confluent.io/platform/current/streams/concepts.html)
