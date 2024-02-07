작성일: 2/7/2024

# 파이프라이닝 설명과 장단점

### 키워드:
#### 병렬 프로그래밍

### 한 줄 요약:
#### 대용량 데이터 처리를 효율적으로 처리하기 위한 병렬 프로그래밍 기법.

## 설명
![Pipelining 기법을 설명하는 대표적인 예시](/hong/img/pipelined_architecture.png)
*Pipelining 기법을 설명하는 대표적인 예시*

위 그림과 같이 옷을 세탁할 때는 1) 세탁물 이동, 2) 세탁기 기동, 3) 건조기 기동, 4) 의류 정리의 과정을 거치게 된다. 이때 20kg의 옷을 최대 용량이 10kg인 세탁기와 건조기를 사용한다고 했을 때 어떤 방식이 가장 효율적일까?

### 단일 사이클인 경우
만약 건조 기능이 포함된 세탁기를 사용한다고 했을 때, 가장 먼저 세탁기의 최대 용량인 10kg의 세탁물이 세탁기에 들어갈 것이다. 세탁이 끝난 뒤 건조기로 들어가고, 건조가 완료되면 10kg의 옷을 정리한다. 정리가 끝나면 나머지 10kg에 대한 작업을 다시 한번 수행한다.

```
10kg 세탁물 이동 → 10kg 세탁 수행 → 10kg 건조 수행 → 10kg 의류 정리 → 1회차 완료 → 10kg 세탁물 이동 → 10kg 세탁 수행 → 10kg 건조 수행 → 10kg 의류 정리 → 2회차 완료
```

### 파이프라이닝(Pipelining) 방식
10kg 건조기를 따로 사용하여 병렬적으로 작업을 수행하면 어떻게 될까? 10kg 세탁 과정까지는 공통으로 수행된다. 세탁이 끝난 후 10kg의 옷이 건조기로 이동되는 동시에 10kg의 세탁물이 다시 세탁기로 이동되어 작업을 수행한다. 건조기가 건조 작업을 끝내기 전에 다음 10kg의 세탁 작업이 끝난다면, 건조기는 쉬지 않고 계속 돌게 된다. 이 과정을 정리해 보면 아래와 같다.

```
10kg 세탁물 이동 → 10kg 세탁 수행 → 10kg 건조 수행 → 10kg 의류 정리 → 1회차 완료

                 다음 10kg 세탁물 이동 → 10kg 세탁 수행 → 10kg 건조 수행 → 10kg 의류 정리 → 2회차 완료
```

프로세스별로 30분의 시간이 소요된다고 가정했을 때 건조 기능이 포함된 세탁기 운용 시 총 4시간이 걸리지만, 건조기를 병렬로 운용할 시 2시간 30분이 걸리게 된다. 이 차이는 세탁물의 양이 많아질수록 커지게 된다.

예를 들어, 세탁물 프로세스가 총 4번 수행될 경우 아래와 같은 효율을 얻을 수 있다.

- Number of processes: _N_=4
- Duration of each process: _D_=30 minutes
- Total runs: _R_=4
- Total duration in linear execution: _Tsequential_=*N*×*D*×*R*=480 minutes
- Total duration in pipelining: _Tpipeline_=_D_+(*N*−1)×*D*+(*R*−1)×*D=*210 minutes

Efficiency Calculation

```python
# Given values
N = 4  # Number of processes
D = 30  # Duration of each process in minutes
R = 4  # Total runs

# Linear execution time
T_linear = N * D * R

# Corrected calculation for pipelining execution time
T_pipeline = N * D + (R - 1) * D

# Efficiency calculation
efficiency = T_linear / T_pipeline

T_pipeline, efficiency

# Result: (210, 2.2857142857142856)
```

만약 건조기가 한 번에 처리할 수 있는 용량이 5kg이라면 어떨까? 회차별로 건조 기능이 총 2번 동작해야 하므로 세탁기가 생성한 세탁물이 건조되는 과정에서 병목현상이 발생하게 된다. 하지만 위 문제는 5kg 건조기를 한 대 더 운용함으로써 간단히 해결될 수 있다.

위 예시에서 세탁물은 data, 각 세탁 과정은 process, 세탁기와 건조기는 thread로 대입하여 생각한다면 파이프라이닝 방식을 쉽게 이해할 수 있다. 따라서 많은 데이터를 효율적으로 처리하기 위해서는 데이터를 병렬로 처리될 수 있는 프로세스로 구분한 뒤 프로세스 별로 필요한 자원을 할당하여 처리하는 방식이 적합하며, 이 것을 파이프라이닝(**Pipelining**)이라고 한다.

<!-- TODO: 장단점 설명 필요 -->
### 장점:

1. Fast Processing
2. Improved Resource Utilization
3. Flexibility
4. Lower Latency
5. Scalability

### 단점:

1. Pipeline Stalls
2. Increased Complexity
3. Higher Overhead
4. Difficulty of Parallelization
5. Limited Scaling


### 추후 커버할 주제: hazards, deadlock, mutex, Semaphore, event, barrier


### 참고 자료:
- Advantages and Disadvantages of Pipelining: https://aspiringyouths.com/advantages-disadvantages/pipelining/
