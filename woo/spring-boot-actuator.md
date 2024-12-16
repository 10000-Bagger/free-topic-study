# spring-boot-actuator
## spring-boot-actuator란?
- actuator는 무언가를 움직이거나 제어하기 위한 기계 장치를 뜻하는 단어이다.
- spring-boot-actuator는 http endpoint나 jmx로 spring boot를 사용한 application의 모니터링 및 관리에 필요한 정보를 제공하는 기능


## Endpoints
### Default EndPoints
| endpoint         | 설명                                                                        |
|------------------|-------------------------------------------------------------------------------|
| auditevents      | 현재 애플리케이션의 감사 이벤트 정보를 노출한다. AuditEventRepository 빈이 필요하다.           |
| beans            | 애플리케이션의 모든 Spring 빈의 전체 목록을 표시한다.                                  |
| caches           | 사용 가능한 캐시를 노출한다.                                                       |
| conditions       | 구성 및 자동 구성 클래스에 대해 평가된 조건들과 그 이유를 보여준다.                         |
| configprops      | @ConfigurationProperties의 모든 목록을 요약하여 표시한다. 정제를 거칠 수 있다.             |
| env              | Spring의 ConfigurableEnvironment에서 속성을 노출한다. 정제를 거칠 수 있다.                |
| flyway           | 적용된 Flyway 데이터베이스 마이그레이션을 보여준다. 하나 이상의 Flyway 빈이 필요하다.       |
| health           | 애플리케이션 건강 정보를 보여준다.                                                     |
| httpexchanges    | HTTP 교환 정보를 표시한다(기본적으로 마지막 100개의 HTTP 요청-응답 교환). HttpExchangeRepository 빈이 필요하다. |
| info             | 임의의 애플리케이션 정보를 표시한다.                                                   |
| integrationgraph | Spring Integration 그래프를 보여준다. spring-integration-core에 대한 의존성이 필요하다.   |
| loggers          | 애플리케이션의 로거 설정을 표시하고 수정한다.                                               |
| liquibase        | 적용된 Liquibase 데이터베이스 마이그레이션을 보여준다. 하나 이상의 Liquibase 빈이 필요하다.  |
| metrics          | 현재 애플리케이션의 "메트릭" 정보를 보여준다.                                                |
| mappings         | @RequestMapping 경로의 모든 목록을 요약하여 표시한다.                                       |
| quartz           | Quartz 스케줄러 작업에 대한 정보를 보여준다. 정제를 거칠 수 있다.                              |
| scheduledtasks   | 애플리케이션의 예약된 작업을 표시한다.                                                     |
| sessions         | Spring Session 기반 세션 저장소에서 사용자 세션을 검색하고 삭제할 수 있다. Spring Session을 사용하는 서블릿 기반 웹 애플리케이션이 필요하다. |
| shutdown         | 애플리케이션을 우아하게 종료할 수 있다. jar 패키징을 사용할 때만 작동한다. 기본적으로 비활성화된다. |
| startup          | ApplicationStartup에 의해 수집된 시작 단계 데이터를 보여준다. SpringApplication이 BufferingApplicationStartup으로 설정되어 있어야 한다. |
| threaddump       | 스레드 덤프를 수행한다.                                                               |


### Optional EndPoints
| 엔드포인트  | 설명                                                                                                       |
|-----------|-----------------------------------------------------------------------------------------------------------|
| heapdump  | HotSpot JVM에서는 HPROF 형식으로, OpenJ9 JVM에서는 PHD 형식으로 힙 덤프 파일을 반환한다.                           |
| logfile   | 로그 파일 이름이나 경로가 설정되어 있으면 로그 파일 내용을 반환한다. HTTP Range 헤더를 사용해서 로그 파일의 일부만 가져올 수 있다. |
| prometheus| Prometheus 서버에서 사용할 수 있는 형식으로 메트릭 정보를 제공한다. 이 기능을 사용하기 위해서는 micrometer-registry-prometheus에 대한 의존성이 필요하다. |



