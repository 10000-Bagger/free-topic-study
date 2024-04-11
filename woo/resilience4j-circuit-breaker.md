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