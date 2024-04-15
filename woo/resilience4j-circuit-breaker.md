# Resilience4j - CircuitBreaker
## 소개
- CircuitBreaker는 FSM을 기반으로 구현 되었다.
- 상태에는 일반 상태 3가지와 특수 상태 2가지가 있다.
  - 일반 상태: CLOSED, OPEN, HALF_OPEN
  - 특수 상태: DISABLED, FORCED_OPEN
- CircuitBreaker가 호출 결과를 집계하고 저장할 때 2가지 선택지가 있다.
  - count based sliding window: 마지막 호출된 N번의 집계 
  - time based sliding window: 마지막 N초 동안의 호출 결과 집계

### count based sliding window
- N개의 측정 값을 지닌 원형 배열(크기 N)로 구현된다.
- 새 호출 결과가 기록되면 총 집계가 수정된다.
- 가장 오래된 측정 값이 제거될 때 총 집계에서 해당 값은 제거되며 bucket은 리셋된다.
- Snapshot 조회 시간 복잡도: O(1)
- 공간 복잡도: O(N)

### time based sliding window
- N개의 부분 집계(버킷)를 지닌 원형 배열로 구현되어 있다.
- 기준 시간이 N초라면, 원형 배열에는 항상 N개의 부분 집계(버킷)이 존재한다.
- 각 버킷은 epoch second 동안 일어난 모든 호출 결과를 집계한다.
- 원형 배열에서 head bucket은 현재 epoch second의 호출 결과를 담고 있다.
- 나머지 bucket은 부분 집계(bucket)에서는 지나간 시간들의 호출 결과들을 저장하고 있다.
- 호출 결과를 개별 저장하지 않고 부분 집계(bucket)와 총 집계를 조금씩 업데이트 해나간다.
- 총 집계는 새 호출 결과가 기록되면서 수정되고, 가장 오래된 부분 집계(bucket)가 제거되면 총 집계에서 이 기록이 제외된 후 부분 집계는 reset된다.
- 부분 집계는 실패 호출 / 느린 호출 / 총 호출 횟수를 카운팅하기 위한 3개의 Integer로 구성된다.
- 추가로 전체 호출에 소요한 시간을 저장하는 long 하나가 있다.
- Snapshot 조회 시간 복잡도: O(1)
- 공간 복잡도: O(N+1)

## 실패율(failure rate)과 지연 처리율(slow call rate)
- 실패율이 설정한 임계치보다 크거나 같을 때 CircuitBreaker 상태는 CLOSED -> OPEN으로 변한다.
  - 기본적으로 모든 예외는 실패로 간주된다.
  - 하지만 설정값을 통해 예외를 선택적으로 식별할 수 있다.
  - 단, 설정을 통해 무시된 예외는 실패 / 성공 둘 중 어느것도 아니다.
- 느린 호출 비율이 임계치보다 크거나 같을 때 CircuitBreaker 상태는 CLOSED -> OPEN으로 변한다.
- 실패율과 느린 호출 비율을 계산하려면 호출 결과의 최소치는 기록한 상태여아 한다.

## CircuitBreaker의 동작 과정
- CircuitBreaker가 OPEN 상태일 때는 CallNotPermittedException을 thorw하여 호출을 반려한다.
- 대기 시간만큼 경과하면 OPEN -> HALF_OPEN으로 상태를 변경하며, 설정한 횟수만큼 호출을 시도한다.
- 허용한 호출을 모두 완료할 때까지 나머지 요청들은 CallNotPermittedException로 반려된다.
- 지정한 횟수만큼의 요청이 성공하면 -> CLOSED, 실패 건이 있다면 -> OPEN이다.

### 특수 상태
- CircuitBreaker는 DISABLED(항상 접근 허용)와 FORCED_OPEN(항상 접근 거부) 상태를 지원한다.
- 이 두 상태에서는 CircuitBreaker 이벤트를 생성하지도, 메트릭을 기록하지도 않는다.
- 트리거나 CircuitBreaker가 리셋되어야 이 상태를 빠져나올 수 있다.

## Thread 안정성
- 아래 이유들로 CircuitBreaker는 thread-safe하다.
  - CircuitBreaker의 상태는 AtomicReference에 저장
  - CircuitBreaker는 원자적 연산과 사이드 이펙트 없는 함수를 통해 상태를 update한다.
  - sliding window에 호출 결과를 저장하고 스냅샷을 조회할 땐 동기화한다.
- 즉, sliding window update에 있어 동시성 문제는 해결되어 있다.
- 하지만 CircuitBreaker의 함수 호출이 동기화된 것은 아니고 sliding window 크기와 실행 가능 thread 수는 다른 의미이다.
  - CircuitBreaker의 함수이 동기화되어 있다면 엄청난 성능 저하를 야기했을 것이다.