##  Micrometer
- Micrometer는 JVM 기반 애플리케이션을 위한 메트릭 계측 라이브러리이다.
- 어떤 모니터링 툴을 사용하는지와 상관 없이 JVM 기반 애플리케이션을 계측할 수 있도록 Facade를 제공해준다.
  - 예를 들면 spring-boot-actuator로 수집된 데이터들을 micrometer-registry-prometheus가 prometheus라는 모니터링 툴이 수집이 가능한 형태로 데이터를 변환해주는 것
- 1.10버전 부터는 Metric뿐만 아니라 Tracing 기능을 추가할 수 있는 plugin도 제공한다고 함


### (1) Supported Monitoring System
#### registry란?
- Micrometer는 계측 Service Provider Interface를 포함한다.
- 이때 각 모니터링 시스템에 맞는 구현체를 registry라 한다.
- 즉, micrometer-registry-prometheus는 Prometheus용 Micrometer 계측 Service Provider Interface 구현체이다.
- 모니터링 시스템의 3가지 특징
  - Dimensionality
    - 모니터링 시스템이 메트릭 이름을 태그의 키/값 쌍으로 풍부하게 만들 수 있는지 여부
    - prometheus는 Dimensional 모니터링 시스템에 속한다.
    - ```
      From ChatGPT
      
      Dimensional System 예시
      차원적 시스템에서는 태그를 사용하여 메트릭에 다양한 차원을 추가할 수 있습니다. 예를 들어, 웹 애플리케이션의 HTTP 요청 처리 시간을 측정하는 메트릭을 생각해보겠습니다. 이 메트릭은 다음과 같은 태그를 포함할 수 있습니다:
        
      method: HTTP 메소드 (GET, POST, PUT, 등)
      endpoint: 요청받은 엔드포인트 (/api/user, /api/product, 등)
      status: HTTP 응답 상태 코드 (200, 404, 500, 등)
      이 태그들을 사용하여 같은 메트릭 이름 아래에서 여러 다른 차원의 데이터를 관찰하고, 특정 조건에 따른 세부적인 분석이 가능해집니다. 예를 들어, POST 메소드를 사용하는 /api/product 엔드포인트의 성공적인 요청(status 200)의 평균 처리 시간을 계산할 수 있습니다.
        
      Hierarchical System 예시
      계층적 시스템에서는 메트릭 이름이 모든 정보를 포함하고, 이름 자체가 구조화되어 있습니다. 같은 웹 애플리케이션의 HTTP 요청 처리 시간을 측정하는 경우를 예로 들면, 메트릭 이름을 다음과 같이 구성할 수 있습니다:
        
      GET_api_user_200
      POST_api_product_500
      이 경우, 각 메트릭 이름은 HTTP 메소드, 엔드포인트, 상태 코드를 하나의 문자열로 결합하여 표현합니다. 이 구조에서는 태그를 별도로 추가하지 않고, 메트릭 이름 자체가 필요한 모든 정보를 포함합니다. 메트릭 시스템이 이러한 구조적 이름을 분석하여 데이터를 저장하고 검색하는 방식은 계층적이라고 할 수 있습니다.
        
      이 두 가지 예를 통해 차원적 시스템이 태그를 사용하여 메트릭의 다양한 관점을 유연하게 탐색할 수 있게 해주는 반면, 계층적 시스템은 보다 고정적이고 구조화된 메트릭 이름을 사용하여 정보를 관리한다는 차이를 확인할 수 있습니다.
      ```
  - Rate Aggregation
    - 모니터링 데이터의 집계 방식으로 Server-side와 Client-side로 나뉜다.
    - prometheus는 Server-side에 속한다.
    - [Server-side, Client-side 설명](https://docs.micrometer.io/micrometer/reference/concepts/rate-aggregation.html)
  - Publishing
    - 모니터링 데이터를 모니터링 시스템에서 수집할 것인가, Client에서 모니터링 툴로 데이터를 보낼 것인가.
    - 당연히 prometheus는 전자.
    - 후자는 Influx 생각하면 됨. Datadog도 후자.